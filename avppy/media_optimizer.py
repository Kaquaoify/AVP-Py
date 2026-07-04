from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import (
    DATA_DIR,
    LOG_DIR,
    RCLONE_SOURCE_DIR,
    RCLONE_SOURCE_READY_FILE,
    load_config,
)
from .media import (
    generate_thumbnail,
    is_video,
    ordered_media_files,
    remove_thumbnail,
    save_media_order,
)


LOGGER = logging.getLogger(__name__)

MAX_WIDTH = 2560
MAX_HEIGHT = 1440
MANIFEST_FILE = DATA_DIR / "media-optimization-manifest.json"
STATUS_FILE = DATA_DIR / "media-optimization-status.json"
MP4_AUDIO_COPY_CODECS = {"aac", "ac3", "alac", "eac3", "mp3"}


@dataclass(frozen=True)
class VideoInfo:
    width: int
    height: int
    video_codec: str
    audio_codec: str
    frame_rate: str

    @property
    def oversized(self) -> bool:
        return self.width > MAX_WIDTH or self.height > MAX_HEIGHT


@dataclass
class OptimizationSummary:
    checked: int = 0
    converted: list[Path] = field(default_factory=list)
    copied: int = 0
    deleted: int = 0
    failed: list[str] = field(default_factory=list)
    deferred: bool = False


def inspect_video(path: Path) -> VideoInfo | None:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        str(path),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        payload = json.loads(result.stdout)
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        LOGGER.error("Could not inspect video %s: %s", path, exc)
        return None

    streams = payload.get("streams", [])
    video = next(
        (
            item
            for item in streams
            if item.get("codec_type") == "video"
            and not item.get("disposition", {}).get("attached_pic")
        ),
        None,
    )
    if not video:
        return None
    audio = next((item for item in streams if item.get("codec_type") == "audio"), {})
    try:
        width = int(video.get("width") or 0)
        height = int(video.get("height") or 0)
    except (TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None

    return VideoInfo(
        width=width,
        height=height,
        video_codec=str(video.get("codec_name") or "").lower(),
        audio_codec=str(audio.get("codec_name") or "").lower(),
        frame_rate=str(video.get("avg_frame_rate") or video.get("r_frame_rate") or ""),
    )


def bootstrap_rclone_source(playback_root: Path) -> int:
    source_root = RCLONE_SOURCE_DIR.resolve()
    playback_root = playback_root.resolve()
    source_root.mkdir(parents=True, exist_ok=True)
    if source_root == playback_root or any(is_video(path) for path in source_root.rglob("*")):
        return 0

    copied = 0
    for source in ordered_media_files(playback_root):
        relative = source.relative_to(playback_root)
        destination = source_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, destination)
        except OSError:
            shutil.copy2(source, destination)
        copied += 1
    if copied:
        LOGGER.info("Bootstrapped rclone source cache with %s local media files", copied)
    return copied


class MediaOptimizer:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._pending_modes: set[str] = set()
        self._state_lock = threading.Lock()
        self._storage_lock = threading.Lock()
        self.thread: threading.Thread | None = None
        self.processing = False
        self.processing_mode = ""
        self.sync_active = False
        self.current_file = ""
        self.phase = ""
        self.maintenance_active = False
        self.playback_paused = False
        self.last_message = ""

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(
            target=self._run,
            name="avp-media-optimizer",
            daemon=True,
        )
        self.thread.start()

    def request(self, mode: str) -> str:
        normalized = "rclone" if mode == "rclone" else "manual"
        self.start()
        with self._condition:
            self._pending_modes.add(normalized)
            self._condition.notify_all()
        with self._state_lock:
            if not self.processing:
                self.last_message = "Traitement demandé."
        return (
            "Vérification et réencodage ajoutés à la file d'attente. "
            "La lecture sera suspendue automatiquement uniquement si un fichier doit être modifié."
        )

    def status(self) -> dict[str, Any]:
        with self._condition:
            pending = sorted(self._pending_modes)
        with self._state_lock:
            return {
                "processing": self.processing,
                "current_file": self.current_file,
                "phase": self.phase,
                "maintenance_active": self.maintenance_active,
                "playback_paused": self.playback_paused,
                "sync_active": self.sync_active,
                "pending_modes": pending,
                "last_message": self.last_message,
            }

    def set_sync_active(self, active: bool) -> None:
        with self._state_lock:
            self.sync_active = active

    def notice(self, media_root: str | Path) -> dict[str, Any]:
        root = Path(media_root).resolve()
        with self._storage_lock:
            payload = self._read_json(STATUS_FILE, {"optimized_files": []})
        names: list[str] = []
        for item in payload.get("optimized_files", []):
            try:
                path = Path(str(item["path"])).resolve()
            except (KeyError, OSError):
                continue
            if path == root or root not in path.parents or not path.exists():
                continue
            names.append(str(item.get("name") or path.name))
        names = sorted(set(names), key=str.lower)
        return {"count": len(names), "files": names}

    def rename_notice(self, root: Path, source: Path, destination: Path) -> None:
        with self._storage_lock:
            payload = self._read_json(STATUS_FILE, {"optimized_files": []})
            changed = False
            for item in payload.get("optimized_files", []):
                if str(item.get("path")) != str(source.resolve()):
                    continue
                item.update(self._notice_entry(root, destination))
                changed = True
            if changed:
                self._write_json(STATUS_FILE, payload)

    def remove_notice(self, path: Path) -> None:
        resolved = str(path.resolve())
        with self._storage_lock:
            payload = self._read_json(STATUS_FILE, {"optimized_files": []})
            files = [
                item
                for item in payload.get("optimized_files", [])
                if str(item.get("path")) != resolved
            ]
            if len(files) != len(payload.get("optimized_files", [])):
                self._write_json(STATUS_FILE, {"optimized_files": files})

    def optimize_manual(self, config: dict[str, Any]) -> OptimizationSummary:
        root = Path(config["local_media_dir"]).resolve()
        root.mkdir(parents=True, exist_ok=True)
        self._cleanup_stale_temps(root)
        summary = OptimizationSummary()
        ordered = ordered_media_files(root)
        updated_order: list[Path] = []

        for source in ordered:
            if self._should_pause():
                summary.deferred = True
                updated_order.extend(path for path in ordered if path not in updated_order)
                break

            info = inspect_video(source)
            summary.checked += 1
            if not info:
                summary.failed.append(f"{source.name}: analyse impossible")
                updated_order.append(source)
                continue
            if not info.oversized:
                updated_order.append(source)
                continue

            target = self._manual_target(source)
            self._begin_mutation()
            converted, deferred = self._transcode(source, target, info)
            if deferred:
                summary.deferred = True
                updated_order.append(source)
                updated_order.extend(path for path in ordered if path not in updated_order)
                break
            if not converted:
                summary.failed.append(f"{source.name}: réencodage impossible")
                updated_order.append(source)
                continue

            remove_thumbnail(source)
            if target != source and source.exists():
                source.unlink()
            generate_thumbnail(target, force=True)
            summary.converted.append(target)
            updated_order.append(target)

        save_media_order(root, self._deduplicate_paths(updated_order))
        if summary.converted:
            self._add_notice_files(root, summary.converted)
        return summary

    def optimize_rclone(self, config: dict[str, Any]) -> OptimizationSummary:
        source_root = RCLONE_SOURCE_DIR.resolve()
        playback_root = Path(config["local_media_dir"]).resolve()
        source_root.mkdir(parents=True, exist_ok=True)
        playback_root.mkdir(parents=True, exist_ok=True)
        self._cleanup_stale_temps(playback_root)
        if not RCLONE_SOURCE_READY_FILE.exists():
            bootstrap_rclone_source(playback_root)
        if source_root == playback_root:
            summary = OptimizationSummary()
            summary.failed.append("Le miroir rclone et le dossier de lecture doivent être séparés.")
            return summary

        summary = OptimizationSummary()
        manifest = self._read_json(MANIFEST_FILE, {"files": {}})
        previous_records = manifest.get("files", {})
        records: dict[str, dict[str, Any]] = {}
        expected_outputs: set[Path] = set()
        ordered_outputs: list[Path] = []
        source_files = ordered_media_files(source_root)
        reserved_outputs = {path.relative_to(source_root) for path in source_files}
        claimed_outputs: set[Path] = set()

        for source in source_files:
            if self._should_pause():
                summary.deferred = True
                break

            relative = source.relative_to(source_root)
            previous = previous_records.get(relative.as_posix(), {})
            info = inspect_video(source)
            summary.checked += 1
            if not info:
                summary.failed.append(f"{relative.as_posix()}: analyse impossible")
                previous_output = previous.get("output")
                if previous_output:
                    previous_target = playback_root / str(previous_output)
                    if previous_target.exists():
                        expected_outputs.add(previous_target.resolve())
                        ordered_outputs.append(previous_target)
                        records[relative.as_posix()] = previous
                continue

            output_relative = self._rclone_output_relative(
                relative,
                info.oversized,
                reserved_outputs,
                claimed_outputs,
            )
            target = playback_root / output_relative
            expected_outputs.add(target.resolve())
            ordered_outputs.append(target)
            fingerprint = self._fingerprint(source)
            unchanged = (
                previous.get("fingerprint") == fingerprint
                and previous.get("output") == output_relative.as_posix()
                and target.exists()
            )

            if unchanged:
                records[relative.as_posix()] = previous
                continue

            self._begin_mutation()
            if info.oversized:
                converted, deferred = self._transcode(source, target, info)
                if deferred:
                    summary.deferred = True
                    break
                if not converted:
                    summary.failed.append(f"{relative.as_posix()}: réencodage impossible")
                    if target.exists():
                        records[relative.as_posix()] = previous
                    continue
                summary.converted.append(target)
            else:
                self._set_progress("Mise à jour de la bibliothèque", source.name)
                if not self._materialize_source(source, target):
                    self._set_progress("Vérification des médias", "")
                    summary.failed.append(f"{relative.as_posix()}: copie impossible")
                    continue
                summary.copied += 1

            generate_thumbnail(target, force=True)
            records[relative.as_posix()] = {
                "fingerprint": fingerprint,
                "output": output_relative.as_posix(),
                "optimized": info.oversized,
                "source_codec": info.video_codec,
            }
            self._set_progress("Vérification des médias", "")

        if not summary.deferred and self._should_pause():
            summary.deferred = True

        if not summary.deferred:
            stale_files = [
                path
                for path in ordered_media_files(playback_root)
                if path.resolve() not in expected_outputs
            ]
            if stale_files:
                self._begin_mutation()
                self._set_progress("Mise à jour de la bibliothèque", "")
            for path in stale_files:
                remove_thumbnail(path)
                path.unlink()
                summary.deleted += 1
            save_media_order(
                playback_root,
                [path for path in ordered_outputs if path.exists()],
            )
            self._write_json(MANIFEST_FILE, {"files": records})
            optimized = [
                playback_root / record["output"]
                for record in records.values()
                if record.get("optimized") and (playback_root / record["output"]).exists()
            ]
            self._replace_notice_files(playback_root, optimized)
        else:
            partial_records = dict(previous_records)
            partial_records.update(records)
            self._write_json(MANIFEST_FILE, {"files": partial_records})
            if summary.converted:
                self._add_notice_files(playback_root, summary.converted)

        return summary

    def _run(self) -> None:
        while True:
            with self._condition:
                while not self._pending_modes:
                    self._condition.wait()
                mode = sorted(self._pending_modes)[0]
                self._pending_modes.remove(mode)

            if self._should_pause():
                with self._condition:
                    self._pending_modes.add(mode)
                time.sleep(10)
                continue

            config = load_config()
            if config.get("media_source", "rclone") != mode:
                with self._state_lock:
                    self.last_message = (
                        f"Optimisation {mode} annulée : la source de médias active a changé."
                    )
                continue
            with self._state_lock:
                self.processing = True
                self.processing_mode = mode
                self.current_file = ""
                self.phase = "Vérification des médias"
                self.maintenance_active = False
                self.playback_paused = False
                self.last_message = ""
            try:
                summary = (
                    self.optimize_rclone(config)
                    if mode == "rclone"
                    else self.optimize_manual(config)
                )
                message = self._summary_message(mode, summary)
                LOGGER.info(message)
                with self._state_lock:
                    self.last_message = message
                if summary.deferred:
                    with self._condition:
                        self._pending_modes.add(mode)
                    time.sleep(10)
            except Exception:
                LOGGER.exception("Media optimization failed mode=%s", mode)
                with self._state_lock:
                    self.last_message = "Le traitement des médias a échoué. Consulte les logs."
            finally:
                self._end_mutation()
                with self._state_lock:
                    self.processing = False
                    self.processing_mode = ""
                    self.current_file = ""
                    self.phase = ""

    def _should_pause(self) -> bool:
        with self._state_lock:
            mode = self.processing_mode
            sync_active = self.sync_active
        if sync_active:
            return True
        if not mode:
            return False
        try:
            return load_config().get("media_source", "rclone") != mode
        except (OSError, ValueError, json.JSONDecodeError):
            return False

    def _transcode(self, source: Path, target: Path, info: VideoInfo) -> tuple[bool, bool]:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.parent / f".{target.stem}-{uuid4().hex}.avptmp"
        encoder = "libx264" if info.video_codec == "h264" else "libx265"
        command = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-map",
            "0:V:0",
            "-map",
            "0:a:0?",
            "-map_metadata",
            "0",
            "-vf",
            (
                f"scale={MAX_WIDTH}:{MAX_HEIGHT}:"
                "force_original_aspect_ratio=decrease:force_divisible_by=2"
            ),
            "-c:v",
            encoder,
        ]
        if encoder == "libx264":
            command.extend(["-preset", "ultrafast", "-crf", "23"])
        else:
            command.extend(["-preset", "ultrafast", "-crf", "28", "-tag:v", "hvc1"])
        if info.audio_codec:
            if info.audio_codec in MP4_AUDIO_COPY_CODECS:
                command.extend(["-c:a", "copy"])
            else:
                command.extend(["-c:a", "aac", "-b:a", "192k"])
        command.extend(
            [
                "-fps_mode",
                "passthrough",
                "-sn",
                "-dn",
                "-movflags",
                "+faststart",
                "-f",
                "mp4",
                str(temporary),
            ]
        )
        if os.name != "nt" and shutil.which("nice"):
            command = ["nice", "-n", "19", *command]

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._set_progress("Réencodage en cours", source.name)
        LOGGER.info(
            "Transcoding %s from %sx%s codec=%s to max %sx%s codec=%s",
            source,
            info.width,
            info.height,
            info.video_codec,
            MAX_WIDTH,
            MAX_HEIGHT,
            encoder,
        )
        try:
            with (LOG_DIR / "media-optimizer.log").open("a", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=log_file,
                    text=True,
                )
                while process.poll() is None:
                    if self._should_pause():
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        temporary.unlink(missing_ok=True)
                        return False, True
                    time.sleep(2)
        except FileNotFoundError:
            LOGGER.error("ffmpeg or nice is unavailable")
            return False, False
        finally:
            self._set_progress("Vérification des médias", "")

        if process.returncode != 0 or not temporary.exists():
            LOGGER.error("Transcoding failed for %s with code %s", source, process.returncode)
            temporary.unlink(missing_ok=True)
            return False, False

        remove_thumbnail(target)
        temporary.replace(target)
        return True, False

    def _begin_mutation(self) -> None:
        with self._state_lock:
            if self.maintenance_active:
                return
        from .scheduler import scheduler

        was_playing = scheduler.begin_media_maintenance()
        with self._state_lock:
            self.maintenance_active = True
            self.playback_paused = was_playing

    def _end_mutation(self) -> None:
        with self._state_lock:
            if not self.maintenance_active:
                return
            resume_playback = self.playback_paused
        from .scheduler import scheduler

        try:
            scheduler.end_media_maintenance(resume_playback)
        except Exception:
            LOGGER.exception("Could not restore playback after media maintenance")
        finally:
            with self._state_lock:
                self.maintenance_active = False
                self.playback_paused = False

    def _set_progress(self, phase: str, current_file: str) -> None:
        with self._state_lock:
            self.phase = phase
            self.current_file = current_file

    @staticmethod
    def _manual_target(source: Path) -> Path:
        if source.suffix.lower() == ".mp4":
            return source
        candidate = source.with_suffix(".mp4")
        counter = 2
        while candidate.exists():
            candidate = source.with_name(f"{source.stem} ({counter}).mp4")
            counter += 1
        return candidate

    @staticmethod
    def _rclone_output_relative(
        relative: Path,
        optimized: bool,
        reserved: set[Path],
        claimed: set[Path],
    ) -> Path:
        if not optimized or relative.suffix.lower() == ".mp4":
            candidate = relative
        else:
            candidate = relative.with_suffix(".mp4")
        if candidate in claimed or (candidate != relative and candidate in reserved):
            digest = hashlib.sha1(relative.as_posix().encode("utf-8")).hexdigest()[:8]
            candidate = relative.with_name(f"{relative.stem}.avp-{digest}.mp4")
        claimed.add(candidate)
        return candidate

    @staticmethod
    def _materialize_source(source: Path, target: Path) -> bool:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.parent / f".{target.name}-{uuid4().hex}.tmp"
        try:
            try:
                os.link(source, temporary)
            except OSError:
                shutil.copy2(source, temporary)
            remove_thumbnail(target)
            temporary.replace(target)
            return True
        except OSError:
            LOGGER.exception("Could not materialize media %s to %s", source, target)
            temporary.unlink(missing_ok=True)
            return False

    @staticmethod
    def _fingerprint(path: Path) -> str:
        stat = path.stat()
        return f"{stat.st_size}:{stat.st_mtime_ns}:{stat.st_ino}"

    @staticmethod
    def _cleanup_stale_temps(root: Path) -> None:
        for path in root.rglob("*.avptmp"):
            try:
                path.unlink()
            except OSError:
                LOGGER.warning("Could not remove stale optimization file %s", path)

    @staticmethod
    def _deduplicate_paths(paths: list[Path]) -> list[Path]:
        seen: set[Path] = set()
        result: list[Path] = []
        for path in paths:
            resolved = path.resolve()
            if resolved in seen or not path.exists():
                continue
            seen.add(resolved)
            result.append(path)
        return result

    def _add_notice_files(self, root: Path, paths: list[Path]) -> None:
        with self._storage_lock:
            payload = self._read_json(STATUS_FILE, {"optimized_files": []})
            existing = {
                str(item.get("path")): item
                for item in payload.get("optimized_files", [])
                if Path(str(item.get("path") or "")).exists()
            }
            for path in paths:
                existing[str(path.resolve())] = self._notice_entry(root, path)
            self._write_json(STATUS_FILE, {"optimized_files": list(existing.values())})

    def _replace_notice_files(self, root: Path, paths: list[Path]) -> None:
        with self._storage_lock:
            payload = self._read_json(STATUS_FILE, {"optimized_files": []})
            kept: list[dict[str, Any]] = []
            resolved_root = root.resolve()
            for item in payload.get("optimized_files", []):
                path = Path(str(item.get("path") or "")).resolve()
                if path != resolved_root and resolved_root not in path.parents and path.exists():
                    kept.append(item)
            kept.extend(self._notice_entry(root, path) for path in paths)
            self._write_json(STATUS_FILE, {"optimized_files": kept})

    @staticmethod
    def _notice_entry(root: Path, path: Path) -> dict[str, str]:
        return {
            "path": str(path.resolve()),
            "name": path.resolve().relative_to(root.resolve()).as_posix(),
            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }

    @staticmethod
    def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError, TypeError):
            return default

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)

    @staticmethod
    def _summary_message(mode: str, summary: OptimizationSummary) -> str:
        return (
            f"Optimisation {mode} terminée : {summary.checked} vérifié(s), "
            f"{len(summary.converted)} réencodé(s), {summary.copied} copié(s), "
            f"{summary.deleted} supprimé(s), {len(summary.failed)} échec(s)"
            + (", traitement reporté car une lecture a démarré" if summary.deferred else "")
        )


media_optimizer = MediaOptimizer()

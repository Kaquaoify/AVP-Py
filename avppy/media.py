from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from .config import DATA_DIR, THUMB_DIR

LOGGER = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mpg", ".mpeg"}
MEDIA_ORDER_FILE = DATA_DIR / "media-order.json"


def is_video(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def probe_media(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=True)
        payload = json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError) as exc:
        LOGGER.warning("ffprobe failed for %s: %s", path, exc)
        return {}

    streams = payload.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    fmt = payload.get("format", {})
    width = video_stream.get("width")
    height = video_stream.get("height")
    duration = float(fmt.get("duration") or video_stream.get("duration") or 0)

    return {
        "duration": round(duration, 1),
        "codec": video_stream.get("codec_name", ""),
        "format": fmt.get("format_long_name") or fmt.get("format_name", ""),
        "resolution": f"{width}x{height}" if width and height else "",
        "container": path.suffix.lower().lstrip("."),
    }


def thumbnail_name(path: Path) -> str:
    digest = hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()
    return f"{digest}.jpg"


def generate_thumbnail(path: Path, force: bool = False) -> str:
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    name = thumbnail_name(path)
    output = THUMB_DIR / name
    if output.exists() and not force:
        return name

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        "00:00:01",
        "-i",
        str(path),
        "-frames:v",
        "1",
        "-vf",
        "scale=320:-1",
        str(output),
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, timeout=30, check=True)
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        LOGGER.warning("ffmpeg thumbnail failed for %s: %s", path, exc)
        return ""
    return name


def remove_thumbnail(path: Path) -> None:
    thumbnail = THUMB_DIR / thumbnail_name(path)
    if thumbnail.exists():
        thumbnail.unlink()


def ordered_media_files(media_dir: str | Path) -> list[Path]:
    root = Path(media_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    files = [path for path in root.rglob("*") if is_video(path)]
    by_relative = {path.relative_to(root).as_posix(): path for path in files}

    configured_order: list[str] = []
    if MEDIA_ORDER_FILE.exists():
        try:
            payload = json.loads(MEDIA_ORDER_FILE.read_text(encoding="utf-8"))
            if payload.get("media_dir") == str(root) and isinstance(payload.get("files"), list):
                configured_order = [str(item) for item in payload["files"]]
        except (json.JSONDecodeError, OSError, AttributeError):
            LOGGER.warning("Could not read media order from %s", MEDIA_ORDER_FILE)

    ordered = [
        by_relative.pop(relative) for relative in configured_order if relative in by_relative
    ]
    ordered.extend(sorted(by_relative.values(), key=lambda path: path.name.lower()))
    return ordered


def save_media_order(media_dir: str | Path, files: list[Path]) -> None:
    root = Path(media_dir).resolve()
    payload = {
        "media_dir": str(root),
        "files": [path.resolve().relative_to(root).as_posix() for path in files],
    }
    MEDIA_ORDER_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEDIA_ORDER_FILE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def resolve_media_path(media_dir: str | Path, relative_path: str) -> Path:
    root = Path(media_dir).resolve()
    candidate = (root / relative_path).resolve()
    if candidate == root or root not in candidate.parents:
        raise ValueError("Chemin de média invalide.")
    return candidate


def move_media(media_dir: str | Path, relative_path: str, direction: str) -> bool:
    root = Path(media_dir).resolve()
    target = resolve_media_path(root, relative_path)
    files = ordered_media_files(root)
    try:
        index = files.index(target)
    except ValueError:
        return False

    new_index = index - 1 if direction == "up" else index + 1
    if new_index < 0 or new_index >= len(files):
        return False
    files[index], files[new_index] = files[new_index], files[index]
    save_media_order(root, files)
    return True


def scan_media(media_dir: str | Path, regenerate_thumbnails: bool = False) -> list[dict[str, Any]]:
    root = Path(media_dir)
    root.mkdir(parents=True, exist_ok=True)
    files = ordered_media_files(root)
    items: list[dict[str, Any]] = []

    for index, path in enumerate(files, start=1):
        metadata = probe_media(path)
        thumb = generate_thumbnail(path, force=regenerate_thumbnails)
        items.append(
            {
                "index": index,
                "filename": path.name,
                "relative_path": path.resolve().relative_to(root.resolve()).as_posix(),
                "title": path.stem,
                "path": str(path),
                "thumbnail": thumb,
                **metadata,
            }
        )
    return items


def write_playlist(media_dir: str | Path, playlist_path: Path) -> int:
    files = ordered_media_files(media_dir)
    playlist_path.parent.mkdir(parents=True, exist_ok=True)
    playlist_path.write_text("\n".join(str(path) for path in files) + "\n", encoding="utf-8")
    return len(files)

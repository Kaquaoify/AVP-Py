from __future__ import annotations

import json
import logging
import os
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import DATA_DIR
from .media import write_playlist

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlaybackResult:
    media_count: int
    started: bool


class PlayerController:
    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.ipc_path = DATA_DIR / "mpv.sock"
        self.playlist_path = DATA_DIR / "playlist.m3u"
        self.playlist_loaded = False

    def status(self) -> dict[str, Any]:
        running = self.is_running()
        current_path = self.get_property("path") if running else None
        return {
            "running": running,
            "playlist_loaded": running and self.playlist_loaded,
            "ipc": str(self.ipc_path),
            "current_media": Path(str(current_path)).name if current_path else "",
        }

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def is_playlist_active(self) -> bool:
        return self.is_running() and self.ipc_path.exists() and self.playlist_loaded

    def ensure_idle(self, config: dict[str, Any]) -> bool:
        if os.name == "nt":
            return False
        if self.is_running():
            return self.ipc_path.exists() or self._wait_for_ipc()

        self.playlist_loaded = False
        if self.ipc_path.exists():
            self.ipc_path.unlink()

        mpv_log_path = DATA_DIR / "logs" / "mpv.log"
        mpv_log_path.parent.mkdir(parents=True, exist_ok=True)
        args = [
            "mpv",
            "--idle=yes",
            "--force-window=yes",
            "--fs",
            "--no-terminal",
            "--really-quiet",
            "--osc=no",
            "--osd-level=0",
            "--cursor-autohide=always",
            f"--input-ipc-server={self.ipc_path}",
            "--background=color",
            "--background-color=#000000",
            f"--log-file={mpv_log_path}",
        ]
        extra_args = (config.get("mpv_extra_args") or "").split()
        args.extend(extra_args)

        LOGGER.info("Starting mpv idle screen")
        with mpv_log_path.open("a", encoding="utf-8") as mpv_log:
            self.process = subprocess.Popen(
                args,
                stdout=mpv_log,
                stderr=subprocess.STDOUT,
                text=True,
            )
        if not self._wait_for_ipc():
            return False
        self.set_volume(int(config.get("volume", 70)))
        return True

    def play_playlist(self, media_dir: str | Path, config: dict[str, Any]) -> PlaybackResult:
        count = write_playlist(media_dir, self.playlist_path)
        if count == 0:
            self.stop_to_black()
            return PlaybackResult(0, False)
        if not self.ensure_idle(config):
            LOGGER.warning(
                "Playback deferred: mpv is unavailable; %s media files remain queued",
                count,
            )
            return PlaybackResult(count, False)
        if not self.command(["loadlist", str(self.playlist_path), "replace"]):
            self.playlist_loaded = False
            LOGGER.warning(
                "Playback deferred: playlist could not be sent to mpv; "
                "%s media files remain queued",
                count,
            )
            return PlaybackResult(count, False)

        self.playlist_loaded = True
        self.command(["set_property", "loop-playlist", "inf"])
        self.command(["set_property", "pause", False])
        self.set_volume(int(config.get("volume", 70)))
        return PlaybackResult(count, True)

    def stop_to_black(self) -> None:
        self.playlist_loaded = False
        self.command(["stop"])

    def pause_to_black(self) -> None:
        self.stop_to_black()

    def next(self) -> None:
        self.command(["playlist-next", "force"])

    def previous(self) -> None:
        self.command(["playlist-prev", "force"])

    def set_volume(self, volume: int) -> None:
        volume = max(0, min(100, volume))
        self.command(["set_property", "volume", volume])

    def command(self, command: list[Any]) -> bool:
        if os.name == "nt":
            LOGGER.info("mpv command skipped on Windows: %s", command)
            return False
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(str(self.ipc_path))
                sock.sendall((json.dumps({"command": command}) + "\n").encode("utf-8"))
            return True
        except OSError as exc:
            LOGGER.warning("mpv IPC command failed %s: %s", command, exc)
            return False

    def get_property(self, name: str) -> Any | None:
        if os.name == "nt":
            return None
        request_id = 1
        payload = {
            "command": ["get_property", name],
            "request_id": request_id,
        }
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect(str(self.ipc_path))
                sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
                with sock.makefile("r", encoding="utf-8") as response:
                    for _ in range(10):
                        line = response.readline()
                        if not line:
                            break
                        message = json.loads(line)
                        if message.get("request_id") == request_id:
                            if message.get("error") == "success":
                                return message.get("data")
                            return None
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.debug("mpv property query failed %s: %s", name, exc)
        return None

    def _wait_for_ipc(self) -> bool:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.ipc_path.exists():
                return True
            if self.process is not None and self.process.poll() is not None:
                LOGGER.error(
                    "mpv exited before creating its IPC socket (code %s); see %s",
                    self.process.returncode,
                    DATA_DIR / "logs" / "mpv.log",
                )
                return False
            time.sleep(0.1)
        LOGGER.warning("mpv IPC socket did not appear: %s", self.ipc_path)
        return False


player = PlayerController()

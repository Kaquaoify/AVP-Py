from __future__ import annotations

import json
import logging
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Any

from .config import DATA_DIR
from .media import write_playlist

LOGGER = logging.getLogger(__name__)


class PlayerController:
    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.ipc_path = DATA_DIR / "mpv.sock"
        self.playlist_path = DATA_DIR / "playlist.m3u"

    def status(self) -> dict[str, Any]:
        return {
            "running": self.process is not None and self.process.poll() is None,
            "ipc": str(self.ipc_path),
        }

    def ensure_idle(self, config: dict[str, Any]) -> None:
        if os.name == "nt":
            return
        if self.process is not None and self.process.poll() is None:
            return

        if self.ipc_path.exists():
            self.ipc_path.unlink()

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
            "--background=black",
        ]
        extra_args = (config.get("mpv_extra_args") or "").split()
        args.extend(extra_args)

        LOGGER.info("Starting mpv idle screen")
        mpv_log_path = DATA_DIR / "logs" / "mpv.log"
        mpv_log_path.parent.mkdir(parents=True, exist_ok=True)
        with mpv_log_path.open("a", encoding="utf-8") as mpv_log:
            self.process = subprocess.Popen(
                args,
                stdout=mpv_log,
                stderr=subprocess.STDOUT,
                text=True,
            )
        self._wait_for_ipc()
        self.set_volume(int(config.get("volume", 70)))

    def play_playlist(self, media_dir: str | Path, config: dict[str, Any]) -> int:
        count = write_playlist(media_dir, self.playlist_path)
        self.ensure_idle(config)
        if count == 0:
            self.stop_to_black()
            return 0
        self.command(["loadlist", str(self.playlist_path), "replace"])
        self.command(["set_property", "loop-playlist", "inf"])
        self.command(["set_property", "pause", False])
        self.set_volume(int(config.get("volume", 70)))
        return count

    def stop_to_black(self) -> None:
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

    def _wait_for_ipc(self) -> None:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.ipc_path.exists():
                return
            if self.process is not None and self.process.poll() is not None:
                LOGGER.error(
                    "mpv exited before creating its IPC socket (code %s); see %s",
                    self.process.returncode,
                    DATA_DIR / "logs" / "mpv.log",
                )
                return
            time.sleep(0.1)
        LOGGER.warning("mpv IPC socket did not appear: %s", self.ipc_path)


player = PlayerController()

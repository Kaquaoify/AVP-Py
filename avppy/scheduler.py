from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from datetime import datetime

from .config import load_config
from .player import player
from .sync import sync_now

LOGGER = logging.getLogger(__name__)


class Scheduler:
    def __init__(self) -> None:
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.last_sync_key = ""
        self.last_reboot_key = ""
        self.playback_active = False

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="avp-scheduler", daemon=True)
        self.thread.start()

    def _run(self) -> None:
        LOGGER.info("Scheduler started")
        while not self.stop_event.is_set():
            try:
                self.tick()
            except Exception:
                LOGGER.exception("Scheduler tick failed")
            self.stop_event.wait(10)

    def tick(self) -> None:
        config = load_config()
        now = datetime.now()
        player.ensure_idle(config)
        self._handle_playback(config, now)
        self._handle_sync(config, now)
        self._handle_reboot(config, now)

    def _handle_playback(self, config: dict, now: datetime) -> None:
        should_play = self._is_playback_time(config, now)
        if should_play and not self.playback_active:
            count = player.play_playlist(config["local_media_dir"], config)
            self.playback_active = count > 0
            LOGGER.info("Scheduled playback started with %s media files", count)
            return

        if not should_play and self.playback_active:
            player.stop_to_black()
            self.playback_active = False
            LOGGER.info("Scheduled playback stopped")

    def _handle_sync(self, config: dict, now: datetime) -> None:
        if config.get("media_source", "rclone") != "rclone":
            return
        sync_time = config.get("sync_time", "03:00")
        key = f"{now.date()}-{sync_time}"
        if now.strftime("%H:%M") == sync_time and self.last_sync_key != key:
            self.last_sync_key = key
            ok, output = sync_now(config)
            LOGGER.info("Scheduled sync finished ok=%s output=%s", ok, output[-500:])

    def _handle_reboot(self, config: dict, now: datetime) -> None:
        if not config.get("reboot_enabled", True):
            return
        reboot_time = config.get("reboot_time", "06:00")
        key = f"{now.date()}-{reboot_time}"
        if now.strftime("%H:%M") == reboot_time and self.last_reboot_key != key:
            self.last_reboot_key = key
            LOGGER.info("Scheduled reboot requested")
            if os.name != "nt":
                subprocess.Popen(["sudo", "systemctl", "reboot"])

    @staticmethod
    def _is_playback_time(config: dict, now: datetime) -> bool:
        if now.weekday() not in set(config.get("playback_days", [])):
            return False
        start = config.get("playback_start", "08:00")
        end = config.get("playback_end", "20:00")
        current = now.strftime("%H:%M")
        if start <= end:
            return start <= current < end
        return current >= start or current < end


scheduler = Scheduler()

from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from datetime import datetime

from .cec import cec_controller, normalize_cec_adapter
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
        self.display_state_key: tuple[str, bool] | None = None
        self.display_command_ok = False
        self.display_retry_at = 0.0
        self.display_command_thread: threading.Thread | None = None
        self.display_failure_count = 0

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
        self._handle_display(config, now)
        self._handle_playback(config, now)
        if not self._is_playback_time(config, now):
            player.ensure_idle(config)
        self._handle_sync(config, now)
        self._handle_reboot(config, now)

    def _handle_playback(self, config: dict, now: datetime) -> None:
        should_play = self._is_playback_time(config, now)
        if should_play and (not self.playback_active or not player.is_playlist_active()):
            result = player.play_playlist(config["local_media_dir"], config)
            self.playback_active = result.started
            if result.started:
                LOGGER.info(
                    "Scheduled playback started with %s media files",
                    result.media_count,
                )
            elif result.media_count:
                LOGGER.info(
                    "Scheduled playback is waiting for mpv with %s media files queued",
                    result.media_count,
                )
            return

        if not should_play and self.playback_active:
            player.stop_to_black()
            self.playback_active = False
            LOGGER.info("Scheduled playback stopped")

    def _handle_display(self, config: dict, now: datetime) -> None:
        if not config.get("cec_schedule_enabled", False):
            self.display_state_key = None
            self.display_command_ok = False
            self.display_retry_at = 0.0
            self.display_failure_count = 0
            return

        if self.display_command_thread and self.display_command_thread.is_alive():
            return

        should_be_on = self._is_playback_time(config, now)
        adapter = normalize_cec_adapter(config.get("cec_adapter"))
        state_key = (adapter, should_be_on)
        monotonic_now = time.monotonic()

        if state_key == self.display_state_key:
            if self.display_command_ok or monotonic_now < self.display_retry_at:
                return
        else:
            self.display_failure_count = 0

        self.display_command_thread = threading.Thread(
            target=self._run_display_action,
            args=(state_key, adapter, should_be_on),
            name="avp-cec",
            daemon=True,
        )
        self.display_command_thread.start()

    def _run_display_action(
        self,
        state_key: tuple[str, bool],
        adapter: str,
        should_be_on: bool,
    ) -> None:
        action = "power on" if should_be_on else "standby"
        try:
            result = (
                cec_controller.power_on(adapter)
                if should_be_on
                else cec_controller.standby(adapter)
            )
        except Exception:
            self.display_state_key = state_key
            self.display_command_ok = False
            retry_delay = self._next_display_retry_delay(should_be_on)
            self.display_retry_at = time.monotonic() + retry_delay
            LOGGER.exception(
                "Scheduled display action=%s crashed; retry in %s seconds",
                action,
                retry_delay,
            )
            return

        self.display_state_key = state_key
        self.display_command_ok = result.ok
        if result.ok:
            self.display_failure_count = 0
            self.display_retry_at = 0.0
            LOGGER.info("Scheduled display action=%s succeeded: %s", action, result.message)
        else:
            retry_delay = self._next_display_retry_delay(should_be_on)
            self.display_retry_at = time.monotonic() + retry_delay
            LOGGER.error(
                "Scheduled display action=%s failed; retry in %s seconds: %s %s",
                action,
                retry_delay,
                result.message,
                result.details[-500:],
            )

    def _next_display_retry_delay(self, should_be_on: bool) -> int:
        delays = (10, 30, 60) if should_be_on else (10, 30, 60, 300)
        delay = delays[min(self.display_failure_count, len(delays) - 1)]
        self.display_failure_count += 1
        return delay

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

from __future__ import annotations

import logging
import os
import subprocess
import threading


LOGGER = logging.getLogger(__name__)


class SystemController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reboot_pending = False
        self.reboot_thread: threading.Thread | None = None

    def request_reboot(self, delay_seconds: float = 1.0) -> tuple[bool, str]:
        if os.name == "nt":
            return False, "Le redémarrage système est indisponible sous Windows."

        with self._lock:
            if self.reboot_pending:
                return True, "Le redémarrage est déjà en cours."
            self.reboot_pending = True

        self.reboot_thread = threading.Thread(
            target=self._perform_reboot,
            args=(delay_seconds,),
            name="avp-reboot",
            daemon=True,
        )
        self.reboot_thread.start()
        return True, "Le Raspberry Pi va redémarrer."

    def _perform_reboot(self, delay_seconds: float) -> None:
        if delay_seconds > 0:
            threading.Event().wait(delay_seconds)

        LOGGER.warning("System reboot requested")
        try:
            result = subprocess.run(
                ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "reboot"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            LOGGER.error("Could not execute system reboot: %s", exc)
            self._clear_pending()
            return

        if result.returncode != 0:
            output = "\n".join(
                part.strip() for part in (result.stdout, result.stderr) if part.strip()
            )
            LOGGER.error(
                "System reboot command failed code=%s output=%s",
                result.returncode,
                output[-1000:],
            )
            self._clear_pending()

    def _clear_pending(self) -> None:
        with self._lock:
            self.reboot_pending = False


system_controller = SystemController()

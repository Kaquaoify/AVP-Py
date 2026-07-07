from __future__ import annotations

import logging
import os
from pathlib import Path
import subprocess
import threading


LOGGER = logging.getLogger(__name__)


class SystemController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reboot_pending = False
        self.reboot_thread: threading.Thread | None = None
        self.update_pending = False
        self.update_thread: threading.Thread | None = None
        self.update_message = ""

    def request_reboot(self, delay_seconds: float = 1.0) -> tuple[bool, str]:
        if os.name == "nt":
            return False, "Le red\u00e9marrage syst\u00e8me est indisponible sous Windows."

        with self._lock:
            if self.reboot_pending:
                return True, "Le red\u00e9marrage est d\u00e9j\u00e0 en cours."
            self.reboot_pending = True

        self.reboot_thread = threading.Thread(
            target=self._perform_reboot,
            args=(delay_seconds,),
            name="avp-reboot",
            daemon=True,
        )
        self.reboot_thread.start()
        return True, "Le Raspberry Pi va red\u00e9marrer."

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

    def request_update(self, script_path: Path, log_path: Path, delay_seconds: float = 1.0) -> tuple[bool, str]:
        if os.name == "nt":
            return False, "La mise \u00e0 jour depuis l'interface web est indisponible sous Windows."
        if not script_path.exists():
            return False, f"Script de mise \u00e0 jour introuvable : {script_path}"

        with self._lock:
            if self.update_pending:
                return True, "Une mise \u00e0 jour est d\u00e9j\u00e0 en cours."
            self.update_pending = True
            self.update_message = "Mise \u00e0 jour en cours."

        self.update_thread = threading.Thread(
            target=self._perform_update,
            args=(script_path, log_path, delay_seconds),
            name="avp-update",
            daemon=True,
        )
        self.update_thread.start()
        return True, "La mise \u00e0 jour va d\u00e9marrer."

    def update_status(self) -> dict:
        with self._lock:
            return {
                "pending": self.update_pending,
                "message": self.update_message,
            }

    def _perform_update(self, script_path: Path, log_path: Path, delay_seconds: float) -> None:
        if delay_seconds > 0:
            threading.Event().wait(delay_seconds)

        LOGGER.warning("Application update requested")
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as output:
                output.write("\n=== AVP-Py web update requested ===\n")
                output.flush()
                command = ["/usr/bin/sudo", "-n", "/bin/bash", str(script_path)]
                process = subprocess.Popen(
                    command,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                return_code = process.wait()
        except (FileNotFoundError, OSError) as exc:
            LOGGER.error("Could not execute application update: %s", exc)
            self._clear_update_pending(f"Mise \u00e0 jour impossible : {exc}")
            return

        if return_code != 0:
            LOGGER.error("Application update failed code=%s", return_code)
            self._clear_update_pending(
                "La mise \u00e0 jour a \u00e9chou\u00e9. Consulte les logs pour le d\u00e9tail."
            )
            return

        self._clear_update_pending("Mise \u00e0 jour termin\u00e9e.")

    def _clear_update_pending(self, message: str) -> None:
        with self._lock:
            self.update_pending = False
            self.update_message = message


system_controller = SystemController()

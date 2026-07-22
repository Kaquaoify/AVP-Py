from __future__ import annotations

import logging
import os
import re
import subprocess
import threading
import unicodedata
from dataclasses import dataclass
from typing import Any

from .config import load_config

LOGGER = logging.getLogger(__name__)


SETUP_CONNECTION_NAME = "avp-py-setup"


@dataclass
class CommandResult:
    ok: bool
    output: str


class NetworkController:
    def __init__(self) -> None:
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.setup_active = False
        self.connecting_to_wifi = False
        self.last_error = ""
        self._state_lock = threading.Lock()
        self._command_lock = threading.RLock()

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="avp-network", daemon=True)
        self.thread.start()

    def status(self) -> dict[str, Any]:
        config = load_config()
        return {
            "enabled": config.get("network_setup_enabled", True),
            "setup_active": self.setup_active,
            "connecting_to_wifi": self.is_connecting_to_wifi(),
            "last_error": self.last_error,
            "connected": has_network_connection(),
            "local_ips": local_ip_addresses(),
            "hotspot_ssid": setup_ssid(config),
            "hotspot_password": config.get("setup_wifi_password", ""),
            "interface": config.get("network_interface", "wlan0"),
            "devices": device_status(),
        }

    def _run(self) -> None:
        if os.name == "nt":
            LOGGER.info("Network setup monitor disabled on Windows")
            return

        delay_done = False
        while not self.stop_event.is_set():
            config = load_config()
            if not config.get("network_setup_enabled", True):
                if not self.is_connecting_to_wifi():
                    self.stop_hotspot()
                self.stop_event.wait(30)
                continue

            if not delay_done:
                delay = int(config.get("network_check_delay_seconds", 75))
                LOGGER.info("Waiting %s seconds before network setup check", delay)
                self.stop_event.wait(delay)
                delay_done = True

            try:
                if self.is_connecting_to_wifi():
                    self.stop_event.wait(5)
                    continue

                if has_network_connection():
                    if self.setup_active:
                        self.stop_hotspot()
                    self.last_error = ""
                elif not self.setup_active:
                    result = self.start_hotspot(config)
                    self.last_error = "" if result.ok else result.output
            except Exception as exc:
                LOGGER.exception("Network monitor failed")
                self.last_error = str(exc)

            self.stop_event.wait(30)

    def is_connecting_to_wifi(self) -> bool:
        with self._state_lock:
            return self.connecting_to_wifi

    def _set_connecting_to_wifi(self, value: bool) -> None:
        with self._state_lock:
            self.connecting_to_wifi = value

    def start_hotspot(self, config: dict[str, Any]) -> CommandResult:
        if self.is_connecting_to_wifi():
            return CommandResult(False, "Connexion Wi-Fi en cours, relance du hotspot bloquee.")

        with self._command_lock:
            if self.is_connecting_to_wifi():
                return CommandResult(False, "Connexion Wi-Fi en cours, relance du hotspot bloquee.")
            return self._start_hotspot_unlocked(config)

    def _start_hotspot_unlocked(self, config: dict[str, Any]) -> CommandResult:
        interface = config.get("network_interface", "wlan0")
        ssid = setup_ssid(config)
        password = config.get("setup_wifi_password", "avpsetup123")

        LOGGER.info("Starting setup hotspot %s on %s", ssid, interface)
        run_nmcli(["connection", "down", SETUP_CONNECTION_NAME], check=False)
        result = run_nmcli(
            [
                "device",
                "wifi",
                "hotspot",
                "ifname",
                interface,
                "con-name",
                SETUP_CONNECTION_NAME,
                "ssid",
                ssid,
                "password",
                password,
            ],
            timeout=45,
        )
        if result.ok:
            run_nmcli(["connection", "modify", SETUP_CONNECTION_NAME, "connection.autoconnect", "no"], check=False)
        self.setup_active = result.ok
        if not result.ok:
            LOGGER.error("Could not start setup hotspot: %s", result.output)
        return result

    def stop_hotspot(self) -> CommandResult:
        with self._command_lock:
            return self._stop_hotspot_unlocked()

    def _stop_hotspot_unlocked(self) -> CommandResult:
        LOGGER.info("Stopping setup hotspot")
        result = run_nmcli(["connection", "down", SETUP_CONNECTION_NAME], check=False)
        run_nmcli(["connection", "modify", SETUP_CONNECTION_NAME, "connection.autoconnect", "no"], check=False)
        self.setup_active = False
        return result

    def connect_wifi(self, ssid: str, password: str, interface: str) -> CommandResult:
        ssid = ssid.strip()
        if not ssid:
            return CommandResult(False, "Le SSID est vide.")

        with self._command_lock:
            self._set_connecting_to_wifi(True)
            try:
                self._stop_hotspot_unlocked()
                args = ["device", "wifi", "connect", ssid, "ifname", interface]
                if password:
                    args.extend(["password", password])

                result = run_nmcli(args, timeout=60)
                if result.ok:
                    self.setup_active = False
                    self.last_error = ""
                    LOGGER.info("Connected to Wi-Fi SSID %s", ssid)
                else:
                    LOGGER.error("Wi-Fi connection failed for %s: %s", ssid, result.output)
                    config = load_config()
                    hotspot_result = self._start_hotspot_unlocked(config)
                    self.last_error = "" if hotspot_result.ok else hotspot_result.output
                return result
            finally:
                self._set_connecting_to_wifi(False)


def setup_ssid(config: dict[str, Any]) -> str:
    prefix = config.get("setup_ssid_prefix", "AVP-SETUP")
    device_name = slugify(config.get("device_name", "avp-py"))
    return f"{prefix}-{device_name}"[:32]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "avp-py"


def set_device_hostname(value: str) -> CommandResult:
    hostname = slugify(value)[:63].strip("-") or "avp-py"
    if os.name == "nt":
        return CommandResult(True, hostname)

    try:
        result = subprocess.run(
            ["sudo", "hostnamectl", "set-hostname", hostname],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except FileNotFoundError:
        return CommandResult(False, "sudo ou hostnamectl est introuvable.")
    except subprocess.TimeoutExpired:
        return CommandResult(False, "Le changement de nom d'hôte a dépassé le délai autorisé.")

    output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode != 0:
        return CommandResult(False, output or f"Erreur hostnamectl code {result.returncode}")

    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "avahi-daemon.service"],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        LOGGER.warning("Hostname changed, but Avahi could not be restarted")
    return CommandResult(True, hostname)


def has_network_connection() -> bool:
    for row in device_status():
        if (
            row["type"] in {"ethernet", "wifi"}
            and row["state"].startswith("connected")
            and row.get("connection") != SETUP_CONNECTION_NAME
        ):
            return True
    return False


def local_ip_addresses() -> list[str]:
    if os.name == "nt":
        return []

    try:
        result = subprocess.run(
            ["hostname", "-I"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    if result.returncode != 0:
        return []

    addresses: list[str] = []
    for value in result.stdout.split():
        if ":" in value or value.startswith("127."):
            continue
        addresses.append(value)
    return addresses


def device_status() -> list[dict[str, str]]:
    result = run_nmcli(["-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"], check=False)
    if not result.ok:
        return []
    devices: list[dict[str, str]] = []
    for line in result.output.splitlines():
        parts = _split_nmcli_terse(line)
        if len(parts) >= 3:
            devices.append(
                {
                    "device": parts[0],
                    "type": parts[1],
                    "state": parts[2],
                    "connection": parts[3] if len(parts) > 3 else "",
                }
            )
    return devices


def scan_wifi() -> list[dict[str, str]]:
    result = run_nmcli(
        ["-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "yes"],
        timeout=30,
    )
    if not result.ok:
        return []

    networks: dict[str, dict[str, str]] = {}
    for line in result.output.splitlines():
        parts = _split_nmcli_terse(line)
        if len(parts) < 2 or not parts[0]:
            continue
        ssid = parts[0]
        signal = parts[1]
        security = parts[2] if len(parts) > 2 else ""
        previous = networks.get(ssid)
        if previous is None or int(signal or 0) > int(previous.get("signal") or 0):
            networks[ssid] = {"ssid": ssid, "signal": signal, "security": security}
    return sorted(networks.values(), key=lambda item: int(item.get("signal") or 0), reverse=True)


def connect_wifi(ssid: str, password: str, interface: str) -> CommandResult:
    return network.connect_wifi(ssid, password, interface)


def run_nmcli(args: list[str], timeout: int = 15, check: bool = True) -> CommandResult:
    if os.name == "nt":
        return CommandResult(False, "nmcli non disponible sous Windows.")

    command = ["sudo", "nmcli", *args]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return CommandResult(False, "nmcli ou sudo est introuvable.")
    except subprocess.TimeoutExpired:
        return CommandResult(False, "La commande nmcli a dépassé le délai autorisé.")

    output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode == 0 or not check:
        return CommandResult(result.returncode == 0, output)
    return CommandResult(False, output or f"Erreur nmcli code {result.returncode}")


def _split_nmcli_terse(line: str) -> list[str]:
    placeholder = "\u0000"
    return [part.replace(placeholder, ":") for part in line.replace(r"\:", placeholder).split(":")]


network = NetworkController()

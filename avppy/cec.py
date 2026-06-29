from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


LOGGER = logging.getLogger(__name__)

CEC_ADAPTERS = (
    ("/dev/cec0", "HDMI 0 (/dev/cec0)"),
    ("/dev/cec1", "HDMI 1 (/dev/cec1)"),
)

CEC_BRANDS = (
    ("auto", "Automatique / CEC standard"),
    ("samsung", "Samsung — Anynet+"),
    ("lg", "LG — SIMPLINK"),
    ("sony", "Sony — BRAVIA Sync"),
    ("panasonic", "Panasonic — VIERA Link"),
    ("philips", "Philips — EasyLink"),
    ("tcl", "TCL — T-Link"),
    ("hisense", "Hisense — HDMI-CEC"),
    ("other", "Autre marque — CEC standard"),
)

_VALID_ADAPTERS = {value for value, _label in CEC_ADAPTERS}
_VALID_BRANDS = {value for value, _label in CEC_BRANDS}
_PHYSICAL_ADDRESS = re.compile(r"\b([0-9a-f]\.){3}[0-9a-f]\b", re.IGNORECASE)


@dataclass(frozen=True)
class CecResult:
    ok: bool
    message: str
    details: str = ""


def normalize_cec_adapter(value: object) -> str:
    adapter = str(value or "")
    return adapter if adapter in _VALID_ADAPTERS else "/dev/cec0"


def normalize_cec_brand(value: object) -> str:
    brand = str(value or "")
    return brand if brand in _VALID_BRANDS else "auto"


class CecController:
    command_timeout = 10

    def status(self, adapter: object) -> dict[str, object]:
        selected = normalize_cec_adapter(adapter)
        tool_path = shutil.which("cec-ctl")
        available = [path for path, _label in CEC_ADAPTERS if Path(path).exists()]
        return {
            "adapter": selected,
            "tool_available": bool(tool_path),
            "tool_path": tool_path or "",
            "adapter_available": selected in available,
            "available_adapters": available,
            "supported_platform": os.name != "nt",
        }

    def power_on(self, adapter: object) -> CecResult:
        selected = normalize_cec_adapter(adapter)
        prepared = self._prepare(selected)
        if not prepared.ok:
            return prepared

        wake = self._run(selected, ["--to", "0", "--image-view-on"])
        if not wake.ok:
            return CecResult(False, "La commande d'allumage CEC a échoué.", wake.details)

        physical_address = ""
        address_details = ""
        for attempt in range(3):
            address = self._run(selected, ["--skip-info", "--physical-address"])
            address_details = address.details
            match = _PHYSICAL_ADDRESS.search(address.details)
            if address.ok and match and match.group(0).lower() != "f.f.f.f":
                physical_address = match.group(0)
                break
            if attempt < 2:
                time.sleep(1)

        details = self._join_details(prepared.details, wake.details, address_details)
        if not physical_address:
            return CecResult(
                False,
                "Commande d'allumage envoyée, mais l'entrée HDMI n'a pas pu être "
                "sélectionnée automatiquement.",
                details,
            )

        select_input = self._run(
            selected,
            ["--to", "0", "--active-source", f"phys-addr={physical_address}"],
        )
        details = self._join_details(details, select_input.details)
        if not select_input.ok:
            return CecResult(
                False,
                "Commande d'allumage envoyée, mais la sélection automatique de "
                "l'entrée HDMI a échoué.",
                details,
            )

        return CecResult(
            True,
            "Commandes d'allumage et de sélection de l'entrée HDMI envoyées.",
            details,
        )

    def standby(self, adapter: object) -> CecResult:
        selected = normalize_cec_adapter(adapter)
        prepared = self._prepare(selected)
        if not prepared.ok:
            return prepared

        standby = self._run(selected, ["--to", "0", "--standby"])
        details = self._join_details(prepared.details, standby.details)
        if not standby.ok:
            return CecResult(False, "La commande de mise en veille CEC a échoué.", details)
        return CecResult(True, "Commande de mise en veille envoyée.", details)

    def _prepare(self, adapter: str) -> CecResult:
        if os.name == "nt":
            return CecResult(
                False,
                "Le contrôle HDMI-CEC est disponible uniquement sur le Raspberry Pi.",
            )
        if not shutil.which("cec-ctl"):
            return CecResult(False, "cec-ctl est introuvable. Installe le paquet v4l-utils.")
        if not Path(adapter).exists():
            return CecResult(
                False,
                f"L'adaptateur {adapter} est introuvable. Vérifie le port HDMI "
                "et la compatibilité CEC.",
            )

        configured = self._run(adapter, ["--playback", "--osd-name", "AVP-Py"])
        if not configured.ok:
            return CecResult(
                False,
                f"Impossible d'initialiser l'adaptateur CEC {adapter}.",
                configured.details,
            )
        return CecResult(True, "Adaptateur CEC initialisé.", configured.details)

    def _run(self, adapter: str, arguments: list[str]) -> CecResult:
        command = ["cec-ctl", "-d", adapter, *arguments]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.command_timeout,
            )
        except FileNotFoundError:
            return CecResult(False, "cec-ctl est introuvable.")
        except subprocess.TimeoutExpired:
            return CecResult(False, "La commande CEC a dépassé le délai autorisé.")

        output = self._join_details(result.stdout, result.stderr)
        if result.returncode != 0:
            LOGGER.error("CEC command failed code=%s output=%s", result.returncode, output[-1000:])
            return CecResult(False, f"Erreur cec-ctl (code {result.returncode}).", output)
        return CecResult(True, "Commande CEC exécutée.", output)

    @staticmethod
    def _join_details(*parts: str) -> str:
        return "\n".join(part.strip() for part in parts if part and part.strip())[-4000:]


cec_controller = CecController()

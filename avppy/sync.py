from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from .config import LOG_DIR, write_rclone_config_if_needed
from .media import scan_media

LOGGER = logging.getLogger(__name__)


def remote_target(config: dict) -> str:
    remote = (config.get("rclone_remote") or "").strip().rstrip(":")
    remote_path = (config.get("rclone_path") or "").strip().strip("/")
    if not remote:
        raise ValueError("Le nom du remote rclone est vide.")
    return f"{remote}:{remote_path}" if remote_path else f"{remote}:"


def rclone_env(config: dict) -> dict[str, str]:
    env = os.environ.copy()
    env.update(write_rclone_config_if_needed(config))
    return env


def test_connection(config: dict) -> tuple[bool, str]:
    target = remote_target(config)
    command = ["rclone", "lsf", target, "--max-depth", "1"]
    return _run_rclone(command, config)


def sync_now(config: dict, regenerate_thumbnails: bool = True) -> tuple[bool, str]:
    target = remote_target(config)
    local_dir = Path(config["local_media_dir"])
    local_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "rclone",
        "sync",
        target,
        str(local_dir),
        "--create-empty-src-dirs",
        "--log-file",
        str(LOG_DIR / "rclone.log"),
        "--log-level",
        "INFO",
    ]
    ok, output = _run_rclone(command, config, timeout=3600)
    if ok:
        scan_media(local_dir, regenerate_thumbnails=regenerate_thumbnails)
    return ok, output


def _run_rclone(command: list[str], config: dict, timeout: int = 120) -> tuple[bool, str]:
    LOGGER.info("Running rclone command: %s", " ".join(command))
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=rclone_env(config),
        )
    except FileNotFoundError:
        message = "rclone n'est pas installé ou introuvable dans le PATH."
        LOGGER.error(message)
        return False, message
    except subprocess.TimeoutExpired:
        message = "La commande rclone a dépassé le délai autorisé."
        LOGGER.error(message)
        return False, message

    output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode == 0:
        LOGGER.info("rclone command completed")
        return True, output or "OK"

    LOGGER.error("rclone command failed: %s", output)
    return False, output or f"Erreur rclone code {result.returncode}"


from __future__ import annotations

import logging
import os
import subprocess
import threading
from pathlib import Path

from .config import (
    LOG_DIR,
    RCLONE_SOURCE_DIR,
    RCLONE_SOURCE_READY_FILE,
    write_rclone_config_if_needed,
)
from .media_optimizer import bootstrap_rclone_source, media_optimizer

LOGGER = logging.getLogger(__name__)
SYNC_LOCK = threading.Lock()


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
    del regenerate_thumbnails
    if not SYNC_LOCK.acquire(blocking=False):
        return False, "Une synchronisation rclone est déjà en cours."

    media_optimizer.set_sync_active(True)
    try:
        target = remote_target(config)
        playback_dir = Path(config["local_media_dir"])
        source_dir = RCLONE_SOURCE_DIR
        source_dir.mkdir(parents=True, exist_ok=True)
        bootstrap_rclone_source(playback_dir)
        command = [
            "rclone",
            "sync",
            target,
            str(source_dir),
            "--create-empty-src-dirs",
            "--checksum",
            "--log-file",
            str(LOG_DIR / "rclone.log"),
            "--log-level",
            "INFO",
        ]
        ok, output = _run_rclone(command, config, timeout=3600)
    finally:
        media_optimizer.set_sync_active(False)
        SYNC_LOCK.release()
    if ok:
        RCLONE_SOURCE_READY_FILE.write_text("ready\n", encoding="utf-8")
        queued = media_optimizer.request("rclone")
        output = f"{output}\n{queued}".strip()
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

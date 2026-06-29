from __future__ import annotations

import hashlib
import json
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any


DATA_DIR = Path(os.environ.get("AVPPY_DATA_DIR", Path.cwd() / "data")).resolve()
CONFIG_FILE = DATA_DIR / "config.json"
MEDIA_DIR = DATA_DIR / "media"
THUMB_DIR = DATA_DIR / "thumbnails"
LOG_DIR = DATA_DIR / "logs"
RCLONE_CONFIG_FILE = DATA_DIR / "rclone.conf"
RCLONE_CONFIG_SOURCE_HASH_FILE = DATA_DIR / "rclone-config-source.sha256"


def ensure_directories() -> None:
    for directory in (DATA_DIR, MEDIA_DIR, THUMB_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt, expected = encoded.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hash_password(password, salt).split("$", 2)[2]
    return secrets.compare_digest(candidate, expected)


def default_config() -> dict[str, Any]:
    return {
        "device_name": os.environ.get("HOSTNAME", "avp-py"),
        "admin_password_hash": hash_password("1234"),
        "secret_key": secrets.token_hex(32),
        "local_media_dir": str(MEDIA_DIR),
        "media_source": "rclone",
        "playback_days": [0, 1, 2, 3, 4, 5, 6],
        "playback_start": "08:00",
        "playback_end": "20:00",
        "sync_time": "03:00",
        "reboot_enabled": True,
        "reboot_time": "06:00",
        "cec_brand": "auto",
        "cec_adapter": "/dev/cec0",
        "cec_schedule_enabled": False,
        "rclone_remote": "gdrive",
        "rclone_path": "",
        "rclone_config_text": "",
        "volume": 70,
        "mpv_extra_args": "--vo=gpu --gpu-context=drm",
        "network_setup_enabled": True,
        "network_interface": "wlan0",
        "network_check_delay_seconds": 75,
        "setup_ssid_prefix": "AVP-SETUP",
        "setup_wifi_password": "avpsetup123",
    }


def load_config() -> dict[str, Any]:
    ensure_directories()
    if not CONFIG_FILE.exists():
        config = default_config()
        save_config(config)
        return config

    with CONFIG_FILE.open("r", encoding="utf-8") as fh:
        loaded = json.load(fh)

    config = default_config()
    config.update(loaded)
    return config


def save_config(config: dict[str, Any]) -> None:
    ensure_directories()
    fd, temp_name = tempfile.mkstemp(prefix="config-", suffix=".json", dir=DATA_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        Path(temp_name).replace(CONFIG_FILE)
    finally:
        temp_path = Path(temp_name)
        if temp_path.exists():
            temp_path.unlink()


def update_config(changes: dict[str, Any]) -> dict[str, Any]:
    config = load_config()
    config.update(changes)
    save_config(config)
    return config


def write_rclone_config_if_needed(config: dict[str, Any]) -> dict[str, str]:
    text = (config.get("rclone_config_text") or "").strip()
    if not text:
        return {}
    source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    applied_hash = ""
    if RCLONE_CONFIG_SOURCE_HASH_FILE.exists():
        applied_hash = RCLONE_CONFIG_SOURCE_HASH_FILE.read_text(encoding="utf-8").strip()

    if not RCLONE_CONFIG_FILE.exists() or applied_hash != source_hash:
        RCLONE_CONFIG_FILE.write_text(text + "\n", encoding="utf-8")
        RCLONE_CONFIG_FILE.chmod(0o600)
        RCLONE_CONFIG_SOURCE_HASH_FILE.write_text(source_hash + "\n", encoding="utf-8")
    return {"RCLONE_CONFIG": str(RCLONE_CONFIG_FILE)}

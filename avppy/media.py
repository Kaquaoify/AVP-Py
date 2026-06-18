from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from .config import THUMB_DIR

LOGGER = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mpg", ".mpeg"}


def is_video(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def probe_media(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=True)
        payload = json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError) as exc:
        LOGGER.warning("ffprobe failed for %s: %s", path, exc)
        return {}

    streams = payload.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    fmt = payload.get("format", {})
    width = video_stream.get("width")
    height = video_stream.get("height")
    duration = float(fmt.get("duration") or video_stream.get("duration") or 0)

    return {
        "duration": round(duration, 1),
        "codec": video_stream.get("codec_name", ""),
        "format": fmt.get("format_long_name") or fmt.get("format_name", ""),
        "resolution": f"{width}x{height}" if width and height else "",
        "container": path.suffix.lower().lstrip("."),
    }


def thumbnail_name(path: Path) -> str:
    digest = hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()
    return f"{digest}.jpg"


def generate_thumbnail(path: Path, force: bool = False) -> str:
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    name = thumbnail_name(path)
    output = THUMB_DIR / name
    if output.exists() and not force:
        return name

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        "00:00:01",
        "-i",
        str(path),
        "-frames:v",
        "1",
        "-vf",
        "scale=320:-1",
        str(output),
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, timeout=30, check=True)
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        LOGGER.warning("ffmpeg thumbnail failed for %s: %s", path, exc)
        return ""
    return name


def scan_media(media_dir: str | Path, regenerate_thumbnails: bool = False) -> list[dict[str, Any]]:
    root = Path(media_dir)
    root.mkdir(parents=True, exist_ok=True)
    files = sorted((p for p in root.rglob("*") if is_video(p)), key=lambda p: p.name.lower())
    items: list[dict[str, Any]] = []

    for index, path in enumerate(files, start=1):
        metadata = probe_media(path)
        thumb = generate_thumbnail(path, force=regenerate_thumbnails)
        items.append(
            {
                "index": index,
                "filename": path.name,
                "title": path.stem,
                "path": str(path),
                "thumbnail": thumb,
                **metadata,
            }
        )
    return items


def write_playlist(media_dir: str | Path, playlist_path: Path) -> int:
    files = sorted((p for p in Path(media_dir).rglob("*") if is_video(p)), key=lambda p: p.name.lower())
    playlist_path.parent.mkdir(parents=True, exist_ok=True)
    playlist_path.write_text("\n".join(str(path) for path in files) + "\n", encoding="utf-8")
    return len(files)


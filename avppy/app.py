from __future__ import annotations

import hmac
import logging
import shutil
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    DATA_DIR,
    LOG_DIR,
    THUMB_DIR,
    hash_password,
    load_config,
    save_config,
    update_config,
    verify_password,
)
from .logging_setup import configure_logging
from .media import (
    VIDEO_EXTENSIONS,
    generate_thumbnail,
    is_video,
    move_media,
    ordered_media_files,
    probe_media,
    remove_thumbnail,
    resolve_media_path,
    save_media_order,
    scan_media,
    write_playlist,
)
from .network import connect_wifi, network, scan_wifi, set_device_hostname, slugify
from .player import player
from .scheduler import scheduler
from .sync import sync_now, test_connection

configure_logging()
LOGGER = logging.getLogger(__name__)

PACKAGE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))

app = FastAPI(title="AVP-Py")
app.mount("/static", StaticFiles(directory=str(PACKAGE_DIR / "static")), name="static")


@app.on_event("startup")
def startup() -> None:
    config = load_config()
    network.start()
    player.ensure_idle(config)
    scheduler.start()
    LOGGER.info("AVP-Py started")


def _auth_signature(config: dict) -> str:
    return hmac.new(config["secret_key"].encode(), b"avp-py-admin", sha256).hexdigest()


def is_authenticated(request: Request, config: dict) -> bool:
    token = request.cookies.get("avppy_auth", "")
    return hmac.compare_digest(token, _auth_signature(config))


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def require_login(request: Request, config: dict) -> RedirectResponse | None:
    if not is_authenticated(request, config):
        return redirect("/login")
    return None


def setup_mode_or_login(request: Request, config: dict) -> RedirectResponse | None:
    if network.setup_active:
        return None
    return require_login(request, config)


def clock_status() -> dict:
    now = datetime.now().astimezone()
    offset = now.utcoffset()
    offset_minutes = int(offset.total_seconds() // 60) if offset else 0
    sign = "+" if offset_minutes >= 0 else "-"
    hours, minutes = divmod(abs(offset_minutes), 60)
    return {
        "iso": now.isoformat(timespec="seconds"),
        "display": now.strftime("%d.%m.%Y %H:%M:%S"),
        "timezone": now.tzname() or "UTC",
        "utc_offset": f"UTC{sign}{hours:02d}:{minutes:02d}",
        "offset_minutes": offset_minutes,
    }


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    config = load_config()
    return templates.TemplateResponse("login.html", {"request": request, "config": config, "error": ""})


@app.post("/login")
def login(request: Request, password: str = Form(...)):
    config = load_config()
    if not verify_password(password, config["admin_password_hash"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "config": config, "error": "Mot de passe incorrect."},
            status_code=401,
        )
    response = redirect("/")
    response.set_cookie("avppy_auth", _auth_signature(config), httponly=True, samesite="lax", max_age=2_592_000)
    return response


@app.post("/logout")
def logout():
    response = redirect("/login")
    response.delete_cookie("avppy_auth")
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    media = scan_media(config["local_media_dir"])
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "config": config,
            "media": media,
            "player_status": player.status(),
            "clock": clock_status(),
        },
    )


@app.post("/control")
async def control(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    form = await request.form()
    action = str(form.get("action", ""))
    if action == "play":
        count = player.play_playlist(config["local_media_dir"], config)
        scheduler.playback_active = count > 0
    elif action == "pause":
        player.pause_to_black()
        scheduler.playback_active = False
    elif action == "next":
        player.next()
    elif action == "previous":
        player.previous()
    return redirect("/")


@app.post("/volume")
def volume(request: Request, volume_value: int = Form(...)):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    volume_value = max(0, min(100, volume_value))
    config["volume"] = volume_value
    save_config(config)
    player.set_volume(volume_value)
    return redirect("/")


@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    return templates.TemplateResponse("settings.html", {"request": request, "config": config})


@app.get("/setup/wifi", response_class=HTMLResponse)
def setup_wifi_page(request: Request, message: str = ""):
    config = load_config()
    if login_redirect := setup_mode_or_login(request, config):
        return login_redirect
    return templates.TemplateResponse(
        "wifi_setup.html",
        {
            "request": request,
            "config": config,
            "message": message,
            "networks": scan_wifi(),
            "network_status": network.status(),
            "setup_mode": network.setup_active,
        },
    )


@app.post("/setup/wifi", response_class=HTMLResponse)
async def save_setup_wifi(request: Request):
    config = load_config()
    if login_redirect := setup_mode_or_login(request, config):
        return login_redirect
    form = await request.form()
    ssid = str(form.get("ssid", "")).strip()
    custom_ssid = str(form.get("custom_ssid", "")).strip()
    password = str(form.get("wifi_password", ""))
    target_ssid = custom_ssid or ssid
    result = connect_wifi(target_ssid, password, config.get("network_interface", "wlan0"))
    message = "Connexion Wi-Fi enregistrée." if result.ok else f"Connexion Wi-Fi échouée.\n{result.output}"
    return templates.TemplateResponse(
        "wifi_setup.html",
        {
            "request": request,
            "config": config,
            "message": message,
            "networks": scan_wifi(),
            "network_status": network.status(),
            "setup_mode": network.setup_active,
        },
    )


@app.get("/settings/schedule", response_class=HTMLResponse)
def schedule_page(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    return templates.TemplateResponse("schedule.html", {"request": request, "config": config})


@app.post("/settings/schedule")
async def save_schedule(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    form = await request.form()
    update_config(
        {
            "playback_days": [int(day) for day in form.getlist("playback_days")],
            "playback_start": str(form.get("playback_start", "08:00")),
            "playback_end": str(form.get("playback_end", "20:00")),
            "sync_time": str(form.get("sync_time", "03:00")),
            "reboot_enabled": "reboot_enabled" in form,
            "reboot_time": str(form.get("reboot_time", "06:00")),
        }
    )
    return redirect("/settings/schedule")


@app.get("/settings/folders", response_class=HTMLResponse)
def folders_page(request: Request, message: str = ""):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    return templates.TemplateResponse(
        "folders.html",
        {"request": request, "config": config, "message": message},
    )


@app.get("/settings/network", response_class=HTMLResponse)
def network_page(request: Request, message: str = ""):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    return templates.TemplateResponse(
        "network.html",
        {
            "request": request,
            "config": config,
            "message": message,
            "network_status": network.status(),
            "networks": scan_wifi(),
        },
    )


@app.post("/settings/network", response_class=HTMLResponse)
async def save_network(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    form = await request.form()
    action = str(form.get("action", "save"))
    setup_password = str(form.get("setup_wifi_password", config.get("setup_wifi_password", ""))).strip()
    try:
        network_delay = int(form.get("network_check_delay_seconds", 75))
    except (TypeError, ValueError):
        network_delay = 75
    network_delay = max(10, min(600, network_delay))
    message = "Paramètres sauvegardés."

    if len(setup_password) < 8:
        message = "Le mot de passe du Wi-Fi setup doit contenir au moins 8 caractères."
    else:
        config = update_config(
            {
                "network_setup_enabled": "network_setup_enabled" in form,
                "network_interface": str(form.get("network_interface", config.get("network_interface", "wlan0"))).strip()
                or "wlan0",
                "network_check_delay_seconds": network_delay,
                "setup_ssid_prefix": str(form.get("setup_ssid_prefix", "AVP-SETUP")).strip() or "AVP-SETUP",
                "setup_wifi_password": setup_password,
            }
        )
        if action == "start_setup":
            result = network.start_hotspot(config)
            message = "Hotspot setup démarré." if result.ok else f"Échec hotspot setup.\n{result.output}"
        elif action == "stop_setup":
            network.stop_hotspot()
            message = "Hotspot setup arrêté."

    return templates.TemplateResponse(
        "network.html",
        {
            "request": request,
            "config": load_config(),
            "message": message,
            "network_status": network.status(),
            "networks": scan_wifi(),
        },
    )


@app.post("/settings/folders")
async def save_folders(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    form = await request.form()
    media_source = str(form.get("media_source", config.get("media_source", "rclone")))
    if media_source not in {"rclone", "manual"}:
        media_source = "rclone"
    changes = {
        "media_source": media_source,
        "local_media_dir": str(form.get("local_media_dir", config["local_media_dir"])).strip(),
        "rclone_remote": str(form.get("rclone_remote", config["rclone_remote"])).strip(),
        "rclone_path": str(form.get("rclone_path", config["rclone_path"])).strip(),
        "rclone_config_text": str(form.get("rclone_config_text", "")),
        "mpv_extra_args": str(
            form.get("mpv_extra_args", config.get("mpv_extra_args", ""))
        ).strip(),
    }
    config = update_config(changes)
    action = str(form.get("action", "save"))
    message = "Paramètres sauvegardés."
    if action == "test":
        ok, output = test_connection(config)
        message = ("Connexion OK\n" if ok else "Connexion échouée\n") + output
    elif action == "sync":
        if config.get("media_source", "rclone") != "rclone":
            message = "Synchronisation ignorée : la gestion locale est active."
        else:
            ok, output = sync_now(config)
            message = ("Synchronisation terminée\n" if ok else "Synchronisation échouée\n") + output
    return templates.TemplateResponse(
        "folders.html",
        {"request": request, "config": config, "message": message},
    )


def _format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("o", "Kio", "Mio", "Gio", "Tio"):
        if size < 1024 or unit == "Tio":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} Tio"


def _media_manager_response(request: Request, config: dict, message: str = ""):
    media_root = Path(config["local_media_dir"])
    media_root.mkdir(parents=True, exist_ok=True)
    disk = shutil.disk_usage(media_root)
    return templates.TemplateResponse(
        "media_manager.html",
        {
            "request": request,
            "config": config,
            "message": message,
            "media": scan_media(media_root),
            "disk_free": _format_bytes(disk.free),
            "disk_total": _format_bytes(disk.total),
            "extensions": ", ".join(sorted(VIDEO_EXTENSIONS)),
        },
    )


def _unique_media_destination(root: Path, filename: str) -> Path:
    destination = root / filename
    counter = 2
    while destination.exists():
        destination = root / f"{Path(filename).stem} ({counter}){Path(filename).suffix}"
        counter += 1
    return destination


def _safe_media_name(value: str) -> str:
    basename = Path(value.replace("\\", "/")).name
    return "".join(character for character in basename if character >= " ").strip(" .")


@app.get("/settings/media", response_class=HTMLResponse)
def media_manager_page(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    return _media_manager_response(request, config)


@app.post("/settings/media/upload", response_class=HTMLResponse)
async def upload_media(request: Request, files: list[UploadFile] = File(...)):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    if config.get("media_source", "rclone") != "manual":
        return _media_manager_response(
            request, config, "Envoi refusé : active d'abord la gestion locale."
        )

    media_root = Path(config["local_media_dir"]).resolve()
    media_root.mkdir(parents=True, exist_ok=True)
    upload_dir = media_root.parent / ".avppy-uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    messages: list[str] = []

    for upload in files:
        filename = _safe_media_name(upload.filename or "")
        suffix = Path(filename).suffix.lower()
        if not filename or suffix not in VIDEO_EXTENSIONS:
            messages.append(
                f"Fichier ignoré : {filename or 'nom vide'} (format non pris en charge)."
            )
            await upload.close()
            continue

        temporary = upload_dir / f"{uuid4().hex}{suffix}"
        try:
            with temporary.open("wb") as output:
                while chunk := await upload.read(1024 * 1024):
                    output.write(chunk)

            if not probe_media(temporary):
                messages.append(f"Fichier refusé : {filename} n'est pas une vidéo lisible.")
                continue

            destination = _unique_media_destination(media_root, filename)
            temporary.replace(destination)
            generate_thumbnail(destination, force=True)
            messages.append(f"Vidéo ajoutée : {destination.name}")
        except OSError as exc:
            LOGGER.exception("Media upload failed for %s", filename)
            messages.append(f"Échec de l'envoi de {filename} : {exc}")
        finally:
            await upload.close()
            if temporary.exists():
                temporary.unlink()

    save_media_order(media_root, ordered_media_files(media_root))
    return _media_manager_response(request, config, "\n".join(messages))


@app.post("/settings/media/delete", response_class=HTMLResponse)
def delete_media(request: Request, relative_path: str = Form(...)):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    if config.get("media_source", "rclone") != "manual":
        return _media_manager_response(
            request, config, "Suppression refusée : active d'abord la gestion locale."
        )
    media_root = Path(config["local_media_dir"]).resolve()
    try:
        target = resolve_media_path(media_root, relative_path)
        if not is_video(target):
            raise ValueError("Le fichier vidéo est introuvable.")
        remove_thumbnail(target)
        target.unlink()
        save_media_order(media_root, ordered_media_files(media_root))
        message = f"Vidéo supprimée : {target.name}"
    except (OSError, ValueError) as exc:
        message = f"Suppression impossible : {exc}"
    return _media_manager_response(request, config, message)


@app.post("/settings/media/rename", response_class=HTMLResponse)
def rename_media(request: Request, relative_path: str = Form(...), new_name: str = Form(...)):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    if config.get("media_source", "rclone") != "manual":
        return _media_manager_response(
            request, config, "Renommage refusé : active d'abord la gestion locale."
        )
    media_root = Path(config["local_media_dir"]).resolve()
    try:
        target = resolve_media_path(media_root, relative_path)
        safe_name = _safe_media_name(new_name)
        if not is_video(target):
            raise ValueError("Le fichier vidéo est introuvable.")
        if not safe_name or Path(safe_name).suffix.lower() not in VIDEO_EXTENSIONS:
            raise ValueError("Le nouveau nom doit conserver une extension vidéo valide.")
        destination = target.with_name(safe_name)
        if destination.exists() and destination != target:
            raise ValueError("Un fichier porte déjà ce nom.")

        files = ordered_media_files(media_root)
        remove_thumbnail(target)
        target.rename(destination)
        files = [destination if path == target else path for path in files]
        save_media_order(media_root, files)
        generate_thumbnail(destination, force=True)
        message = f"Vidéo renommée : {destination.name}"
    except (OSError, ValueError) as exc:
        message = f"Renommage impossible : {exc}"
    return _media_manager_response(request, config, message)


@app.post("/settings/media/reorder", response_class=HTMLResponse)
def reorder_media(request: Request, relative_path: str = Form(...), direction: str = Form(...)):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    if config.get("media_source", "rclone") != "manual":
        return _media_manager_response(
            request, config, "Modification refusée : active d'abord la gestion locale."
        )
    changed = direction in {"up", "down"} and move_media(
        config["local_media_dir"], relative_path, direction
    )
    message = "Ordre de lecture modifié." if changed else "Ce média est déjà en bout de liste."
    return _media_manager_response(request, config, message)


@app.post("/settings/media/publish", response_class=HTMLResponse)
def publish_media(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    if scheduler.playback_active:
        count = player.play_playlist(config["local_media_dir"], config)
        scheduler.playback_active = count > 0
    else:
        count = write_playlist(config["local_media_dir"], DATA_DIR / "playlist.m3u")
    return _media_manager_response(request, config, f"Playlist publiée avec {count} vidéo(s).")


@app.get("/settings/logs", response_class=HTMLResponse)
def logs_page(request: Request, file: str = ""):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect

    files = sorted([p.name for p in LOG_DIR.glob("*.log*")])
    selected = file if file in files else (files[0] if files else "")
    content = ""
    if selected:
        log_path = LOG_DIR / selected
        content = log_path.read_text(encoding="utf-8", errors="replace")[-50_000:]
    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "config": config, "files": files, "selected": selected, "content": content},
    )


@app.get("/settings/admin", response_class=HTMLResponse)
def admin_page(request: Request, message: str = ""):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "config": config, "message": message},
    )


@app.post("/settings/admin")
async def save_admin(request: Request):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    form = await request.form()
    requested_name = str(form.get("device_name", config["device_name"])).strip() or "avp-py"
    device_name = slugify(requested_name)[:63].strip("-") or "avp-py"
    changes = {"device_name": device_name}
    result = set_device_hostname(device_name)
    if result.ok:
        message = (
            f"Nom d'appareil appliqué. Nouvelle adresse : "
            f"http://{device_name}.local:8000"
        )
    else:
        changes.pop("device_name")
        message = f"Impossible de modifier le nom d'hôte : {result.output}"
    new_password = str(form.get("new_password", "")).strip()
    if new_password:
        changes["admin_password_hash"] = hash_password(new_password)
    config = update_config(changes)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "config": config, "message": message},
    )


@app.get("/thumbs/{name}")
def thumbnail(request: Request, name: str):
    config = load_config()
    if login_redirect := require_login(request, config):
        return login_redirect
    path = THUMB_DIR / Path(name).name
    if not path.exists():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
            '<rect width="320" height="180" fill="#101112"/>'
            '<path d="M132 54l88 36-88 36z" fill="#f0f3f6" opacity=".75"/>'
            "</svg>"
        )
        return Response(svg, media_type="image/svg+xml")
    return FileResponse(path)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "player": player.status(), "network": network.status(), "clock": clock_status()}

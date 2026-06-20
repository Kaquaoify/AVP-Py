#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-${REPO_URL:-https://github.com/CHANGE_ME/AVP-Py.git}}"
INSTALL_DIR="${INSTALL_DIR:-/opt/avp-py/app}"
DATA_DIR="${AVPPY_DATA_DIR:-/var/lib/avp-py}"
RUN_USER="${AVPPY_USER:-${SUDO_USER:-$USER}}"
SERVICE_FILE="/etc/systemd/system/avp-py.service"

if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

echo "Installing AVP-Py for user ${RUN_USER}"

${SUDO} apt-get update
${SUDO} apt-get install -y git python3 python3-venv python3-pip rclone ffmpeg mpv avahi-daemon network-manager
${SUDO} systemctl enable NetworkManager.service
${SUDO} systemctl start NetworkManager.service

if [[ -n "${AVP_HOSTNAME:-}" ]]; then
  ${SUDO} hostnamectl set-hostname "${AVP_HOSTNAME}"
fi

${SUDO} mkdir -p "$(dirname "${INSTALL_DIR}")" "${DATA_DIR}/media" "${DATA_DIR}/thumbnails" "${DATA_DIR}/logs"
${SUDO} chown -R "${RUN_USER}:${RUN_USER}" "$(dirname "${INSTALL_DIR}")" "${DATA_DIR}"

if [[ -d "${INSTALL_DIR}/.git" ]]; then
  git -C "${INSTALL_DIR}" pull --ff-only
else
  git clone "${REPO_URL}" "${INSTALL_DIR}"
fi

python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

${SUDO} usermod -aG audio,video,input,render "${RUN_USER}" || true
{
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/systemctl reboot, /bin/systemctl reboot"
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/nmcli"
} | ${SUDO} tee /etc/sudoers.d/avp-py >/dev/null
${SUDO} chmod 0440 /etc/sudoers.d/avp-py

TMP_SERVICE="$(mktemp)"
sed \
  -e "s|@INSTALL_DIR@|${INSTALL_DIR}|g" \
  -e "s|@DATA_DIR@|${DATA_DIR}|g" \
  -e "s|@RUN_USER@|${RUN_USER}|g" \
  "${INSTALL_DIR}/systemd/avp-py.service" > "${TMP_SERVICE}"
${SUDO} mv "${TMP_SERVICE}" "${SERVICE_FILE}"
${SUDO} systemctl daemon-reload
${SUDO} systemctl disable getty@tty1.service || true
${SUDO} systemctl enable avp-py.service
${SUDO} systemctl restart avp-py.service

echo "AVP-Py is installed."
echo "Open http://$(hostname).local:8000"

#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/avp-py/app}"
DATA_DIR="${AVPPY_DATA_DIR:-/var/lib/avp-py}"
RUN_USER="${AVPPY_USER:-${SUDO_USER:-$USER}}"
SERVICE_FILE="/etc/systemd/system/avp-py.service"

if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

if [[ "${AVP_UPDATE_REEXEC:-0}" != "1" ]]; then
  git -C "${INSTALL_DIR}" pull --ff-only
  export AVP_UPDATE_REEXEC=1
  exec bash "${INSTALL_DIR}/scripts/update.sh"
fi

${SUDO} apt-get update
${SUDO} apt-get install -y network-manager v4l-utils
${SUDO} systemctl enable NetworkManager.service
${SUDO} systemctl start NetworkManager.service
{
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/systemctl reboot, /bin/systemctl reboot"
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/systemctl restart avahi-daemon.service"
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/hostnamectl set-hostname *"
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/nmcli"
} | ${SUDO} tee /etc/sudoers.d/avp-py >/dev/null
${SUDO} chmod 0440 /etc/sudoers.d/avp-py
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

TMP_SERVICE="$(mktemp)"
sed \
  -e "s|@INSTALL_DIR@|${INSTALL_DIR}|g" \
  -e "s|@DATA_DIR@|${DATA_DIR}|g" \
  -e "s|@RUN_USER@|${RUN_USER}|g" \
  "${INSTALL_DIR}/systemd/avp-py.service" > "${TMP_SERVICE}"
${SUDO} mv "${TMP_SERVICE}" "${SERVICE_FILE}"
${SUDO} systemctl daemon-reload
${SUDO} systemctl disable getty@tty1.service || true
${SUDO} systemctl restart avp-py.service

echo "AVP-Py updated and restarted."

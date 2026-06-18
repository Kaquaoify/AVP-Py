#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/avp-py/app}"
RUN_USER="${AVPPY_USER:-${SUDO_USER:-$USER}}"

if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

git -C "${INSTALL_DIR}" pull --ff-only
${SUDO} apt-get update
${SUDO} apt-get install -y network-manager
${SUDO} systemctl enable NetworkManager.service
${SUDO} systemctl start NetworkManager.service
{
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/systemctl reboot, /bin/systemctl reboot"
  echo "${RUN_USER} ALL=NOPASSWD: /usr/bin/nmcli"
} | ${SUDO} tee /etc/sudoers.d/avp-py >/dev/null
${SUDO} chmod 0440 /etc/sudoers.d/avp-py
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"
${SUDO} systemctl restart avp-py.service

echo "AVP-Py updated and restarted."

#!/usr/bin/env bash
# One-time server setup: creates the virtualenv, installs dependencies and
# registers my-todo-app as a systemd service that starts on boot.
# Safe to re-run. Usage: deploy/install.sh [port]   (default port 8000)
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${1:-8000}"
SERVICE=my-todo-app
UNIT_PATH="/etc/systemd/system/${SERVICE}.service"

cd "$APP_DIR"

echo "==> Checking that Python can create virtual environments"
if ! python3 -m venv "$(mktemp -d)/probe" >/dev/null 2>&1; then
  echo "Python can't create virtual environments yet. Install the missing package with:" >&2
  echo "  sudo apt install -y python3-venv" >&2
  exit 1
fi

echo "==> Creating virtualenv and installing dependencies"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --quiet --disable-pip-version-check --upgrade pip
.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt

echo "==> Installing systemd service to ${UNIT_PATH} (needs sudo)"
sed -e "s|@USER@|$(id -un)|g" -e "s|@APP_DIR@|${APP_DIR}|g" -e "s|@PORT@|${PORT}|g" \
  deploy/my-todo-app.service.in | sudo tee "$UNIT_PATH" >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE"
sudo systemctl restart "$SERVICE"

"$APP_DIR/deploy/healthcheck.sh" "$PORT"
echo "==> Done. Open http://$(hostname -I | awk '{print $1}'):${PORT} from your home network."

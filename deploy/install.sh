#!/usr/bin/env bash
# One-time server setup: creates the virtualenv, installs dependencies and
# registers my-todo-app as a systemd service that starts on boot.
# Safe to re-run. Usage: deploy/install.sh [port]
# The port defaults to the one already installed, or 8000 on first install.
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=deploy/common.sh
source "$APP_DIR/deploy/common.sh"

CURRENT_PORT="$(installed_port || true)"
PORT="${1:-${CURRENT_PORT:-8000}}"

cd "$APP_DIR"

echo "==> Checking that port ${PORT} is free"
# Our own running service may already hold the port on a re-install.
if port_in_use "$PORT" && ! { [ "$PORT" = "$CURRENT_PORT" ] && systemctl is-active --quiet "$SERVICE"; }; then
  echo "Port ${PORT} is already used by another program. Pick a free port, for example:" >&2
  echo "  deploy/install.sh $(suggest_free_port)" >&2
  exit 1
fi

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
render_unit "$(id -un)" "$APP_DIR" "$PORT" | sudo tee "$UNIT_PATH" >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE"
sudo systemctl restart "$SERVICE"

"$APP_DIR/deploy/healthcheck.sh" "$PORT"
echo "==> Done. Open http://$(hostname -I | awk '{print $1}'):${PORT} from your home network."

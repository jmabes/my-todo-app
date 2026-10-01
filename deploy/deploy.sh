#!/usr/bin/env bash
# Deploys the latest main: pulls, updates dependencies, restarts the service
# and confirms it is answering. Usage: deploy/deploy.sh
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=deploy/common.sh
source "$APP_DIR/deploy/common.sh"
cd "$APP_DIR"

PORT="$(installed_port || true)"
if [ -z "$PORT" ]; then
  echo "The service isn't installed yet. Run deploy/install.sh first." >&2
  exit 1
fi

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "There are uncommitted changes to tracked files on the server; refusing to deploy." >&2
  echo "Inspect them with: git -C '$APP_DIR' status" >&2
  exit 1
fi

echo "==> Pulling latest main"
git checkout --quiet main
before="$(git rev-parse --short HEAD)"
git pull --ff-only --quiet origin main
after="$(git rev-parse --short HEAD)"
echo "    ${before} -> ${after}"

echo "==> Updating dependencies"
.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt

echo "==> Restarting service (needs sudo)"
sudo systemctl restart "$SERVICE"

"$APP_DIR/deploy/healthcheck.sh" "$PORT"
echo "==> Deployed ${after}"

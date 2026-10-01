#!/usr/bin/env bash
# Waits up to ~15s for the service to be running and for the to-do API to
# answer on localhost. Usage: healthcheck.sh <port>
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=deploy/common.sh
source "$APP_DIR/deploy/common.sh"

PORT="$1"
URL="http://127.0.0.1:${PORT}/api/todos"

# Passes only if the response is this app's to-do list (a JSON array), so
# another program on the same port can't be mistaken for it.
is_todo_api() {
  python3 - "$URL" <<'PY' 2>/dev/null
import json, sys, urllib.request
with urllib.request.urlopen(sys.argv[1], timeout=2) as res:
    sys.exit(0 if isinstance(json.load(res), list) else 1)
PY
}

echo "==> Waiting for the app at ${URL}"
for _ in $(seq 1 30); do
  if systemctl is-active --quiet "$SERVICE" && is_todo_api; then
    echo "    App is up."
    exit 0
  fi
  sleep 0.5
done

echo "The app did not respond. Recent logs:" >&2
journalctl -u "$SERVICE" -n 30 --no-pager >&2 || true
exit 1

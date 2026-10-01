#!/usr/bin/env bash
# Waits up to ~15s for the app to answer on localhost. Usage: healthcheck.sh [port]
set -euo pipefail
PORT="${1:-8000}"
URL="http://127.0.0.1:${PORT}/api/todos"

echo "==> Waiting for the app at ${URL}"
for _ in $(seq 1 30); do
  if python3 -c "import urllib.request,sys; urllib.request.urlopen(sys.argv[1], timeout=2)" "$URL" 2>/dev/null; then
    echo "    App is up."
    exit 0
  fi
  sleep 0.5
done

echo "The app did not respond. Recent logs:" >&2
journalctl -u my-todo-app -n 30 --no-pager >&2 || true
exit 1

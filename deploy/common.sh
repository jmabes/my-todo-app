# Shared helpers for the deploy scripts. Source it; don't run it.

SERVICE=my-todo-app
UNIT_PATH="/etc/systemd/system/${SERVICE}.service"

# Prints the port the installed service listens on, or nothing if not installed.
installed_port() {
  [ -f "$UNIT_PATH" ] && sed -n 's/.*--port \([0-9][0-9]*\).*/\1/p' "$UNIT_PATH" | head -n 1
}

# Succeeds if something is listening on TCP port $1.
port_in_use() {
  [ -n "$(ss -Hltn "sport = :$1")" ]
}

# Prints the first free port from 8001 to 8999.
suggest_free_port() {
  local p
  for p in $(seq 8001 8999); do
    if ! port_in_use "$p"; then
      echo "$p"
      return
    fi
  done
}

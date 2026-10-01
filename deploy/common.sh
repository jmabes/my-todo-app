# Shared helpers for the deploy scripts. Source it; don't run it.

SERVICE=my-todo-app
UNIT_PATH="/etc/systemd/system/${SERVICE}.service"

# Prints the port the installed service listens on, or nothing if not installed.
installed_port() {
  [ -f "$UNIT_PATH" ] && sed -n 's/.*--port \([0-9][0-9]*\).*/\1/p' "$UNIT_PATH" | head -n 1
}

# Prints the user the installed service runs as, or nothing if not installed.
installed_user() {
  [ -f "$UNIT_PATH" ] && sed -n 's/^User=//p' "$UNIT_PATH" | head -n 1
}

# Prints the systemd unit for user $1, app directory $2 and port $3, rendered
# from the template in the checkout.
render_unit() {
  sed -e "s|@USER@|$1|g" -e "s|@APP_DIR@|$2|g" -e "s|@PORT@|$3|g" \
    "$2/deploy/my-todo-app.service.in"
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

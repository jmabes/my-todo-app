# Deploying to a home server

These steps run the app as a systemd service on an Ubuntu server, reachable
from your home network. They were written for Ubuntu 24.04 (Python 3.12).

> **The app has no login.** Anyone who can reach it can read and change your
> to-dos. Keep it on your home network, or reach it remotely through a private
> VPN such as Tailscale. Do not forward a router port to it.

## One-time setup

SSH into the server, then run the commands below. The clone needs no login
because the repository is public; if it is private, the server needs its own
GitHub access (such as a read-only deploy key) first.

```bash
git clone https://github.com/jmabes/my-todo-app.git ~/my-todo-app
~/my-todo-app/deploy/install.sh
```

`install.sh` creates a virtualenv, installs dependencies, and registers the
`my-todo-app` service so it starts on boot. It asks for your sudo password to
install the service. When it finishes it prints the address to open, such as
`http://192.168.1.20:8001`.

The app listens on port 8000 unless you choose another. If that port is
already taken, `install.sh` stops and suggests a free one; run it again with
that port, for example `deploy/install.sh 8001`. The chosen port is saved in
the service, so later runs of `install.sh` and `deploy.sh` reuse it. To move
to a different port later, run `install.sh` with the new port.

If it says Python can't create virtual environments, run
`sudo apt install -y python3-venv` and run `install.sh` again.

If the page doesn't load from your phone but `install.sh` reported the app is
up, the server's firewall may be blocking the port. With Ubuntu's `ufw`:
`sudo ufw allow <port>/tcp`.

## Deploying an update

After a pull request is merged into `main`:

```bash
~/my-todo-app/deploy/deploy.sh
```

It pulls the latest `main`, updates dependencies, restarts the service, and
waits until the app answers on its saved port. If the app fails to start, it prints the recent
logs. The script refuses to run if files in the checkout were edited on the
server, so a deploy never silently overwrites local changes.

## Day-to-day commands

| Task | Command |
| --- | --- |
| Status | `systemctl status my-todo-app` |
| Live logs | `journalctl -u my-todo-app -f` |
| Restart | `sudo systemctl restart my-todo-app` |
| Stop | `sudo systemctl stop my-todo-app` |

## Where the data lives

To-dos are stored in `/var/lib/my-todo-app/todos.db`, outside the git
checkout, so deploys never touch them. To back up, copy that file.

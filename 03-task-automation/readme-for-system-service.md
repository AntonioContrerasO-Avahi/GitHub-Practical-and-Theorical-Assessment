# systemd Timer — Setup & Operations
# =====================================
#
# NOTE: systemd is Linux-only. It does not exist on macOS.
# To test locally on a Mac, use the Docker container from 3.1
# which runs Alpine Linux where these unit files can be deployed.
#
# On a real Linux server, unit files point to your actual repo path:
#   ExecStart:        /Users/antonio.contreras/Desktop/GitHub-Practical-and-Theorical-Assessment/03-task-automation/run_ingest.sh
#   WorkingDirectory: /Users/antonio.contreras/Desktop/GitHub-Practical-and-Theorical-Assessment/03-task-automation
# (swap the Mac path for wherever the repo lives on the Linux host)


# --- Install ---
sudo cp avahi-ingest.service /etc/systemd/system/
sudo cp avahi-ingest.timer   /etc/systemd/system/

# Reload systemd so it picks up the new unit files
sudo systemctl daemon-reload

# Enable + start the TIMER (not the service directly)
sudo systemctl enable --now avahi-ingest.timer


# --- Verify ---

# Is the timer active? When does it fire next?
systemctl status avahi-ingest.timer

# List all timers — shows last/next trigger times
systemctl list-timers avahi-ingest.timer

# Did the last service run succeed?
systemctl status avahi-ingest.service


# --- Logs (the big advantage over cron) ---

# All output from run_ingest.sh, structured and queryable
journalctl -u avahi-ingest.service

# Follow live output during a run
journalctl -u avahi-ingest.service -f

# Only today's runs
journalctl -u avahi-ingest.service --since today

# Only failures
journalctl -u avahi-ingest.service -p err


# --- Manual trigger (test without waiting for 2:30 AM) ---
sudo systemctl start avahi-ingest.service


# --- Disable / remove ---
sudo systemctl disable --now avahi-ingest.timer
sudo rm /etc/systemd/system/avahi-ingest.{service,timer}
sudo systemctl daemon-reload


# --- Testing on macOS via Docker (Alpine Linux container) ---

# Build and enter the container interactively
docker build -t avahi-ingest .
docker run --rm -it avahi-ingest bash

# Inside the container — install systemd (Alpine uses OpenRC by default,
# so for a pure systemd test use a Ubuntu-based image instead):
docker run --rm -it ubuntu:24.04 bash

# Inside Ubuntu container:
apt-get update && apt-get install -y systemd
cp avahi-ingest.service /etc/systemd/system/
cp avahi-ingest.timer   /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now avahi-ingest.timer
systemctl list-timers
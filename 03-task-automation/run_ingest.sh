#!/usr/bin/env bash
# run_ingest.sh — Production wrapper for ingest.py
# Crontab: 30 2 * * * /app/run_ingest.sh
set -euo pipefail

# --- Config ---
PROJECT_DIR="/app"
SCRIPT="$PROJECT_DIR/ingest.py"
LOG_DIR="/var/log/avahi"
LOCK_FILE="/tmp/avahi_ingest.lock"
LOG_FILE="$LOG_DIR/ingest_$(date +%Y-%m-%d).log"

# --- Setup ---
mkdir -p "$LOG_DIR"

# Redirect all output (stdout + stderr) to dated log file
exec >> "$LOG_FILE" 2>&1

echo "========================================"
echo "Run started at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "PID: $$"
echo "========================================"

# --- flock: prevent concurrent runs (Linux native) ---
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "ERROR: Another ingest run is already active (lock: $LOCK_FILE). Exiting." >&2
  exit 1
fi

# --- Run ---
echo "Invoking ingest.py via uv..."
cd "$PROJECT_DIR"
uv run python "$SCRIPT"

EXIT_CODE=$?

echo "----------------------------------------"
echo "Run finished at $(date -u +"%Y-%m-%dT%H:%M:%SZ") — exit code: $EXIT_CODE"
echo ""

exit $EXIT_CODE
#!/usr/bin/env bash
# generate_logs.sh — Simulate 1000 log files with ~20% ERROR probability per line
set -euo pipefail

OUTPUT_DIR="${1:-./logs}"
NUM_FILES=1000
LINES_PER_FILE=20
ERROR_PROBABILITY=20  # percent

mkdir -p "$OUTPUT_DIR"

LEVELS=("INFO" "DEBUG" "WARN" "ERROR")
MESSAGES=(
  "Starting pipeline run"
  "Loading model weights"
  "Processing batch"
  "Evaluating outputs"
  "Writing results to disk"
  "Connection timeout"
  "Unexpected null value"
  "Checkpoint saved"
  "Memory threshold exceeded"
  "Run complete"
)

for i in $(seq 1 $NUM_FILES); do
  log_file="$OUTPUT_DIR/run_$(printf '%04d' $i).log"
  {
    for _ in $(seq 1 $LINES_PER_FILE); do
      roll=$((RANDOM % 100))
      if [[ $roll -lt $ERROR_PROBABILITY ]]; then
        level="ERROR"
      else
        level="${LEVELS[$((RANDOM % 3))]}"  # INFO, DEBUG, WARN only
      fi
      msg="${MESSAGES[$((RANDOM % ${#MESSAGES[@]}))]}"
      timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
      echo "[$timestamp] [$level] $msg"
    done
  } > "$log_file"
done

echo "Generated $NUM_FILES log files in '$OUTPUT_DIR'."
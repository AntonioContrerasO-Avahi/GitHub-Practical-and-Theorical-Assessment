#!/usr/bin/env bash
# count_errors.sh — Count ERROR lines across all .log files in a directory
set -euo pipefail

TARGET_DIR="${1:-.}"

shopt -s nullglob
log_files=("$TARGET_DIR"/*.log)
shopt -u nullglob

if [[ ${#log_files[@]} -eq 0 ]]; then
  echo "No .log files found in '$TARGET_DIR'." >&2
  exit 0
fi

total_errors=0
total_files=${#log_files[@]}

for log_file in "${log_files[@]}"; do
  error_count=$(grep -c "ERROR" "$log_file" || true)
  total_errors=$((total_errors + error_count))
  echo "$(basename "$log_file"): $error_count ERROR(s)"
done

echo "---"
echo "Total: $total_errors ERROR(s) across $total_files file(s)"
echo "Files with errors: $(grep -rl "ERROR" "${log_files[@]}" 2>/dev/null | wc -l) / $total_files"
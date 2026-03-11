#!/usr/bin/env bash
set -euo pipefail

validate_input_file() {
  local file="$1"

  if [[ ! -f "$file" ]]; then
    echo "Error: '$file' is not a regular file." >&2
    return 1
  fi

  if [[ ! -r "$file" ]]; then
    echo "Error: '$file' is not readable." >&2
    return 1
  fi

  if [[ ! -s "$file" ]]; then
    echo "Error: '$file' is empty." >&2
    return 1
  fi

  return 0
}

#!/usr/bin/env bash
# load_env.sh — Safe, sourceable .env loader
# Usage: source load_env.sh && load_env [path/to/.env]

load_env() {
  local env_file="${1:-.env}"

  # --- File checks ---
  if [[ ! -f "$env_file" ]]; then
    echo "load_env: file not found: '$env_file'" >&2
    return 1
  fi

  if [[ ! -r "$env_file" ]]; then
    echo "load_env: permission denied: '$env_file'" >&2
    return 1
  fi

  # Warn if world-readable (permissions like -rw-r--r-- or looser)
  local perms
  perms=$(stat -c "%a" "$env_file" 2>/dev/null || stat -f "%OLp" "$env_file")
  if [[ "${perms: -1}" -gt 0 ]]; then
    echo "load_env: WARNING '$env_file' is world-readable (permissions: $perms). Consider: chmod 600 '$env_file'" >&2
  fi

  # --- Parse and export ---
  local line key value
  local loaded=0 skipped=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip blank lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

    # Validate KEY=VALUE format
    if [[ ! "$line" =~ ^[[:alpha:]_][[:alnum:]_]*= ]]; then
      echo "load_env: skipping malformed line: '$line'" >&2
      continue
    fi

    key="${line%%=*}"
    value="${line#*=}"

    # Strip optional wrapping quotes (' or ")
    if [[ "$value" =~ ^\"(.*)\"$ ]] || [[ "$value" =~ ^\'(.*)\'$ ]]; then
      value="${BASH_REMATCH[1]}"
    fi

    # Do not overwrite already-set variables
    if [[ -v "$key" ]]; then
      echo "load_env: skipping '$key' (already set)" >&2
      (( skipped++ )) || true
      continue
    fi

    export "$key=$value"
    (( loaded++ )) || true

  done < "$env_file"

  echo "load_env: loaded $loaded variable(s) from '$env_file' ($skipped skipped — already set)."
}
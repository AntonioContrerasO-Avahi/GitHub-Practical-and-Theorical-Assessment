#!/usr/bin/env bash
# 2.4 uv Virtual Environments: Speed and Simplicity (~20 min)
set -euo pipefail

pip install --quiet uv

TMPDIR_BASE="$(pwd)/uv-venvs-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"

echo "=== Speed comparison ==="
cd "$TMPDIR_BASE"

echo "python -m venv:"
time python -m venv test-venv

echo ""
echo "uv venv:"
time uv venv test-uv-venv

echo ""
echo "=== Automatic creation with uv ==="
mkdir -p uv-demo && cd uv-demo
uv init --no-workspace
uv add requests
ls -la .venv/

echo ""
echo "=== No activation needed ==="
uv run python -c "import requests; print('Works without activation!')"

echo ""
echo "=== Python version management ==="
echo "uv init --python 3.9   → auto-downloads Python 3.9"
echo "uv init --python 3.11  → auto-downloads Python 3.11"

echo ""
echo "=== Workflow comparison ==="
echo "Traditional:"
echo "  python -m venv .venv && source .venv/bin/activate && pip install requests && python script.py && deactivate"
echo ""
echo "Modern (uv):"
echo "  uv add requests && uv run python script.py"

# Cleanup
rm -rf "$TMPDIR_BASE"

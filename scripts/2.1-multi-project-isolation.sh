#!/usr/bin/env bash
# 2.1 Multi-Project Environment Isolation (~25 min)
set -euo pipefail

pip install --quiet uv

# ── Install Python versions with uv ───────────────────────────────────────
uv python install 3.9
uv python install 3.11
echo "Installed Python versions:"
uv python list

# ── Project Alpha (Python 3.9, Django 3.2) ────────────────────────────────
BASE_DIR="$(pwd)"
mkdir -p "$BASE_DIR/projects/alpha"
cd "$BASE_DIR/projects/alpha"
uv init --python 3.9 --no-workspace
uv add Django==3.2.0 psycopg2-binary pytest
echo "Alpha Python version:"
uv run python --version

# ── Project Beta (Python 3.11, Django 4.2) ────────────────────────────────
mkdir -p "$BASE_DIR/projects/beta"
cd "$BASE_DIR/projects/beta"
uv init --python 3.11 --no-workspace
uv add Django==4.2.0 psycopg2-binary pytest
echo "Beta Python version:"
uv run python --version

# ── Shell aliases (add to ~/.zshrc or ~/.bashrc) ──────────────────────────
echo ""
echo "Add these aliases to your shell config:"
echo "  alias alpha='cd $BASE_DIR/projects/alpha && uv run python --version'"
echo "  alias beta='cd $BASE_DIR/projects/beta && uv run python --version'"

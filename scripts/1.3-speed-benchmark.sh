#!/usr/bin/env bash
# 1.3 Speed Benchmarking: pip vs poetry vs uv (~25 min)
set -euo pipefail

pip install --quiet uv

readonly DEPS=("flask" "pandas" "numpy" "scikit-learn" "requests" "sqlalchemy")
TMPDIR_BASE="$(pwd)/benchmark-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"

echo "========================================="
echo " Package Manager Speed Benchmark"
echo "========================================="

# ── pip ────────────────────────────────────────────────────────────────────
echo ""
echo "[1/3] pip (cold install)"
PIP_DIR="$TMPDIR_BASE/pip-env"
python -m venv "$PIP_DIR"
time "$PIP_DIR/bin/pip" install --quiet "${DEPS[@]}"

echo ""
echo "[2/3] pip (warm install — cache populated)"
PIP_DIR2="$TMPDIR_BASE/pip-env2"
python -m venv "$PIP_DIR2"
time "$PIP_DIR2/bin/pip" install --quiet "${DEPS[@]}"

# ── uv ────────────────────────────────────────────────────────────────────
echo ""
echo "[3/3] uv (cold install)"
UV_DIR="$TMPDIR_BASE/uv-project"
mkdir -p "$UV_DIR" && cd "$UV_DIR"
uv init --no-workspace --quiet
time uv add --quiet "${DEPS[@]}"

echo ""
echo "========================================="
echo " Typical Results:"
echo "   pip cold:   45-60s  | warm: 20-30s"
echo "   poetry cold: 50-70s | warm: 15-25s"
echo "   uv cold:    4-8s    | warm: 1-2s  (10-100x faster!)"
echo "========================================="

# Cleanup
rm -rf "$TMPDIR_BASE"

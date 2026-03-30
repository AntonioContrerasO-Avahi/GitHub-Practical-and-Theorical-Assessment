#!/usr/bin/env bash
# 2.5 Global vs Isolated Environments (~20 min)
set -euo pipefail

TMPDIR_BASE="$(pwd)/isolation-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"

echo "=== Risk 1: Version Conflicts ==="
# Project A needs Flask 1.1.4, Project B needs Flask 2.3.0
# Global: only ONE version possible!

mkdir -p "$TMPDIR_BASE/project-a" && cd "$TMPDIR_BASE/project-a"
python -m venv .venv && source .venv/bin/activate
pip install --quiet Flask==1.1.4
echo "project-a Flask: $(python -c 'import flask; print(flask.__version__)')"
deactivate

mkdir -p "$TMPDIR_BASE/project-b" && cd "$TMPDIR_BASE/project-b"
python -m venv .venv && source .venv/bin/activate
pip install --quiet Flask==2.3.0
echo "project-b Flask: $(python -c 'import flask; print(flask.__version__)')"
deactivate

echo "Both Flask versions work simultaneously in isolation!"

echo ""
echo "=== Risk 2: System Corruption ==="
echo "Ubuntu's apt uses Python internally."
echo "Global 'sudo pip install' can break system tools."
echo "Example: update-manager broke with newer 'requests' package."
echo "Solution: NEVER use 'sudo pip install'."

echo ""
echo "=== Risk 3: Non-Reproducibility ==="
echo "Dev A installs pandas → gets 1.5.0"
echo "Dev B installs pandas later → gets 2.1.0"
echo "Result: code breaks on Dev B's machine ('works on my machine')"

echo ""
echo "=== Solution: pin versions in requirements.txt ==="
cd "$TMPDIR_BASE/project-a"
source .venv/bin/activate
pip freeze > requirements.txt
echo "requirements.txt created:"
head -5 requirements.txt
deactivate

# Cleanup
rm -rf "$TMPDIR_BASE"

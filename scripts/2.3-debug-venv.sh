#!/usr/bin/env bash
# 2.3 Debugging Broken Virtual Environments (~25 min)
set -euo pipefail

VENV_PATH="${1:-.venv}"

echo "=== Diagnosing virtual environment: $VENV_PATH ==="

# Check Python symlink
if [[ -L "$VENV_PATH/bin/python" ]]; then
    target=$(readlink "$VENV_PATH/bin/python")
    if [[ -f "$target" ]]; then
        echo "OK — symlink valid: $target"
    else
        echo "BROKEN — symlink points to missing file: $target"
    fi
elif [[ -f "$VENV_PATH/bin/python" ]]; then
    echo "OK — python binary exists (not a symlink)"
else
    echo "ERROR — $VENV_PATH/bin/python not found"
fi

# Check pip permissions
if [[ -f "$VENV_PATH/bin/pip" ]]; then
    if [[ -x "$VENV_PATH/bin/pip" ]]; then
        echo "OK — pip is executable"
    else
        echo "BROKEN — pip not executable, fixing permissions..."
        chmod -R u+w "$VENV_PATH"
    fi
fi

echo ""
echo "=== Repair Options ==="
echo ""
echo "1. In-place upgrade (preserves packages, fixes broken symlinks):"
echo "   python -m venv --upgrade $VENV_PATH"
echo ""
echo "2. Fix permissions:"
echo "   chmod -R u+w $VENV_PATH"
echo ""
echo "3. Recreate (preserving packages):"
cat << 'REPAIR'
   .venv/bin/python -m pip freeze > packages.txt
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r packages.txt
REPAIR

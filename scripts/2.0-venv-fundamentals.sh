#!/usr/bin/env bash
# 2.0 Virtual Environment Fundamentals (~15 min)
set -euo pipefail

WORKDIR="$(pwd)/venv-practice"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Create virtual environment
python -m venv myenv

# Activate
source myenv/bin/activate

# Verify isolation
echo "Python path: $(which python)"
echo "Initial packages:"
pip list

# Install package
pip install requests

echo ""
echo "After install:"
pip list | grep requests

# Deactivate and verify isolation
deactivate
echo ""
echo "After deactivate, trying to import requests:"
python -c "import requests; print('requests found')" 2>/dev/null || echo "ModuleNotFoundError — isolation confirmed!"

# Cleanup
cd ..
rm -rf "$WORKDIR"

echo ""
echo "Comparison:"
echo "  venv:      Built-in, lightweight, uses system Python"
echo "  virtualenv: Third-party, works with Python 2 & 3"
echo "  conda:     Heavy (500MB+), manages non-Python deps"
echo "  uv:        40-60x faster, manages Python versions"

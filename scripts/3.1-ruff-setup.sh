#!/usr/bin/env bash
# 3.1 Modern Code Quality with Ruff (~25 min)
set -euo pipefail

TMPDIR_BASE="$(pwd)/ruff-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"

pip install --quiet ruff

# What ruff replaces:
# ✓ black (formatting)
# ✓ flake8 (linting)
# ✓ isort (imports)
# ✗ mypy (type checking — different purpose)

# Configure for Avahi standards
cat > pyproject.toml << 'EOF'
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
  "E", "W",   # pycodestyle
  "F",        # Pyflakes
  "I",        # isort
  "N",        # pep8-naming
  "UP",       # pyupgrade
  "B",        # bugbear
]
ignore = ["E501"]
EOF

# Create a sample file with issues
cat > sample.py << 'EOF'
import os
import sys
import json

x=1
y = 2
z=x+y

def bad_function( a,b ):
    return a+b
EOF

echo "=== Before fix ==="
ruff check sample.py || true

echo ""
echo "=== Auto-fix ==="
ruff check --fix sample.py

echo ""
echo "=== Format ==="
ruff format sample.py

echo ""
echo "=== After fix ==="
cat sample.py

# Cleanup
rm -rf "$TMPDIR_BASE"

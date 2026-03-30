#!/usr/bin/env bash
# 3.5 Advanced Ruff Configuration (~20 min)
set -euo pipefail

TMPDIR_BASE="$(pwd)/advanced-ruff-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"
mkdir -p src tests

# Avahi standard ruff configuration
cat > pyproject.toml << 'EOF'
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]   # Allow unused imports in __init__
"tests/*" = ["S101"]       # Allow assert in tests
EOF

# Sample files
cat > src/__init__.py << 'EOF'
from .service import process  # F401 suppressed here
EOF

cat > src/service.py << 'EOF'
from typing import Optional


def process(value: Optional[str] = None) -> str:
    if value is None:
        return "default"
    return value.strip()
EOF

cat > tests/test_service.py << 'EOF'
from src.service import process


def test_process_none():
    assert process() == "default"  # S101 suppressed in tests


def test_process_value():
    assert process("  hello  ") == "hello"
EOF

pip install --quiet ruff

echo "=== Ruff check with Avahi config ==="
ruff check src/ tests/

echo ""
echo "=== Speed context (50k LOC) ==="
echo "  flake8 + pylint + isort: ~180s"
echo "  ruff:                    ~2s  (90x faster)"

# Cleanup
rm -rf "$TMPDIR_BASE"

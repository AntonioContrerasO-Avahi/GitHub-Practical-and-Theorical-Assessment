#!/usr/bin/env bash
# 3.3 Testing with pytest (~20 min)
set -euo pipefail

TMPDIR_BASE="$(pwd)/pytest-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"

pip install --quiet pytest pytest-cov

mkdir -p src tests

# Application code
cat > src/calculator.py << 'EOF'
def add(a: int, b: int) -> int:
    return a + b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
EOF

touch src/__init__.py

# Tests
cat > tests/test_calculator.py << 'EOF'
import pytest
from src.calculator import add, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_divide():
    assert divide(10, 2) == 5.0
    assert divide(9, 3) == 3.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (5, 3, 8),
    (-2, 2, 0),
    (100, 0, 100),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
EOF

# Configure pytest
cat > pyproject.toml << 'EOF'
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--verbose --cov=src --cov-fail-under=80"
EOF

echo "=== Running pytest with coverage ==="
pytest

# Cleanup
rm -rf "$TMPDIR_BASE"

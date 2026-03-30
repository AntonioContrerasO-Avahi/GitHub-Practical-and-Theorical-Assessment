#!/usr/bin/env bash
# 5. Capstone — Production Project Setup
# Usage: bash scripts/5-capstone.sh <project-name>
set -euo pipefail

apt-get update -qq && apt-get install -y -qq git
pip install --quiet uv
git config --global user.email "test@avahi.com"
git config --global user.name "Avahi Test"

PROJECT_NAME="${1:?Usage: $0 <project-name>}"

echo "=== Bootstrapping production project: $PROJECT_NAME ==="

rm -rf "$PROJECT_NAME"
mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Package management with uv
uv init --no-workspace
git init

# Production + dev dependencies
uv add fastapi uvicorn pydantic
uv add --dev pytest pytest-cov ruff mypy

# Directory structure
mkdir -p "src/$PROJECT_NAME" tests

# Application code
cat > "src/$PROJECT_NAME/__init__.py" << 'EOF'
EOF

cat > "src/$PROJECT_NAME/main.py" << 'EOF'
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
EOF

# Tests
cat > tests/__init__.py << 'EOF'
EOF

cat > tests/test_main.py << EOF
from fastapi.testclient import TestClient
from src.${PROJECT_NAME}.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
EOF

# Configure ruff + pytest
cat > pyproject.toml << 'EOF'
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-fail-under=80"
EOF

# Pre-commit config
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
EOF

# GitHub Actions CI
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install uv
      - run: uv sync --all-extras
      - run: uv run ruff check .
      - run: uv run mypy src/
      - run: uv run pytest
EOF

# .gitignore
cat > .gitignore << 'EOF'
.venv/
__pycache__/
*.pyc
.coverage
htmlcov/
dist/
EOF

# Install and verify
uv sync --all-extras
uv run ruff check .
uv run pytest

echo ""
echo "=== Project '$PROJECT_NAME' is production-ready! ==="
echo "  Package manager : uv"
echo "  Linter/formatter: ruff"
echo "  Type checker    : mypy"
echo "  Tests           : pytest (80%+ coverage gate)"
echo "  Pre-commit      : .pre-commit-config.yaml"
echo "  CI/CD           : .github/workflows/ci.yml"

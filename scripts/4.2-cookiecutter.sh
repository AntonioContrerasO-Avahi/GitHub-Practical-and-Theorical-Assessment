#!/usr/bin/env bash
# 4.2 Cookiecutter (~20 min)
set -euo pipefail

pip install --quiet cookiecutter

TMPDIR_BASE="$(pwd)/cookiecutter-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"

# ── Use an existing template ───────────────────────────────────────────────
# cookiecutter gh:audreyfeldroy/cookiecutter-pypackage  # interactive
# cookiecutter gh:tiangolo/full-stack-fastapi-template  # FastAPI

echo "To use an existing template interactively:"
echo "  cookiecutter gh:audreyfeldroy/cookiecutter-pypackage"
echo ""

# ── Create a minimal custom template ──────────────────────────────────────
mkdir -p my-template/'{{cookiecutter.project_name}}'

cat > my-template/cookiecutter.json << 'EOF'
{
  "project_name": "my-service",
  "author_name": "Avahi Team",
  "python_version": "3.11"
}
EOF

cat > "my-template/{{cookiecutter.project_name}}/README.md" << 'EOF'
# {{cookiecutter.project_name}}

Created by {{cookiecutter.author_name}}
Python {{cookiecutter.python_version}}
EOF

cat > "my-template/{{cookiecutter.project_name}}/pyproject.toml" << 'EOF'
[project]
name = "{{cookiecutter.project_name}}"
requires-python = ">=3.11"
EOF

echo "=== Generating project from custom template ==="
cookiecutter my-template/ --no-input

echo ""
echo "Generated files:"
find my-service/ -type f

# Cleanup
rm -rf "$TMPDIR_BASE"

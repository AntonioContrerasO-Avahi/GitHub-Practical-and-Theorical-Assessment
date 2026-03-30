#!/usr/bin/env bash
# 4.3 Copier (~20 min)
set -euo pipefail

apt-get update -qq && apt-get install -y -qq git
git config --global user.email "test@avahi.com"
git config --global user.name "Avahi Test"

pip install --quiet copier

TMPDIR_BASE="$(pwd)/copier-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"

# ── Create a Git-versioned template ───────────────────────────────────────
mkdir my-copier-template && cd my-copier-template
git init --quiet

cat > copier.yml << 'EOF'
project_name:
  type: str
  default: my-service
  help: Name of the project

author:
  type: str
  default: Avahi Team
EOF

mkdir -p '{{project_name}}'

cat > '{{project_name}}/README.md' << 'TMPL'
# {{project_name}}

Author: {{author}}
TMPL

git add .
git commit --quiet -m "v1.0"
git tag v1.0

echo "Template v1.0 created."

# ── Generate a project ────────────────────────────────────────────────────
cd "$TMPDIR_BASE"
copier copy my-copier-template/ my-project --defaults

echo ""
echo "Generated project:"
cat my-project/README.md

# ── Evolve the template ───────────────────────────────────────────────────
cd my-copier-template

cat >> '{{project_name}}/README.md' << 'TMPL'

## Quick Start
```bash
uv sync && uv run python -m {{project_name}}
```
TMPL

git add .
git commit --quiet -m "v1.1 — add quick start"
git tag v1.1

echo ""
echo "Template updated to v1.1."

# ── Update existing project ───────────────────────────────────────────────
cd "$TMPDIR_BASE/my-project"
git init --quiet && git add . && git commit --quiet -m "initial"
copier update --defaults

echo ""
echo "After copier update:"
cat README.md

# Cleanup
rm -rf "$TMPDIR_BASE"

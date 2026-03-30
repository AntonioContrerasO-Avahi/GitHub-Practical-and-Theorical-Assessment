#!/usr/bin/env bash
# 3.4 Production PEP 8 Checker — Pre-commit Hook (~20 min)
set -euo pipefail

apt-get update -qq && apt-get install -y -qq git

TMPDIR_BASE="$(pwd)/pre-commit-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"
git init --quiet

# ── Option 1: Manual pre-commit hook ──────────────────────────────────────
pip install --quiet ruff

cat > .git/hooks/pre-commit << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

apt-get update -qq && apt-get install -y -qq git

mapfile -t staged_files < <(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
[[ ${#staged_files[@]} -eq 0 ]] && exit 0

echo "Running ruff on staged Python files..."
if ruff check "${staged_files[@]}" --quiet; then
    echo "✓ ruff passed"
else
    echo "✗ ruff failed — fix with: ruff check --fix ."
    exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
echo "Manual pre-commit hook installed."

# ── Option 2: pre-commit framework ────────────────────────────────────────
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
EOF
echo ".pre-commit-config.yaml created."

# Test the hook
cat > bad_code.py << 'EOF'
import os
import sys
x=1
y=2
EOF

git add bad_code.py
echo ""
echo "=== Testing hook with bad code ==="
git commit -m "test" 2>&1 || echo "Hook blocked the commit as expected!"

# Cleanup
rm -rf "$TMPDIR_BASE"

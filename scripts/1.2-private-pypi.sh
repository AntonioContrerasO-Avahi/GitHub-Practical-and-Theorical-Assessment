#!/usr/bin/env bash
# 1.2 Private PyPI Repository Configuration (~30 min)
# NOTE: Replace YOUR_USERNAME and YOUR_TOKEN with real credentials before running.
set -euo pipefail

# ── pip configuration ──────────────────────────────────────────────────────
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
extra-index-url = https://pypi.avahi.internal/simple/
trusted-host = pypi.avahi.internal
EOF

cat > ~/.netrc << 'EOF'
machine pypi.avahi.internal
login YOUR_USERNAME
password YOUR_TOKEN
EOF
chmod 600 ~/.netrc

echo "pip.conf written to ~/.pip/pip.conf"
echo "Credentials written to ~/.netrc (chmod 600)"

# ── poetry configuration ───────────────────────────────────────────────────
# poetry config repositories.avahi https://pypi.avahi.internal/simple/
# poetry config http-basic.avahi YOUR_USERNAME YOUR_TOKEN

# ── uv configuration ───────────────────────────────────────────────────────
# export UV_INDEX_avahi_internal_USERNAME=YOUR_USERNAME
# export UV_INDEX_avahi_internal_PASSWORD=YOUR_TOKEN

echo "Poetry and uv commands are commented out — fill in credentials and uncomment."

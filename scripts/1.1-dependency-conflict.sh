#!/usr/bin/env bash
# 1.1 Dependency Conflict Resolution (~25 min)
set -euo pipefail

WORKDIR="$(pwd)/conflict-resolution"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"
python -m venv .venv
source .venv/bin/activate

pip install Flask==2.3.0 flask-marshmallow==0.14.0

# Step 1: Identify conflict
echo "--- Attempting to install marshmallow==3.20.0 ---"
pip install marshmallow==3.20.0 || echo "ERROR: flask-marshmallow 0.14.0 requires marshmallow<3.14"

# Step 2: Research compatible versions
pip show flask-marshmallow
pip index versions flask-marshmallow 2>/dev/null || true

# Step 3: Find solution — flask-marshmallow 0.15.0+ supports marshmallow 3.x
pip install flask-marshmallow==0.15.0 marshmallow==3.20.0
pip freeze > requirements.txt

echo "--- requirements.txt ---"
cat requirements.txt

deactivate

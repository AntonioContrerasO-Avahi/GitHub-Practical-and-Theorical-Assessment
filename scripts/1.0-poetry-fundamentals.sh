#!/usr/bin/env bash
# 1.0 Poetry Fundamentals (~15 min)
set -euo pipefail

pip install --quiet poetry

WORKDIR="$(pwd)/poetry-basics"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Step 1: Initialize Poetry project
poetry init --no-interaction --name "my-service"

# Step 2: Add dependencies
poetry add requests                   # Production dependency
poetry add --group dev pytest black   # Dev-only dependencies

# Step 3: Examine generated files
cat pyproject.toml
cat poetry.lock

# Step 4: Understand commands
# After cloning a repo:
poetry install          # Reads poetry.lock (exact versions)

# Adding NEW package:
# poetry add fastapi    # Updates pyproject.toml + poetry.lock

# Upgrading packages:
# poetry update         # Re-resolves ALL dependencies
# poetry update requests  # Update just one package

# Step 5: Run commands
poetry run python -c "import requests; print(requests.__version__)"
# poetry shell  # Activates virtual environment (interactive)

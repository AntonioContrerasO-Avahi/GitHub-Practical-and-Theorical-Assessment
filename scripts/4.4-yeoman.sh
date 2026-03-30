#!/usr/bin/env bash
# 4.4 Yeoman (~15 min)
# Prerequisites: Node.js and npm must be installed
set -euo pipefail

# Install Yeoman globally
npm install -g yo

# Install a generator (example: webapp)
npm install -g generator-webapp

echo "=== Using a Yeoman generator ==="
echo "Command: yo webapp"
echo "(run interactively — not executed here to avoid prompts)"
echo ""

echo "=== Generator naming convention ==="
echo "Generators are npm packages named 'generator-*'"
echo "Examples:"
echo "  npm install -g generator-webapp  → yo webapp"
echo "  npm install -g generator-react   → yo react"
echo "  npm install -g generator-node    → yo node"
echo ""

echo "=== Hypothetical Avahi generator ==="
echo "  npm install -g generator-avahi-service  → yo avahi-service"
echo ""

echo "=== When to use Yeoman ==="
echo "  Best for: JavaScript/frontend scaffolding"
echo "  NOT recommended for: Python backends (use Copier instead)"

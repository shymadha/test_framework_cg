#!/bin/bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)

echo "Running pre-commit checks..."
pre-commit run --all-files || true

echo "Fixing imports with isort..."
isort "$ROOT_DIR"

echo "Running ruff lint (with fixes)..."
ruff check "$ROOT_DIR" --fix --unsafe-fixes

echo "Running ruff formatter..."
ruff format "$ROOT_DIR"

echo "Formatting complete ✅"
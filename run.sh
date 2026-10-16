#!/usr/bin/env bash
set -euo pipefail

echo "Checking environment for vc-yc-extractor..."
uv sync --extra dev
uv run pytest -o pythonpath=.
echo "Environment ready!"
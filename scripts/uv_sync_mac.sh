#!/usr/bin/env bash
set -euo pipefail

PY_BIN="${PY_BIN:-python3.11}"

if [ ! -d .venv ]; then
  uv venv .venv --python "$PY_BIN"
fi
uv sync --python "$PY_BIN" --extra dev --extra serve --extra mac

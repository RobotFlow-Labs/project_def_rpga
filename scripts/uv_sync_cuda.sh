#!/usr/bin/env bash
set -euo pipefail

PY_BIN="${PY_BIN:-python3.11}"

if [ ! -d .venv ]; then
  uv venv .venv --python "$PY_BIN"
fi
uv sync --python "$PY_BIN" --extra dev --extra serve --extra cuda

cat <<'EOF'
CUDA note:
- On Linux GPU hosts, install the matching PyTorch CUDA wheel into the uv environment if the default wheel is CPU-only.
- Example:
  uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cu124 torch torchvision
- Install the detector stack with uv as well:
  uv pip install --python .venv/bin/python mmengine mmdet mmcv
EOF

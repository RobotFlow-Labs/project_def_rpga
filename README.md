# DEF-RPGA

Paper-backed ANIMA module for physical adversarial camouflage generation using 3D Gaussian Splatting.

> Paper: [arXiv:2507.01367](https://arxiv.org/abs/2507.01367)
> Upstream code reference: [TRLou/R-PGA](https://github.com/TRLou/R-PGA)

## Environment

- Package manager: `uv`
- Python: `3.11`
- Local mac bootstrap:

```bash
bash scripts/uv_sync_mac.sh
```

- Linux / CUDA bootstrap:

```bash
bash scripts/uv_sync_cuda.sh
```

## Main entrypoints

```bash
uv run def-rpga-check-assets --config configs/foundation.toml
uv run python -m anima_def_rpga.serve
uv run pytest
```

# PRD-02: Core Model

> Module: DEF-RPGA | Priority: P0
> Depends on: PRD-01
> Status: ⬜ Not started

## Objective
The module can load a reconstructed Gaussian scene, isolate the target surface, and optimize SH0 camouflage under the PGA loss stack.

## Context (from paper)
PGA is not a conventional classifier; its "model" is an attack state over a 3DGS scene. The paper optimizes only color-bearing Gaussian coefficients while preserving geometry, adds mask-based composition, enforces cross-view consistency, and uses a min-max background perturbation to avoid non-robust features.

Paper references:
- §4.1, Eq. (2-8)
- §4.2.1 Cross-viewpoint consistency
- §4.2.2 Min-max optimization
- §4.2.3 NPS and primary-color regularization

## Acceptance Criteria
- [ ] A Gaussian scene loader exposes means, scales, quaternions, opacity, SH0, and frozen higher-order coefficients.
- [ ] The optimizer updates SH0 only and leaves geometry untouched.
- [ ] Mutual-occlusion and self-occlusion controls are implemented as configurable consistency losses / constraints.
- [ ] Background max-step optimization (`sigma`) is implemented with an `L_inf` budget and mask exclusion.
- [ ] EoT, NPS, and primary-color regularization terms are implemented and individually testable.
- [ ] Test: `uv run pytest tests/test_core_attack.py -v` passes.
- [ ] Benchmark: on a reference fixture scene, attack loss decreases over a short optimization run.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/scene/gaussian_state.py` | Canonical in-memory Gaussian scene representation | §3 / §4.1 | ~220 |
| `src/anima_def_rpga/scene/checkpoint_loader.py` | Loader for 3DGS / GIR checkpoints | §4.1 | ~180 |
| `src/anima_def_rpga/attack/masking.py` | SAM-backed or mask-file backed target isolation | Eq. (3-4) | ~140 |
| `src/anima_def_rpga/attack/regularizers.py` | consistency, NPS, color, EoT utilities | §4.2 | ~220 |
| `src/anima_def_rpga/attack/background_minmax.py` | `sigma` update loop with `L_inf` clamp | Eq. (9) | ~160 |
| `src/anima_def_rpga/attack/optimizer.py` | SH0 attack loop and checkpointing | Eq. (6-11) | ~260 |
| `configs/attack.toml` | Attack hyperparameters and toggles | §4.2 | ~120 |
| `tests/test_core_attack.py` | Unit tests for losses and optimizer mechanics | — | ~180 |

## Architecture Detail (from paper)

### Inputs
- `GaussianState`
  - `means: Tensor[G, 3]`
  - `scales: Tensor[G, 3]`
  - `quats: Tensor[G, 4]`
  - `opacity: Tensor[G, 1]`
  - `sh0: Tensor[G, 3]`
  - `sh_rest: Tensor[G, K, 3]`
- `RenderedBatch.rgb: Tensor[B, 3, H, W]`
- `MaskBatch.mask: Tensor[B, 1, H, W]`
- `DetectorTargets.gt_boxes: list[Tensor[N_i, 4]]`

### Outputs
- `AttackStepState`
  - `loss_total: Tensor[]`
  - `loss_det: Tensor[]`
  - `loss_nps: Tensor[]`
  - `loss_color: Tensor[]`
  - `sigma: Tensor[B, 3, H, W]`
- `OptimizedCamouflage`
  - updated `sh0`
  - immutable scene geometry

### Algorithm
```python
# Paper Eq. (6-11)
for step in range(num_steps):
    rendered = render_views(scene, view_batch)
    mask = build_target_mask(rendered, prompts_or_masks)
    sigma = maximize_background_loss(rendered, mask, detector, eps)
    composite = rendered.rgb + sigma * (1 - mask)
    loss = (
        detection_loss(composite, gt_boxes)
        + lambda_consistency * consistency_loss(scene)
        + lambda_nps * nps_loss(composite, printable_colors)
        + lambda_color * primary_color_loss(composite, mask, palette)
        + lambda_eot * eot_loss(composite)
    )
    update(scene.sh0, loss)
```

## Dependencies
```toml
torch = ">=2.1"
torchvision = ">=0.16"
segment-anything = ">=1.0"
numpy = ">=1.26"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| Scene checkpoint | scene-dependent | `/mnt/forge-data/models/def_rpga/scenes/<scene_id>/` | build from capture |
| Mask prompts or precomputed masks | per view | `/mnt/forge-data/datasets/def_rpga/masks/` | generate locally |
| Detector checkpoint | varies | `/mnt/forge-data/models/def_rpga/detectors/` | model-zoo download |

## Test Plan
```bash
uv run pytest tests/test_core_attack.py -v
uv run python -m anima_def_rpga.attack.optimizer --config configs/attack.toml --dry-run
```

## References
- Paper: §4.1, §4.2.1, §4.2.2, §4.2.3
- Reference impl: `R-PGA/train_rel_attack_hpcm.py`, `R-PGA/utils/main_utils.py`
- Depends on: PRD-01
- Feeds into: PRD-03, PRD-04

# PRD-03: Inference

> Module: DEF-RPGA | Priority: P0
> Depends on: PRD-01, PRD-02
> Status: ⬜ Not started

## Objective
Given a scene checkpoint and a benchmark view grid, the module can render, score, and export PGA camouflage artifacts without entering training mode.

## Context (from paper)
The paper evaluates the optimized camouflage across multi-view renderings and physical deployments. The inference path therefore includes view sampling, compositing, detector scoring, and export of printable camouflage assets.

Paper references:
- §4.1 rendering and detector path
- §5.2 digital experiments
- §5.3 physical experiments

## Acceptance Criteria
- [ ] A view sampler can generate the paper protocol grid for digital evaluation and arbitrary custom views for real captures.
- [ ] An inference runner renders composite images, calls the detector, and returns per-view attack summaries.
- [ ] Export utilities can emit texture maps, mesh-linked color payloads, and sticker-sheet previews.
- [ ] CLI entrypoints exist for `render`, `score`, and `export`.
- [ ] Test: `uv run pytest tests/test_inference_pipeline.py -v` passes.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/rendering/view_sampler.py` | Build paper-compliant viewpoint grids | §5.1 | ~140 |
| `src/anima_def_rpga/rendering/render_session.py` | Batched rendering/compositing interface | §4.1 | ~180 |
| `src/anima_def_rpga/detectors/mmdet.py` | Detector adapter returning per-view loss/boxes | §4.1 / §5.1 | ~200 |
| `src/anima_def_rpga/inference/pipeline.py` | End-to-end inference runner | §5.2 / §5.3 | ~220 |
| `src/anima_def_rpga/export/texture_export.py` | Texture / mesh / sticker export | §4.1 / §5.3 | ~180 |
| `src/anima_def_rpga/cli/infer.py` | CLI for render/score/export | — | ~120 |
| `tests/test_inference_pipeline.py` | Inference tests | — | ~150 |

## Architecture Detail (from paper)

### Inputs
- `GaussianState`
- `BenchmarkProtocol`
- `ViewSpec[B]`
- detector config + checkpoint

### Outputs
- `InferenceResult`
  - `rendered_rgb: Tensor[B, 3, H, W]`
  - `detector_boxes: list[Tensor]`
  - `detector_scores: list[Tensor]`
  - `ap50_ready_records: list[dict]`
- exported mesh/texture/sticker bundle

### Algorithm
```python
views = sample_views(protocol)
rendered = render_session(scene, views)
masked = compose_foreground_background(rendered.rgb, rendered.mask, rendered.background)
scores = detector(masked)
summary = summarize_attack(scores, gt_boxes)
export_bundle = export_camouflage(scene, summary)
```

## Dependencies
```toml
torch = ">=2.1"
pillow = ">=10.0"
opencv-python = ">=4.9"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| scene checkpoint | scene-dependent | `/mnt/forge-data/models/def_rpga/scenes/<scene_id>/` | local build |
| benchmark protocol json | tiny | `/mnt/forge-data/datasets/def_rpga/metadata/` | local generation |
| detector checkpoint | varies | `/mnt/forge-data/models/def_rpga/detectors/` | model-zoo download |

## Test Plan
```bash
uv run pytest tests/test_inference_pipeline.py -v
uv run python -m anima_def_rpga.cli.infer render --config configs/attack.toml --dry-run
```

## References
- Paper: §4.1, §5.1, §5.2, §5.3
- Reference impl: `R-PGA/train_func.py`, `R-PGA/detectors/mmdet_wrapper.py`
- Depends on: PRD-01, PRD-02
- Feeds into: PRD-04, PRD-05, PRD-06

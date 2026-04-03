# DEF-RPGA — Pipeline Map

## Planning Basis
- Canonical paper: `papers/2507.01367_PGA.pdf`
- Canonical module identity: `DEF-RPGA`
- Upstream code reference: `TRLou/R-PGA`
- Canonical future package namespace: `src/anima_def_rpga/`

## Paper-to-Code Mapping
| Paper Stage | Paper Ref | Upstream Reference | Planned ANIMA Component | Notes |
|---|---|---|---|---|
| Multi-view capture + reconstruction | §4.1, reconstruction module | `scene/`, `core/gaussian_model_*`, GIR-pretrained checkpoints | `data/capture_index.py`, `scene/checkpoint_loader.py`, `scene/gaussian_state.py` | Input is a scene checkpoint plus per-view metadata, not raw mesh priors. |
| Camera-set rendering | §4.1, Eq. (2) | `core/renderer.py`, `core/renderer_pbr.py`, `core/cameras_simple.py` | `rendering/view_sampler.py`, `rendering/render_session.py` | Must support discrete pitch/azimuth/distance/weather grids. |
| Attack-region masking | §4.1, Eq. (3-4) | SAM integration is implicit in paper, partial mask logic in `train_func.py` | `attack/masking.py` | Compose adversarial foreground with clean background under binary masks. |
| Detection loss | §4.1, Eq. (5-8) | `detectors/mmdet_wrapper.py`, `utils/main_utils.py` | `detectors/mmdet.py`, `attack/detection_loss.py` | White-box Faster R-CNN first, transfer adapters second. |
| Cross-view consistency fixes | §4.2.1 | `core/gaussian_model_pbr.py`, SuGaR-inspired surface alignment | `attack/consistency.py` | Freeze high-order SH and keep surface-aligned Gaussians. |
| Min-max background attack | §4.2.2, Eq. (9) | `train_rel_attack_hpcm.py`, `utils/main_utils.py` | `attack/background_minmax.py`, `attack/optimizer.py` | MVP should implement paper PGA min-max; HPCM is optional later extension. |
| EoT, NPS, primary color regularization | §4.2.2-4.2.3, Eq. (10-11) | `utils/main_utils.py`, `NPSCalculator` | `attack/eot.py`, `attack/regularizers.py` | These are needed for physical deployment fidelity. |
| AP@0.5 evaluation | §5.1-5.3 | `utils/main_utils.py` | `evaluation/ap50.py`, `evaluation/report.py` | Must reproduce digital, 1:1, and 1:24 protocols. |
| Physical export and deployment | §5.3 | `export_albedo_from_ply.py` | `export/texture_export.py`, `export/sticker_layout.py` | Output is printable camouflage, mesh/texture assets, and benchmark reports. |

## Canonical Data Flow
```text
capture images + metadata
  -> scene reconstruction checkpoint
  -> view sampling grid
  -> differentiable render
  -> SAM / explicit mask isolation
  -> clean/adversarial compositing
  -> detector forward + loss
  -> consistency + physical regularizers
  -> optimized SH0 camouflage state
  -> export mesh / texture / sticker sheets
  -> AP@0.5 benchmark + qualitative report
```

## Core Runtime Objects
| Object | Shape / Fields | Planned Module |
|---|---|---|
| `CaptureRecord` | `image_path`, `intrinsics`, `extrinsics`, `weather`, `distance_m`, `pitch_deg`, `azimuth_deg` | `data/schema.py` |
| `GaussianState` | `means[G,3]`, `scales[G,3]`, `quats[G,4]`, `opacity[G,1]`, `sh0[G,3]`, `sh_rest[G,K,3]` | `scene/gaussian_state.py` |
| `ViewSpec` | `distance_m`, `pitch_deg`, `azimuth_deg`, `weather`, `camera_id` | `rendering/view_sampler.py` |
| `RenderedBatch` | `rgb[B,3,H,W]`, `mask[B,1,H,W]`, `background[B,3,H,W]` | `rendering/render_session.py` |
| `DetectorBatchOutput` | `boxes[N,4]`, `scores[N,C]`, `labels[N]` | `detectors/types.py` |
| `AttackStepState` | `loss_total`, `loss_det`, `loss_nps`, `loss_color`, `loss_eot`, `sigma[B,3,H,W]` | `attack/types.py` |
| `EvaluationBundle` | per-view detections, AP summary, qualitative grids | `evaluation/report.py` |

## Module Layout Target
```text
src/anima_def_rpga/
├── config/
├── data/
├── scene/
├── rendering/
├── attack/
├── detectors/
├── inference/
├── evaluation/
├── export/
├── api/
├── ros2/
└── production/
```

## Implementation Decisions
1. Build against paper PGA first, not journal-only `R-PGA` features by default.
2. Keep relightable rendering and HPCM as optional extensions under feature flags once the base paper path reproduces.
3. Treat `src/anima_hachiman/` as stale scaffold code to be replaced during implementation.
4. Make the evaluation protocol first-class. The module is only useful if the CARLA and physical metrics are reproducible.

# DEF-RPGA — Asset Manifest

## Paper
- Title: 3D Gaussian Splatting Driven Multi-View Robust Physical Adversarial Camouflage Generation
- Short name: PGA
- Correct ArXiv: 2507.01367
- Version used for planning: v2, August 13, 2025
- Authors: Tianrui Lou, Xiaojun Jia, Siyuan Liang, Jiawei Liang, Ming Zhang, Yanjun Xiao, Xiaochun Cao
- Correct PDF path: `papers/2507.01367_PGA.pdf`
- Stale local artifact: `papers/2503.16190_PGA-Camouflage.pdf` is unrelated to this project and should not be used for implementation planning.

## Status: ALMOST

The paper, active upstream repo, and benchmark protocol are now identified. The implementation-critical datasets, checkpoints, and scene captures are still missing locally.

## Reference Code
| Asset | Role | Source | Local Path | Status |
|---|---|---|---|---|
| `TRLou/PGA` | Paper repo landing page | https://github.com/TRLou/PGA | `repositories/PGA/README.md` | DONE |
| `TRLou/R-PGA` | Active journal-version codebase referenced by upstream README | https://github.com/TRLou/R-PGA | not vendored | VERIFIED |
| SuGaR regularization | Surface-aligned Gaussian regularization referenced by paper §4.2.1 | https://github.com/Anttwo/SuGaR | not vendored | MISSING |
| SAM weights | Object mask extraction for attack-region isolation | https://github.com/facebookresearch/segment-anything | not downloaded | MISSING |

## Pretrained Weights
| Model | Size / Variant | Source | Path on Server | Status |
|---|---|---|---|---|
| Faster R-CNN | COCO, R50-FPN | MMDetection model zoo | `/mnt/forge-data/models/def_rpga/detectors/faster_rcnn_r50_fpn_1x_coco.pth` | MISSING |
| YOLO-v5 | COCO | official YOLOv5 release | `/mnt/forge-data/models/def_rpga/detectors/yolov5*.pt` | MISSING |
| Mask R-CNN | COCO, R50-FPN | MMDetection model zoo | `/mnt/forge-data/models/def_rpga/detectors/mask_rcnn_r50_fpn_1x_coco.pth` | MISSING |
| Deformable-DETR | COCO | MMDetection model zoo | `/mnt/forge-data/models/def_rpga/detectors/deformable_detr_r50*.pth` | MISSING |
| SAM | ViT-H or ViT-B | Segment Anything | `/mnt/forge-data/models/def_rpga/sam/sam_vit_*.pth` | MISSING |
| 3DGS / GIR scene checkpoint | Per-scene reconstruction artifact | built from capture set | `/mnt/forge-data/models/def_rpga/scenes/<scene_id>/` | MISSING |

## Datasets
| Dataset | Size | Split / Scope | Source | Path | Status |
|---|---|---|---|---|---|
| CARLA digital evaluation set | 1,440 images | 2 weathers x 4 distances x 5 pitch angles x 36 azimuth views | paper §5.1 | `/mnt/forge-data/datasets/def_rpga/carla_eval/` | MISSING |
| Real-vehicle reconstruction set | 282 images | drone capture of Golf Sportsvan for scene fitting | paper §5.1 | `/mnt/forge-data/datasets/def_rpga/real_vehicle_capture/` | MISSING |
| 1:1 physical evaluation set | video-derived image set | drone views after sticker deployment | paper §5.3 | `/mnt/forge-data/datasets/def_rpga/physical_1to1_eval/` | MISSING |
| 1:24 toy-car physical set | multi-view stills at 50 cm and 100 cm | physical transfer benchmark | paper §5.3 | `/mnt/forge-data/datasets/def_rpga/physical_1to24_eval/` | MISSING |
| Scene masks / prompts | per-view foreground masks or point prompts for SAM | attack-region isolation | generated during preprocessing | `/mnt/forge-data/datasets/def_rpga/masks/` | MISSING |
| Camera metadata | extrinsics, intrinsics, weather, distance, pitch, azimuth | reconstruction + evaluation | capture pipeline | `/mnt/forge-data/datasets/def_rpga/metadata/` | MISSING |

## Hyperparameters / Protocol Knobs
| Param | Value | Source |
|---|---|---|
| optimized Gaussian attribute | zero-order SH term only | paper §4.2.1 |
| detection loss | confidence suppression on max-IoU matched box | paper Eq. (6) |
| attack objective | `min_G max_sigma L_det(Idet + sigma * (1 - M))` | paper Eq. (9) |
| background perturbation budget | `||sigma||_inf <= epsilon` | paper Eq. (9) |
| masking method | SAM over rendered views | paper Eq. (3) |
| digital benchmark weather | sunny, cloudy | paper §5.1 |
| digital benchmark distances | 5 m, 10 m, 15 m, 20 m | paper §5.1 |
| digital benchmark pitch angles | 20°, 30°, 40°, 50°, 60° | paper §5.1 |
| digital benchmark azimuth spacing | 10° over 360° | paper §5.1 |
| physical deployment medium | printed stickers | paper §5.1 / §5.3 |

## Upstream Defaults Worth Mirroring During Reproduction
| Param | Value | Source |
|---|---|---|
| optimizer | AdamW | `R-PGA/attack_options_hpcm.py` |
| learning rate | 0.01 | `R-PGA/attack_options_hpcm.py` |
| batch size | 4 | `R-PGA/attack_options_hpcm.py` |
| total steps | 20,000 | `R-PGA/attack_options_hpcm.py` |
| second-stage render step | 30,000 | `R-PGA/attack_options_hpcm.py` |

These are not paper-backed PGA hyperparameters, but they are useful bootstrap values for an implementation plan until the exact training recipe is recovered from supplementary code or ablation reruns.

## Expected Metrics
| Benchmark | Metric | Paper Value | Our Target |
|---|---|---|---|
| Digital, white-box, angle sweep average | AP@0.5 on Faster R-CNN | 6.73 | <= 8.0 |
| Digital, hardest reported angle | AP@0.5 at 60° on Faster R-CNN | 0.00 | <= 2.0 |
| 1:1 real car | AP@0.5 on Faster R-CNN | 25.67 after attack, from 88.48 clean | <= 30.0 |
| Physical transfer | AP@0.5 on toy-car benchmark | PGA is best among compared methods | beat RAUCA on average |

## Compute / Runtime Expectations
| Need | Evidence | Planning Decision |
|---|---|---|
| CUDA-first renderer | upstream depends on diff-gaussian-rasterization, MMDetection, envlight | MVP is CUDA-first |
| CPU fallback | useful for metadata, export, report generation | allow non-rendering CPU mode |
| MLX backend | not supported by paper or upstream | defer to optional future work |

## Immediate Gaps
1. Replace stale `2503.16190` references across scaffold files during implementation.
2. Materialize the CARLA benchmark capture protocol as an indexed dataset.
3. Decide whether to implement pure paper PGA first or feature-gate journal-only `R-PGA` extras such as relightable rendering and HPCM.
4. Acquire or generate scene checkpoints and mask prompts for at least one reference object.

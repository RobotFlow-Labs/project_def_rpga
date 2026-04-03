# DEF-RPGA: 3D Gaussian Splatting Driven Multi-View Robust Physical Adversarial Camouflage Generation — Implementation PRD
## ANIMA Wave-7 Defense Module

**Status:** PRD Suite Ready
**Version:** 0.2
**Date:** 2026-04-03
**Paper:** 3D Gaussian Splatting Driven Multi-View Robust Physical Adversarial Camouflage Generation
**Correct Paper Link:** https://arxiv.org/abs/2507.01367
**Paper Repo Landing:** https://github.com/TRLou/PGA
**Active Upstream Code:** https://github.com/TRLou/R-PGA
**Compute:** CUDA-first, render-heavy
**Functional Name:** DEF-RPGA
**Stack:** Defense

## 1. Executive Summary
DEF-RPGA operationalizes the PGA paper as an ANIMA module for generating multi-view robust physical adversarial camouflage from a 3D Gaussian Splatting scene rather than a hand-authored mesh. The module centers on five paper-faithful behaviors:

1. reconstruct or load a 3DGS scene from multi-view captures,
2. render paper-protocol viewpoints,
3. isolate the target region with masks,
4. optimize only Gaussian color terms with cross-view consistency and min-max background hardening,
5. evaluate transfer and physical robustness with AP@0.5.

The PRD suite in `prds/` and the implementation tasks in `tasks/` break this into a build sequence that preserves the paper’s algorithm while adapting it to ANIMA conventions, typed configs, Docker, and ROS2.

## 2. Paper Verification Status
- [x] Project title matches the intended camouflage paper.
- [x] Correct paper located and downloaded at `papers/2507.01367_PGA.pdf`.
- [x] Repo landing page confirmed at `TRLou/PGA`.
- [x] Active upstream code path confirmed via `TRLou/R-PGA`.
- [x] Local scaffold mismatch identified: `2503.16190` and the existing PDF point to an unrelated paper.
- [ ] Datasets confirmed accessible locally.
- [ ] Detector checkpoints materialized locally.
- [ ] At least one reference scene checkpoint reproduced locally.
- [ ] Metrics reproduced within tolerance.
- **Verdict:** Planning basis verified, implementation assets still incomplete.

## 3. What We Take From The Paper
- 3DGS as the differentiable attack substrate instead of mesh priors.
- Multi-view benchmark protocol: weather, distance, pitch, azimuth coverage.
- SAM-style masking so perturbations only affect the target region.
- SH0-only color optimization over a fixed Gaussian geometry.
- Cross-view consistency improvements against mutual and self-occlusion.
- Min-max background perturbation to filter non-robust features.
- EoT, NPS, and primary-color regularization for physical deployability.
- AP@0.5 reporting for digital and physical evaluation.

## 4. What We Skip
- Any dependence on the stale scaffold identity `HACHIMAN`.
- Simulator-only abstractions that are not required for real-capture workflows.
- Geometry deformation or shape optimization; the paper attacks color, not geometry.
- Journal-only `R-PGA` relightable extras as default MVP behavior unless feature-gated after the paper-faithful path is stable.

## 5. What We Adapt
- Canonical package namespace becomes `anima_def_rpga`.
- Config and asset handling move to TOML + Pydantic settings.
- The paper’s offline pipeline is exposed through CLI, API, Docker, and ROS2 wrappers.
- Evaluation manifests become first-class artifacts under ANIMA.
- Export formats become explicit release artifacts: textures, sticker sheets, reports, provenance.

## 6. Architecture
```text
capture metadata / masks / detector ckpts
  -> scene checkpoint loader
  -> view sampler
  -> differentiable render + compositing
  -> detector loss + min-max background update
  -> SH0 camouflage optimizer
  -> inference/export bundle
  -> AP@0.5 evaluation + qualitative report
```

Canonical future package layout:

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

## 7. Implementation Phases

### Phase 1 — Foundation + Paper-Faithful Core ⬜
- [ ] Normalize module identity and paths around `DEF-RPGA`.
- [ ] Implement settings, schemas, asset checks, and benchmark metadata.
- [ ] Load 3DGS checkpoints and implement the SH0 attack loop.
- [ ] Implement consistency, min-max background, EoT, NPS, and color losses.

### Phase 2 — Inference + Evaluation ⬜
- [ ] Render benchmark view grids and detector-facing composites.
- [ ] Reproduce digital evaluation manifests and AP@0.5 scoring.
- [ ] Add physical-eval manifests for 1:1 and 1:24 workflows.
- [ ] Generate qualitative comparison grids and paper-style reports.

### Phase 3 — ANIMA Interfaces ⬜
- [ ] FastAPI endpoints for optimize / evaluate / export.
- [ ] Docker runtime for CUDA-first execution.
- [ ] ROS2 capture + orchestration bridge.

### Phase 4 — Productionization ⬜
- [ ] Provenance, validation gates, export packaging, release checklist.
- [ ] Benchmark thresholds enforced against paper targets.

## 8. Datasets
| Dataset | Size / Scope | Source | Phase Needed |
|---|---|---|---|
| CARLA digital benchmark | 1,440 views, 2 weathers, 4 distances, 5 pitches, 36 azimuths | paper §5.1 | Phase 2 |
| Real-car reconstruction set | 282 capture images | paper §5.1 | Phase 1 |
| 1:1 real-car eval set | drone-derived views after sticker deployment | paper §5.3 | Phase 2 |
| 1:24 toy-car eval set | multi-view physical benchmark at 50 cm / 100 cm | paper §5.3 | Phase 2 |

## 9. Dependencies on Other Wave Projects
| Needs output from | What it provides |
|---|---|
| None required for MVP | DEF-RPGA is self-contained once datasets and weights exist |

## 10. Success Criteria
- Digital white-box angle-sweep average reaches `AP@0.5 <= 6.73` on Faster R-CNN.
- Hardest reported angle case can approach the paper’s `0.00 AP@0.5` result at 60°.
- Real 1:1 deployment can drive Faster R-CNN AP@0.5 from ~88.48 clean toward <= 30.0.
- Transfer evaluation shows PGA-style degradation on YOLO-v5, Mask R-CNN, and Deformable-DETR.
- Every benchmark run emits reproducible manifests and qualitative grids.

## 11. Risk Assessment
- The local scaffold references the wrong arXiv id and wrong PDF; any implementation that trusts those files will diverge immediately.
- The paper’s public repo is only a landing page; the active codebase is a later journal-version repo that may contain extra features not present in the paper.
- Exact scene-reconstruction steps depend on external GIR / 3DGS tooling and locally captured data.
- Physical performance is highly sensitive to mask quality, printing fidelity, and capture geometry.
- CPU-only environments are not realistic for the main render/attack loop.

## 12. Build Plan
| PRD# | Scope | Status |
|---|---|---|
| [PRD-01](prds/PRD-01-foundation.md) | Foundation & Config | ⬜ |
| [PRD-02](prds/PRD-02-core-model.md) | Core Model | ⬜ |
| [PRD-03](prds/PRD-03-inference.md) | Inference | ⬜ |
| [PRD-04](prds/PRD-04-evaluation.md) | Evaluation | ⬜ |
| [PRD-05](prds/PRD-05-api-docker.md) | API & Docker | ⬜ |
| [PRD-06](prds/PRD-06-ros2-integration.md) | ROS2 Integration | ⬜ |
| [PRD-07](prds/PRD-07-production.md) | Production | ⬜ |

## 13. Task Inventory
- Foundation tasks: `tasks/PRD-0101.md` to `tasks/PRD-0104.md`
- Core tasks: `tasks/PRD-0201.md` to `tasks/PRD-0205.md`
- Inference tasks: `tasks/PRD-0301.md` to `tasks/PRD-0304.md`
- Evaluation tasks: `tasks/PRD-0401.md` to `tasks/PRD-0404.md`
- API tasks: `tasks/PRD-0501.md` to `tasks/PRD-0504.md`
- ROS2 tasks: `tasks/PRD-0601.md` to `tasks/PRD-0604.md`
- Production tasks: `tasks/PRD-0701.md` to `tasks/PRD-0704.md`

## 14. Demo / Readiness Notes
- Minimum meaningful milestone: PRD-01 through PRD-04 complete on one reference scene.
- Demoable milestone: PRD-05 and PRD-06 provide API and capture orchestration on top of a validated benchmark run.

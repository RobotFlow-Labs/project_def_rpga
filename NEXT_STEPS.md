# DEF-RPGA — Execution Ledger

Resume rule: Read this file completely before continuing work.

## 1. Working Rules
- Work only inside `project_def_rpga/`
- Prefix future commits with `[DEF-RPGA]`
- Use `uv` and Python `3.11`
- Build locally on macOS first, then move the train path to CUDA Linux

## 2. Canonical Paper
- **Title**: 3D Gaussian Splatting Driven Multi-View Robust Physical Adversarial Camouflage Generation
- **ArXiv**: 2507.01367
- **Link**: https://arxiv.org/abs/2507.01367
- **Landing Repo**: https://github.com/TRLou/PGA
- **Active Repo**: https://github.com/TRLou/R-PGA
- **Verification status**: Correct PDF ✅ | Active repo ✅ | Local scaffold mismatch identified ✅

## 3. Current Status
- **Date**: 2026-04-03
- **Phase**: PRD-02 core attack scaffold implemented
- **MVP Readiness**: 34%
- **Accomplished**:
  1. Paper-aligned PRD suite and task breakdown created
  2. Correct paper PDF added locally
  3. Autopilot Gate 0 completed: fresh implementation start confirmed
  4. Autopilot preflight found stale scaffold identity and missing serve infra
  5. Python 3.11 `uv` packaging reset for macOS and CUDA handoff
  6. Foundation schemas, asset audit CLI, serve entrypoint, and ANIMA infra files added
  7. PRD-02 core attack scaffold added: mask composition, regularizers, losses, dry-run optimizer
  8. Validation passing: `ruff` clean, `16` tests passing, dry-run optimizer smoke passes
- **Current build focus**:
  1. PRD-03 evaluation and detector integration scaffolding
  2. PRD-04 experiment reporting and metrics surfaces
  3. Real asset ingestion once datasets / checkpoints are mounted
- **Training blockers**:
  1. No local datasets
  2. No detector checkpoints
  3. No reconstructed scene checkpoint

## 4. Data / Model Roots
- macOS datasets root: `/Volumes/AIFlowDev/RobotFlowLabs/datasets/datasets/def_rpga`
- macOS models root: `/Volumes/AIFlowDev/RobotFlowLabs/datasets/models/def_rpga`
- CUDA target: `/mnt/forge-data/datasets/def_rpga` and `/mnt/forge-data/models/def_rpga`

## 5. Next Actions
1. Add PRD-03 detector adapter and evaluation runner scaffolding
2. Add experiment/report artifacts for PRD-04
3. Mount real datasets, scene checkpoints, and detector weights
4. Run `python -m anima_def_rpga.cli.check_assets --config configs/foundation.toml`
5. Re-run the optimizer and evaluation pipeline on the CUDA host

## 6. Session Log
| Date | Agent | What Happened |
|------|-------|---------------|
| 2026-04-03 | ANIMA Research Agent | Project scaffolded |
| 2026-04-03 | Codex | Created PRD suite, corrected paper basis, started autopilot build |
| 2026-04-03 | Codex | Implemented PRD-01/02 scaffold, passing local 3.11 validation, prepared mac/cuda sync scripts |

# PRD-07: Production

> Module: DEF-RPGA | Priority: P1
> Depends on: PRD-01, PRD-04, PRD-05, PRD-06
> Status: ⬜ Not started

## Objective
DEF-RPGA ships with reproducibility controls, export provenance, failure handling, and release gates that make paper-faithful runs auditable.

## Context (from paper)
The paper demonstrates physical deployment on both 1:1 and 1:24 setups. For ANIMA, this must become a controlled artifact pipeline with explicit success thresholds and fallback behavior.

Paper references:
- §5.2 digital evaluation
- §5.3 physical evaluation
- conclusion claims on physical robustness

## Acceptance Criteria
- [ ] Each run emits a provenance bundle with paper version, detector weights, dataset manifest hashes, and config snapshot.
- [ ] Release gates fail if required assets are missing or benchmark thresholds regress materially against paper targets.
- [ ] Export packaging supports sticker sheets, mesh/texture bundle, evaluation report, and JSON metadata.
- [ ] CPU-only and missing-checkpoint failure modes are explicit and non-destructive.
- [ ] Test: `uv run pytest tests/test_production_validation.py -v` passes.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/production/provenance.py` | run metadata and hashing | §5 | ~140 |
| `src/anima_def_rpga/production/validation.py` | release-gate logic | Table 1-4 | ~180 |
| `src/anima_def_rpga/production/release.py` | artifact packaging | §5.3 | ~140 |
| `docs/release_checklist.md` | operator checklist | — | ~80 |
| `tests/test_production_validation.py` | production tests | — | ~120 |

## Architecture Detail (from paper)

### Inputs
- run config
- dataset manifests
- detector checkpoint identifiers
- evaluation outputs

### Outputs
- `RunProvenance`
- `ReleaseBundle`
- `ValidationReport`

### Algorithm
```python
provenance = collect_run_metadata(config, assets, git_state)
validation = compare_against_targets(metrics, targets)
if validation.ok:
    package_release_bundle(exports, provenance, metrics)
```

## Dependencies
```toml
packaging = ">=24.0"
pyyaml = ">=6.0"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| evaluation summaries | run-dependent | `/mnt/forge-data/exports/def_rpga/reports/` | generated |
| exported stickers / meshes | run-dependent | `/mnt/forge-data/exports/def_rpga/releases/` | generated |

## Test Plan
```bash
uv run pytest tests/test_production_validation.py -v
uv run python -m anima_def_rpga.production.validation --config configs/eval.toml --dry-run
```

## References
- Paper: §5.2, §5.3
- Depends on: PRD-01, PRD-04, PRD-05, PRD-06
- Feeds into: release / demo readiness

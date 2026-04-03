# PRD-01: Foundation & Config

> Module: DEF-RPGA | Priority: P0
> Depends on: None
> Status: ⬜ Not started

## Objective
The repo exposes a canonical `anima_def_rpga` package with typed settings, asset validation, dataset schemas, and benchmark metadata for the real PGA paper.

## Context (from paper)
PGA assumes a clean pipeline from multi-view captures to 3DGS reconstruction, view sampling, masking, and evaluation. The paper depends on consistent viewpoint metadata and clean separation between reconstruction, rendering, and attack stages.

Paper references:
- §4.1 Reconstruction / Rendering / Attack modules
- §5.1 Experimental setup and viewpoint protocol

## Acceptance Criteria
- [ ] New planning-aware code uses `anima_def_rpga` as the canonical namespace and does not introduce new `hachiman` references.
- [ ] A `BaseSettings` configuration tree resolves paper id, upstream repos, detector checkpoint paths, dataset roots, and runtime backend settings.
- [ ] Data contracts exist for capture records, scene checkpoints, masks, benchmark view specs, and evaluation manifests.
- [ ] Asset validation explicitly detects the stale local PDF mismatch and missing checkpoint/dataset gaps.
- [ ] Test: `uv run pytest tests/test_foundation_config.py -v` passes.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/config/settings.py` | Pydantic settings for assets, detectors, backend, paths | §4.1 / §5.1 | ~180 |
| `src/anima_def_rpga/data/schema.py` | Typed dataclasses / models for capture, view, eval manifests | §4.1 / §5.1 | ~180 |
| `src/anima_def_rpga/assets/manifest.py` | Asset validation and path auditing | §5.1 | ~140 |
| `src/anima_def_rpga/cli/check_assets.py` | CLI smoke check for assets and repo identity | — | ~80 |
| `configs/foundation.toml` | Default module config | §5.1 | ~80 |
| `tests/test_foundation_config.py` | Foundation and config tests | — | ~150 |

## Architecture Detail (from paper)

### Inputs
- `ProjectConfig`: resolved settings tree
- `CaptureRecord`: metadata for one camera view
- `AssetManifest`: paths for paper PDF, datasets, checkpoints, exports

### Outputs
- `ResolvedPaths`: validated filesystem layout for implementation stages
- `BenchmarkProtocol`: discrete pitch / azimuth / distance / weather grid

### Algorithm
```python
# Foundation does not implement rendering.
# It encodes the paper protocol so later PRDs can execute it consistently.

class ProjectSettings(BaseSettings):
    module_name: str = "DEF-RPGA"
    paper_arxiv: str = "2507.01367"
    package_name: str = "anima_def_rpga"

def build_protocol() -> BenchmarkProtocol:
    return BenchmarkProtocol(
        distances_m=[5, 10, 15, 20],
        pitch_deg=[20, 30, 40, 50, 60],
        azimuth_step_deg=10,
        weather=["sunny", "cloudy"],
    )
```

## Dependencies
```toml
pydantic = ">=2.7"
pydantic-settings = ">=2.2"
rich = ">=13.0"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| Correct paper PDF | ~15 MB | `papers/2507.01367_PGA.pdf` | DONE |
| Detector checkpoints | varies | `/mnt/forge-data/models/def_rpga/detectors/` | model-zoo download |
| CARLA evaluation manifest | small metadata + image roots | `/mnt/forge-data/datasets/def_rpga/carla_eval/` | build locally |

## Test Plan
```bash
uv run pytest tests/test_foundation_config.py -v
uv run python -m anima_def_rpga.cli.check_assets --config configs/foundation.toml
```

## References
- Paper: §4.1, §5.1
- Upstream repo: `TRLou/PGA`, `TRLou/R-PGA`
- Feeds into: PRD-02, PRD-03, PRD-04

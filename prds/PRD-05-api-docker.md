# PRD-05: API & Docker

> Module: DEF-RPGA | Priority: P1
> Depends on: PRD-01, PRD-02, PRD-03, PRD-04
> Status: ⬜ Not started

## Objective
The module can be launched as a containerized service that exposes optimize, evaluate, and export operations for a mounted DEF-RPGA workspace.

## Context (from paper)
The paper itself is offline-research oriented, but ANIMA modules need a stable API surface for orchestration. The service must preserve the paper’s execution path rather than inventing a different algorithmic interface.

Paper references:
- §4 method pipeline
- §5 evaluation / deployment workflow

## Acceptance Criteria
- [ ] FastAPI app exposes `optimize`, `evaluate`, `export`, and `health` endpoints.
- [ ] Service can mount scene checkpoints, datasets, detector weights, and export directories.
- [ ] Docker image supports CUDA-first execution with deterministic environment configuration.
- [ ] Endpoint contracts preserve paper-level abstractions: scene checkpoint, protocol config, detector config, output bundle.
- [ ] Test: `uv run pytest tests/test_api_smoke.py -v` passes.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/api/schemas.py` | request / response models | §4 / §5 | ~140 |
| `src/anima_def_rpga/api/jobs.py` | long-running job orchestration | — | ~180 |
| `src/anima_def_rpga/api/app.py` | FastAPI surface | — | ~160 |
| `docker/Dockerfile` | reproducible runtime image | — | ~120 |
| `docker/docker-compose.yml` | mounted local execution | — | ~80 |
| `.env.example` | runtime knobs | — | ~60 |
| `tests/test_api_smoke.py` | endpoint smoke tests | — | ~120 |

## Architecture Detail (from paper)

### Inputs
- `OptimizeRequest(scene_id, protocol, detector, attack_config)`
- `EvaluateRequest(run_id, benchmark_manifest)`
- `ExportRequest(run_id, export_format)`

### Outputs
- `JobHandle`
- `MetricReport`
- `ExportBundle`

### Algorithm
```python
@app.post("/optimize")
def optimize(req: OptimizeRequest) -> JobHandle:
    return enqueue(run_attack_pipeline, req)

@app.post("/evaluate")
def evaluate(req: EvaluateRequest) -> JobHandle:
    return enqueue(run_evaluation_pipeline, req)
```

## Dependencies
```toml
fastapi = ">=0.111"
uvicorn = ">=0.30"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| scene checkpoints | scene-dependent | mounted under `/mnt/forge-data/models/def_rpga/scenes/` | local build |
| detector weights | varies | mounted under `/mnt/forge-data/models/def_rpga/detectors/` | model-zoo download |
| exports | run-dependent | `/mnt/forge-data/exports/def_rpga/` | generated |

## Test Plan
```bash
uv run pytest tests/test_api_smoke.py -v
docker compose -f docker/docker-compose.yml config
```

## References
- Paper: §4, §5
- Depends on: PRD-01, PRD-02, PRD-03, PRD-04
- Feeds into: PRD-06, PRD-07

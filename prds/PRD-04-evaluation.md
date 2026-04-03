# PRD-04: Evaluation

> Module: DEF-RPGA | Priority: P0
> Depends on: PRD-01, PRD-02, PRD-03
> Status: ⬜ Not started

## Objective
The repo can reproduce the paper’s digital and physical evaluation protocol and emit AP@0.5 summaries with side-by-side qualitative evidence.

## Context (from paper)
PGA’s contribution is measured by multi-view robustness, transferability, and physical deployment performance. The benchmark protocol is therefore part of the method, not a separate afterthought.

Paper references:
- §5.1 Experimental setup
- Table 1 digital benchmark
- Table 2 angle sweep
- Table 3 ablation
- §5.3 physical experiments

## Acceptance Criteria
- [ ] CARLA protocol support covers 2 weather settings, 4 distances, 5 pitch angles, and 36 azimuth views.
- [ ] AP@0.5 computation is implemented for target detectors and exportable as CSV/Markdown.
- [ ] Evaluation harness supports digital, 1:1 real-car, and 1:24 toy-car manifests.
- [ ] Qualitative grids mirror the paper’s comparison style for clean vs attack vs baseline.
- [ ] Test: `uv run pytest tests/test_evaluation_protocol.py -v` passes.
- [ ] Benchmark: evaluation config encodes Table 2 target `AP@0.5 <= 6.73` average on the white-box angle sweep.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/evaluation/ap50.py` | AP@0.5 scorer and per-class reductions | §5.1 | ~180 |
| `src/anima_def_rpga/evaluation/carla_protocol.py` | CARLA benchmark manifest builder | §5.1 / Table 1 | ~160 |
| `src/anima_def_rpga/evaluation/physical_protocol.py` | 1:1 and 1:24 physical benchmark manifests | §5.3 | ~140 |
| `src/anima_def_rpga/evaluation/report.py` | tables, plots, qualitative contact sheets | Table 1-4 | ~220 |
| `configs/eval.toml` | Evaluation targets and thresholds | §5 | ~80 |
| `tests/test_evaluation_protocol.py` | Evaluation tests | — | ~150 |

## Architecture Detail (from paper)

### Inputs
- `InferenceResult` records per view
- ground-truth bounding boxes / labels
- `BenchmarkProtocol`

### Outputs
- `MetricTable`
  - `ap50_by_detector`
  - `ap50_by_pitch`
  - `ap50_by_distance`
  - `physical_summary`
- `QualitativeReport` assets

### Algorithm
```python
records = collect_detector_outputs(...)
metric_table = compute_ap50(records, gt_annotations)
angle_report = aggregate_by_pitch(metric_table)
distance_report = aggregate_by_distance(metric_table)
write_markdown_tables(metric_table, angle_report, distance_report)
build_qualitative_grid(rendered_views, predictions)
```

## Dependencies
```toml
numpy = ">=1.26"
pandas = ">=2.2"
matplotlib = ">=3.8"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| CARLA eval set | 1,440 images + annos | `/mnt/forge-data/datasets/def_rpga/carla_eval/` | local generation |
| Real-car eval set | scene-specific | `/mnt/forge-data/datasets/def_rpga/physical_1to1_eval/` | local capture |
| Toy-car eval set | scene-specific | `/mnt/forge-data/datasets/def_rpga/physical_1to24_eval/` | local capture |

## Test Plan
```bash
uv run pytest tests/test_evaluation_protocol.py -v
uv run python -m anima_def_rpga.evaluation.report --config configs/eval.toml --dry-run
```

## References
- Paper: §5.1, §5.2, §5.3, Table 1-4
- Reference impl: `R-PGA/utils/main_utils.py`
- Depends on: PRD-01, PRD-02, PRD-03
- Feeds into: PRD-05, PRD-07

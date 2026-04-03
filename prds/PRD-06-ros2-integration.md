# PRD-06: ROS2 Integration

> Module: DEF-RPGA | Priority: P1
> Depends on: PRD-01, PRD-03, PRD-05
> Status: ⬜ Not started

## Objective
ROS2 nodes can collect pose-tagged capture frames, invoke DEF-RPGA optimization/evaluation jobs, and publish preview/status outputs for ANIMA robotics workflows.

## Context (from paper)
The paper relies on physically captured multi-view images and drone-based real-world validation. In ANIMA, that capture and evaluation loop should be routable through ROS2 topics and services.

Paper references:
- §5.1 real-car capture
- §5.3 physical deployment and evaluation

## Acceptance Criteria
- [ ] ROS2 message / service definitions exist for capture manifests, optimize requests, and preview outputs.
- [ ] A capture node can subscribe to camera frames and pose data and accumulate a DEF-RPGA-ready manifest.
- [ ] A bridge node can call the API service and publish job status and preview artifacts.
- [ ] Launch files support offline replay from rosbag for regression tests.
- [ ] Test: `uv run pytest tests/test_ros2_bridge.py -v` passes.

## Files to Create

| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_rpga/ros2/messages.py` | ROS-facing dataclasses / schemas | §5.1 / §5.3 | ~120 |
| `src/anima_def_rpga/ros2/capture_node.py` | frame + pose capture node | §5.1 | ~180 |
| `src/anima_def_rpga/ros2/bridge_node.py` | API bridge / job status publishing | — | ~180 |
| `src/anima_def_rpga/ros2/launch/def_rpga.launch.py` | launch definitions | — | ~80 |
| `tests/test_ros2_bridge.py` | ROS2-adjacent tests | — | ~120 |

## Architecture Detail (from paper)

### Inputs
- `sensor_msgs/Image`
- pose topic carrying camera pose / distance / angle metadata
- API job requests

### Outputs
- capture manifest JSON
- optimization / evaluation status topics
- preview image topic or path notification

### Algorithm
```python
capture_node:
    subscribe(image, pose)
    emit CaptureRecord list

bridge_node:
    send capture manifest to DEF-RPGA API
    poll job state
    publish preview + metrics
```

## Dependencies
```toml
rclpy = ">=3.3"
sensor-msgs-py = "*"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| rosbag captures | run-dependent | `/mnt/forge-data/datasets/def_rpga/rosbags/` | local capture |
| preview exports | run-dependent | `/mnt/forge-data/exports/def_rpga/previews/` | generated |

## Test Plan
```bash
uv run pytest tests/test_ros2_bridge.py -v
ros2 launch anima_def_rpga def_rpga.launch.py dry_run:=true
```

## References
- Paper: §5.1, §5.3
- Depends on: PRD-01, PRD-03, PRD-05
- Feeds into: PRD-07

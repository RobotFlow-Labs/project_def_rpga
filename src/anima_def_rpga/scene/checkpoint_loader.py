from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from anima_def_rpga.scene.gaussian_state import GaussianState


def _require_tensor(payload: dict[str, Any], *names: str) -> torch.Tensor:
    for name in names:
        value = payload.get(name)
        if isinstance(value, torch.Tensor):
            return value
    joined = ", ".join(names)
    raise KeyError(f"missing tensor payload for any of: {joined}")


def _normalize_payload(raw: dict[str, Any]) -> dict[str, Any]:
    if "gaussian_state" in raw and isinstance(raw["gaussian_state"], dict):
        return raw["gaussian_state"]
    return raw


def load_gaussian_state(path: str | Path, map_location: str = "cpu") -> GaussianState:
    raw = torch.load(Path(path), map_location=map_location)
    if not isinstance(raw, dict):
        raise TypeError(f"checkpoint must be a mapping, got {type(raw)!r}")
    payload = _normalize_payload(raw)
    return GaussianState(
        means=_require_tensor(payload, "means", "xyz"),
        scales=_require_tensor(payload, "scales", "scaling"),
        quats=_require_tensor(payload, "quats", "rotation"),
        opacity=_require_tensor(payload, "opacity"),
        sh0=_require_tensor(payload, "sh0", "features_dc"),
        sh_rest=_require_tensor(payload, "sh_rest", "features_rest"),
    )


def save_gaussian_state(state: GaussianState, path: str | Path) -> None:
    torch.save({"gaussian_state": state.as_dict()}, Path(path))

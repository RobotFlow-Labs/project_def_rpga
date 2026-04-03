from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class GaussianState:
    means: torch.Tensor
    scales: torch.Tensor
    quats: torch.Tensor
    opacity: torch.Tensor
    sh0: torch.Tensor
    sh_rest: torch.Tensor

    def __post_init__(self) -> None:
        gaussian_count = self.means.shape[0]
        expected_shapes = {
            "means": (gaussian_count, 3),
            "scales": (gaussian_count, 3),
            "quats": (gaussian_count, 4),
            "opacity": (gaussian_count, 1),
            "sh0": (gaussian_count, 3),
        }
        for name, expected in expected_shapes.items():
            tensor = getattr(self, name)
            if tuple(tensor.shape) != expected:
                raise ValueError(f"{name} expected shape {expected}, got {tuple(tensor.shape)}")
        if self.sh_rest.shape[0] != gaussian_count:
            raise ValueError("sh_rest must share gaussian dimension with means")

    @property
    def gaussian_count(self) -> int:
        return int(self.means.shape[0])

    def to(
        self,
        device: str | torch.device,
        dtype: torch.dtype | None = None,
    ) -> GaussianState:
        kwargs = {"device": device}
        if dtype is not None:
            kwargs["dtype"] = dtype
        return GaussianState(
            means=self.means.to(**kwargs),
            scales=self.scales.to(**kwargs),
            quats=self.quats.to(**kwargs),
            opacity=self.opacity.to(**kwargs),
            sh0=self.sh0.to(**kwargs),
            sh_rest=self.sh_rest.to(**kwargs),
        )

    def clone(self) -> GaussianState:
        return GaussianState(
            means=self.means.clone(),
            scales=self.scales.clone(),
            quats=self.quats.clone(),
            opacity=self.opacity.clone(),
            sh0=self.sh0.clone(),
            sh_rest=self.sh_rest.clone(),
        )

    def as_dict(self) -> dict[str, torch.Tensor]:
        return {
            "means": self.means,
            "scales": self.scales,
            "quats": self.quats,
            "opacity": self.opacity,
            "sh0": self.sh0,
            "sh_rest": self.sh_rest,
        }

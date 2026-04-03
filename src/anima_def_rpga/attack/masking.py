from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image


def ensure_mask_channels(mask: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
    if mask.ndim == reference.ndim - 1:
        mask = mask.unsqueeze(-3)
    if mask.ndim != reference.ndim:
        raise ValueError(f"mask dims {mask.ndim} incompatible with reference dims {reference.ndim}")
    if mask.shape[-3] == 1 and reference.shape[-3] == 3:
        mask = mask.expand(*mask.shape[:-3], 3, *mask.shape[-2:])
    return mask.to(dtype=reference.dtype, device=reference.device)


def compose_with_mask(
    adversarial_rgb: torch.Tensor,
    clean_rgb: torch.Tensor,
    mask: torch.Tensor,
) -> torch.Tensor:
    if adversarial_rgb.shape != clean_rgb.shape:
        raise ValueError("adversarial and clean tensors must share shape")
    mask = ensure_mask_channels(mask, adversarial_rgb).clamp(0.0, 1.0)
    return adversarial_rgb * mask + clean_rgb * (1.0 - mask)


def load_mask_image(path: str | Path, image_hw: tuple[int, int] | None = None) -> torch.Tensor:
    mask_image = Image.open(Path(path)).convert("L")
    mask = torch.from_numpy(np.asarray(mask_image, dtype=np.float32) / 255.0)
    mask = mask.unsqueeze(0).unsqueeze(0)
    if image_hw is not None:
        mask = F.interpolate(mask, size=image_hw, mode="nearest")
    return mask


def infer_mask_from_prompt(
    *,
    image_hw: tuple[int, int],
    sam_predictor: object,
    sam_prompt: dict[str, object],
) -> torch.Tensor:
    if not hasattr(sam_predictor, "predict_mask"):
        raise TypeError(
            "sam_predictor must provide a predict_mask("
            "image_hw=..., prompt=...) method"
        )

    predicted = sam_predictor.predict_mask(image_hw=image_hw, prompt=sam_prompt)
    if isinstance(predicted, torch.Tensor):
        mask = predicted.detach().clone().float()
    else:
        mask = torch.as_tensor(predicted, dtype=torch.float32)

    if mask.ndim == 2:
        mask = mask.unsqueeze(0).unsqueeze(0)
    elif mask.ndim == 3:
        mask = mask.unsqueeze(0)

    if mask.shape != (1, 1, *image_hw):
        mask = F.interpolate(mask, size=image_hw, mode="nearest")
    return mask.clamp(0.0, 1.0)


def load_or_infer_mask(
    *,
    image_hw: tuple[int, int],
    mask_path: str | Path | None = None,
    sam_predictor: object | None = None,
    sam_prompt: dict[str, object] | None = None,
) -> torch.Tensor:
    if mask_path is not None:
        return load_mask_image(mask_path, image_hw=image_hw)
    if sam_predictor is not None and sam_prompt is not None:
        return infer_mask_from_prompt(
            image_hw=image_hw,
            sam_predictor=sam_predictor,
            sam_prompt=sam_prompt,
        )
    raise ValueError("either mask_path or both sam_predictor and sam_prompt must be provided")

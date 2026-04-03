from __future__ import annotations

import torch

from anima_def_rpga.attack.masking import ensure_mask_channels


def project_background_sigma(
    sigma: torch.Tensor,
    mask: torch.Tensor,
    epsilon: float,
) -> torch.Tensor:
    background_mask = 1.0 - mask.clamp(0.0, 1.0)
    projected = sigma.clamp(-epsilon, epsilon) * background_mask
    return projected


def apply_background_sigma(
    clean_rgb: torch.Tensor,
    sigma: torch.Tensor,
    mask: torch.Tensor,
    epsilon: float,
) -> torch.Tensor:
    sigma = project_background_sigma(sigma, mask, epsilon)
    sigma_rgb = ensure_mask_channels(sigma, clean_rgb)
    return (clean_rgb + sigma_rgb).clamp(0.0, 1.0)


def expectation_over_transform_loss(losses: torch.Tensor) -> torch.Tensor:
    return losses.float().mean()


def non_printability_score(
    colors: torch.Tensor,
    printable_palette: torch.Tensor,
) -> torch.Tensor:
    flat_colors = colors.reshape(-1, 3)
    palette = printable_palette.reshape(-1, 3).to(
        device=flat_colors.device,
        dtype=flat_colors.dtype,
    )
    distances = torch.cdist(flat_colors, palette, p=2)
    return distances.min(dim=1).values.mean()


def background_palette_centroids(
    background_rgb: torch.Tensor,
    mask: torch.Tensor,
    *,
    centroid_count: int = 3,
) -> torch.Tensor:
    background_mask = (1.0 - ensure_mask_channels(mask, background_rgb))[:, :1]
    pixels = background_rgb.permute(0, 2, 3, 1).reshape(-1, 3)
    keep = background_mask.reshape(-1) > 0.5
    selected = pixels[keep]
    if selected.numel() == 0:
        selected = pixels

    luminance = selected @ selected.new_tensor([0.299, 0.587, 0.114])
    order = torch.argsort(luminance)
    ordered = selected[order]
    chunks = torch.chunk(ordered, min(centroid_count, ordered.shape[0]), dim=0)
    centroids = [chunk.mean(dim=0) for chunk in chunks if chunk.numel() > 0]
    return torch.stack(centroids, dim=0)


def color_regularizer(
    adversarial_rgb: torch.Tensor,
    background_rgb: torch.Tensor,
    mask: torch.Tensor,
    *,
    centroid_count: int = 3,
) -> torch.Tensor:
    centroids = background_palette_centroids(
        background_rgb,
        mask,
        centroid_count=centroid_count,
    )
    foreground = adversarial_rgb.permute(0, 2, 3, 1).reshape(-1, 3)
    distances = torch.cdist(foreground, centroids.to(foreground), p=2)
    return distances.min(dim=1).values.mean()

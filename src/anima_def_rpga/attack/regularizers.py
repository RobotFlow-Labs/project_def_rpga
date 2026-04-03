from __future__ import annotations

import torch
import torch.nn.functional as F

from anima_def_rpga.scene.gaussian_state import GaussianState


def freeze_higher_order_sh(state: GaussianState) -> GaussianState:
    """Paper §4.2.1 keeps higher-order SH terms fixed to avoid self-occlusion drift."""
    state.sh_rest.requires_grad_(False)
    return state


def attack_parameters(
    state: GaussianState,
    *,
    optimize_sh0_only: bool = True,
) -> list[torch.Tensor]:
    state.sh0.requires_grad_(True)
    if optimize_sh0_only:
        freeze_higher_order_sh(state)
        return [state.sh0]

    state.sh_rest.requires_grad_(True)
    return [state.sh0, state.sh_rest]


def consistency_loss(
    current_state: GaussianState,
    reference_state: GaussianState,
) -> torch.Tensor:
    """Paper §4.2.1 consistency proxy that penalizes deviation from the frozen scene state."""
    sh0_term = F.mse_loss(current_state.sh0, reference_state.sh0)
    sh_rest_term = F.mse_loss(current_state.sh_rest, reference_state.sh_rest)
    return sh0_term + sh_rest_term

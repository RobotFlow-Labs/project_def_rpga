from __future__ import annotations

from pathlib import Path

import pytest
import torch
from PIL import Image

from anima_def_rpga.attack.losses import (
    apply_background_sigma,
    background_palette_centroids,
    color_regularizer,
    non_printability_score,
    project_background_sigma,
)
from anima_def_rpga.attack.masking import (
    compose_with_mask,
    ensure_mask_channels,
    load_mask_image,
    load_or_infer_mask,
)
from anima_def_rpga.attack.optimizer import (
    AttackConfig,
    AttackMetrics,
    AttackSettings,
    build_fixture_batch,
    run_attack_optimization,
    save_attack_checkpoint,
)
from anima_def_rpga.attack.regularizers import (
    attack_parameters,
    consistency_loss,
    freeze_higher_order_sh,
)
from anima_def_rpga.scene.checkpoint_loader import load_gaussian_state, save_gaussian_state
from anima_def_rpga.scene.gaussian_state import GaussianState


def build_state() -> GaussianState:
    return GaussianState(
        means=torch.zeros(2, 3),
        scales=torch.ones(2, 3),
        quats=torch.tensor([[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]),
        opacity=torch.ones(2, 1),
        sh0=torch.zeros(2, 3),
        sh_rest=torch.zeros(2, 15, 3),
    )


def test_gaussian_state_round_trip(tmp_path: Path) -> None:
    state = build_state()
    target = tmp_path / "state.pth"
    save_gaussian_state(state, target)
    restored = load_gaussian_state(target)
    assert restored.gaussian_count == 2
    assert torch.equal(restored.sh_rest, state.sh_rest)


def test_ensure_mask_channels_and_compose() -> None:
    clean = torch.zeros(1, 3, 2, 2)
    adv = torch.ones(1, 3, 2, 2)
    mask = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]])
    expanded = ensure_mask_channels(mask, adv)
    assert expanded.shape == adv.shape
    composed = compose_with_mask(adv, clean, mask)
    assert composed[0, 0, 0, 0].item() == 1.0
    assert composed[0, 0, 0, 1].item() == 0.0


def test_load_mask_image(tmp_path: Path) -> None:
    image = Image.new("L", (4, 4), color=255)
    mask_path = tmp_path / "mask.png"
    image.save(mask_path)
    mask = load_mask_image(mask_path, image_hw=(2, 2))
    assert mask.shape == (1, 1, 2, 2)
    assert torch.all(mask == 1.0)


class DummySamPredictor:
    def predict_mask(self, *, image_hw: tuple[int, int], prompt: dict[str, object]) -> torch.Tensor:
        assert prompt["label"] == "vehicle"
        return torch.ones(1, 1, *image_hw)


def test_load_or_infer_mask_supports_prompt_path() -> None:
    mask = load_or_infer_mask(
        image_hw=(3, 5),
        sam_predictor=DummySamPredictor(),
        sam_prompt={"label": "vehicle"},
    )
    assert mask.shape == (1, 1, 3, 5)
    assert torch.all(mask == 1.0)


def test_consistency_freezes_higher_order_sh() -> None:
    state = build_state()
    frozen = freeze_higher_order_sh(state)
    params = attack_parameters(frozen, optimize_sh0_only=True)
    assert params == [state.sh0]
    assert state.sh_rest.requires_grad is False


def test_consistency_loss_is_positive_when_sh_changes() -> None:
    reference = build_state()
    current = build_state()
    current.sh0 = current.sh0 + 0.5
    assert consistency_loss(current, reference).item() > 0.0


def test_project_background_sigma_only_updates_outside_mask() -> None:
    sigma = torch.full((1, 1, 2, 2), 0.5)
    mask = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]])
    projected = project_background_sigma(sigma, mask, epsilon=0.1)
    assert projected[0, 0, 0, 0].item() == 0.0
    assert projected[0, 0, 0, 1].item() == pytest.approx(0.1)


def test_apply_background_sigma_keeps_foreground_pixels_clean() -> None:
    clean = torch.zeros(1, 3, 2, 2)
    sigma = torch.full((1, 1, 2, 2), 0.1)
    mask = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]])
    perturbed = apply_background_sigma(clean, sigma, mask, epsilon=0.2)
    assert perturbed[0, :, 0, 0].tolist() == [0.0, 0.0, 0.0]
    assert perturbed[0, :, 0, 1].tolist() == pytest.approx([0.1, 0.1, 0.1])


def test_non_printability_and_color_losses() -> None:
    colors = torch.tensor([[[0.9, 0.1, 0.1], [0.1, 0.9, 0.1]]])
    palette = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    nps = non_printability_score(colors, palette)
    assert nps.item() < 0.2

    background = torch.zeros(1, 3, 2, 2)
    background[:, 1] = 0.5
    mask = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]])
    centroids = background_palette_centroids(background, mask, centroid_count=2)
    assert centroids.shape[1] == 3

    adversarial = torch.full((1, 3, 2, 2), 0.25)
    color_loss = color_regularizer(adversarial, background, mask)
    assert color_loss.item() >= 0.0


def test_optimizer_updates_only_sh0_and_decreases_loss(tmp_path: Path) -> None:
    reference = build_state()
    batch = build_fixture_batch(batch_size=1, image_hw=(6, 6))
    config = AttackConfig(
        attack=AttackSettings(
            steps=6,
            learning_rate=0.5,
            lambda_consistency=0.05,
            lambda_nps=0.01,
            lambda_color=0.01,
            use_minmax_background=False,
            checkpoint_every=3,
            output_dir=str(tmp_path),
        )
    )
    final_state, metrics = run_attack_optimization(reference, batch, config)
    assert metrics[-1].total_loss < metrics[0].total_loss
    assert not torch.equal(final_state.sh0.detach(), reference.sh0)
    assert torch.equal(final_state.sh_rest, reference.sh_rest)


def test_checkpoint_contains_config_and_step_metadata(tmp_path: Path) -> None:
    state = build_state()
    config = AttackConfig(
        attack=AttackSettings(
            steps=1,
            output_dir=str(tmp_path),
        )
    )
    metrics = AttackMetrics(
        step=3,
        total_loss=1.5,
        target_loss=1.0,
        consistency_loss=0.25,
        nps_loss=0.15,
        color_loss=0.10,
    )
    checkpoint = save_attack_checkpoint(
        output_dir=tmp_path,
        state=state,
        config=config,
        metrics=metrics,
    )
    payload = torch.load(checkpoint, map_location="cpu")
    assert payload["step"] == 3
    assert payload["config"]["attack"]["steps"] == 1
    assert payload["metrics"]["total_loss"] == 1.5
    assert "gaussian_state" in payload

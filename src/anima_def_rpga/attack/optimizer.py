from __future__ import annotations

import argparse
import json
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from pydantic import BaseModel, Field

from anima_def_rpga.attack.losses import (
    apply_background_sigma,
    color_regularizer,
    expectation_over_transform_loss,
    non_printability_score,
    project_background_sigma,
)
from anima_def_rpga.attack.masking import compose_with_mask
from anima_def_rpga.attack.regularizers import attack_parameters, consistency_loss
from anima_def_rpga.scene.gaussian_state import GaussianState


class AttackSettings(BaseModel):
    steps: int = 20_000
    batch_size: int = 4
    learning_rate: float = 1e-2
    sigma_epsilon: float = 8.0 / 255.0
    sigma_step_size: float = 2.0 / 255.0
    lambda_consistency: float = 1.0
    lambda_eot: float = 1.0
    lambda_nps: float = 1.0
    lambda_color: float = 0.25
    optimize_sh0_only: bool = True
    use_minmax_background: bool = True
    checkpoint_every: int = 5
    output_dir: str = "./outputs/attack"
    printable_palette: list[list[float]] = Field(
        default_factory=lambda: [
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


class AttackConfig(BaseModel):
    attack: AttackSettings = Field(default_factory=AttackSettings)


@dataclass(slots=True)
class AttackBatch:
    clean_rgb: torch.Tensor
    target_rgb: torch.Tensor
    mask: torch.Tensor


@dataclass(slots=True)
class AttackMetrics:
    step: int
    total_loss: float
    target_loss: float
    consistency_loss: float
    nps_loss: float
    color_loss: float


def load_attack_config(path: str | Path) -> AttackConfig:
    with Path(path).open("rb") as handle:
        payload = tomllib.load(handle)
    return AttackConfig.model_validate(payload)


def render_sh0_rgb(state: GaussianState, clean_rgb: torch.Tensor) -> torch.Tensor:
    color = torch.sigmoid(state.sh0.mean(dim=0)).view(1, 3, 1, 1)
    return color.expand_as(clean_rgb)


def clone_attack_state(reference_state: GaussianState) -> GaussianState:
    cloned = reference_state.clone()
    cloned.sh0 = cloned.sh0.detach().clone().requires_grad_(True)
    cloned.sh_rest = cloned.sh_rest.detach().clone()
    return cloned


def build_fixture_batch(
    *,
    batch_size: int = 1,
    image_hw: tuple[int, int] = (8, 8),
) -> AttackBatch:
    height, width = image_hw
    clean_rgb = torch.full((batch_size, 3, height, width), 0.2)
    target_rgb = torch.full((batch_size, 3, height, width), 0.85)
    mask = torch.zeros(batch_size, 1, height, width)
    mask[:, :, 2:6, 2:6] = 1.0
    return AttackBatch(clean_rgb=clean_rgb, target_rgb=target_rgb, mask=mask)


def save_attack_checkpoint(
    *,
    output_dir: str | Path,
    state: GaussianState,
    config: AttackConfig,
    metrics: AttackMetrics,
) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"attack-step-{metrics.step:04d}.pt"
    payload = {
        "step": metrics.step,
        "config": config.model_dump(),
        "metrics": asdict(metrics),
        "gaussian_state": state.as_dict(),
    }
    torch.save(payload, target)
    return target


def run_attack_optimization(
    reference_state: GaussianState,
    batch: AttackBatch,
    config: AttackConfig,
) -> tuple[GaussianState, list[AttackMetrics]]:
    current_state = clone_attack_state(reference_state)
    parameters = attack_parameters(
        current_state,
        optimize_sh0_only=config.attack.optimize_sh0_only,
    )
    optimizer = torch.optim.Adam(parameters, lr=config.attack.learning_rate)
    sigma = torch.zeros_like(batch.mask, requires_grad=True)
    palette = torch.tensor(config.attack.printable_palette, dtype=batch.clean_rgb.dtype)
    metrics_log: list[AttackMetrics] = []

    for step in range(config.attack.steps):
        optimizer.zero_grad(set_to_none=True)
        if sigma.grad is not None:
            sigma.grad.zero_()

        adversarial_rgb = render_sh0_rgb(current_state, batch.clean_rgb)
        background_rgb = batch.clean_rgb
        if config.attack.use_minmax_background:
            background_rgb = apply_background_sigma(
                batch.clean_rgb,
                sigma,
                batch.mask,
                config.attack.sigma_epsilon,
            )
        composed = compose_with_mask(adversarial_rgb, background_rgb, batch.mask)

        per_view_losses = ((composed - batch.target_rgb) ** 2).mean(dim=(1, 2, 3))
        target_loss = config.attack.lambda_eot * expectation_over_transform_loss(per_view_losses)
        consistency_term = consistency_loss(current_state, reference_state)
        nps_term = non_printability_score(
            adversarial_rgb.permute(0, 2, 3, 1),
            palette,
        )
        color_term = color_regularizer(adversarial_rgb, batch.clean_rgb, batch.mask)
        total_loss = (
            target_loss
            + config.attack.lambda_consistency * consistency_term
            + config.attack.lambda_nps * nps_term
            + config.attack.lambda_color * color_term
        )
        total_loss.backward()
        optimizer.step()

        if config.attack.use_minmax_background and sigma.grad is not None:
            with torch.no_grad():
                sigma.copy_(
                    project_background_sigma(
                        sigma + config.attack.sigma_step_size * sigma.grad.sign(),
                        batch.mask,
                        config.attack.sigma_epsilon,
                    )
                )

        metrics = AttackMetrics(
            step=step,
            total_loss=float(total_loss.detach().item()),
            target_loss=float(target_loss.detach().item()),
            consistency_loss=float(consistency_term.detach().item()),
            nps_loss=float(nps_term.detach().item()),
            color_loss=float(color_term.detach().item()),
        )
        metrics_log.append(metrics)

        if (
            config.attack.checkpoint_every > 0
            and (step + 1) % config.attack.checkpoint_every == 0
        ):
            save_attack_checkpoint(
                output_dir=config.attack.output_dir,
                state=current_state,
                config=config,
                metrics=metrics,
            )

    return current_state, metrics_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the DEF-RPGA dry-run optimizer loop.")
    parser.add_argument("--config", default="configs/attack.toml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--steps", type=int, default=None)
    return parser


def build_fixture_state() -> GaussianState:
    return GaussianState(
        means=torch.zeros(4, 3),
        scales=torch.ones(4, 3),
        quats=torch.tensor([[1.0, 0.0, 0.0, 0.0]] * 4),
        opacity=torch.ones(4, 1),
        sh0=torch.zeros(4, 3),
        sh_rest=torch.zeros(4, 15, 3),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_attack_config(args.config)
    if args.steps is not None:
        config.attack.steps = args.steps
    if args.dry_run:
        config.attack.learning_rate = 0.25
        config.attack.lambda_consistency = 0.05
        config.attack.lambda_nps = 0.01
        config.attack.lambda_color = 0.01
        config.attack.use_minmax_background = False
        config.attack.checkpoint_every = 0

    state = build_fixture_state()
    batch = build_fixture_batch(batch_size=config.attack.batch_size)
    final_state, metrics = run_attack_optimization(state, batch, config)
    summary = {
        "dry_run": args.dry_run,
        "steps": len(metrics),
        "initial_total_loss": metrics[0].total_loss,
        "final_total_loss": metrics[-1].total_loss,
        "updated_sh0": not torch.equal(final_state.sh0.detach(), state.sh0),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

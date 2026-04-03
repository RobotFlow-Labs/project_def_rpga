from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectSettings(BaseModel):
    name: str = "anima-def-rpga"
    codename: str = "DEF-RPGA"
    package_name: str = "anima_def_rpga"
    functional_name: str = "DEF-RPGA"
    wave: int = 7
    paper_title: str = (
        "3D Gaussian Splatting Driven Multi-View Robust Physical "
        "Adversarial Camouflage Generation"
    )
    paper_arxiv: str = "2507.01367"
    paper_pdf: str = "papers/2507.01367_PGA.pdf"
    stale_paper_pdf: str = "papers/2503.16190_PGA-Camouflage.pdf"
    upstream_repo: str = "https://github.com/TRLou/R-PGA"


class ComputeSettings(BaseModel):
    backend: str = "auto"
    precision: str = "fp32"
    python: str = "3.11"


class DataSettings(BaseModel):
    shared_volume: str = "/Volumes/AIFlowDev/RobotFlowLabs/datasets"
    repos_volume: str = "/Volumes/AIFlowDev/RobotFlowLabs/repos/wave7"
    datasets_root: str = "/Volumes/AIFlowDev/RobotFlowLabs/datasets/datasets/def_rpga"
    models_root: str = "/Volumes/AIFlowDev/RobotFlowLabs/datasets/models/def_rpga"
    exports_root: str = "./outputs"


class HardwareSettings(BaseModel):
    zed2i: bool = True
    unitree_l2_lidar: bool = True
    cobot_xarm6: bool = False


class DetectorSettings(BaseModel):
    default: str = "faster-rcnn"
    faster_rcnn_checkpoint: str = ""
    yolov5_checkpoint: str = ""
    mask_rcnn_checkpoint: str = ""
    deformable_detr_checkpoint: str = ""
    sam_checkpoint: str = ""


class ServeSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8407


class ModuleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANIMA_DEF_RPGA_", extra="forbid")

    project: ProjectSettings = Field(default_factory=ProjectSettings)
    compute: ComputeSettings = Field(default_factory=ComputeSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    hardware: HardwareSettings = Field(default_factory=HardwareSettings)
    detectors: DetectorSettings = Field(default_factory=DetectorSettings)
    serve: ServeSettings = Field(default_factory=ServeSettings)

    @classmethod
    def from_toml(cls, path: str | Path) -> ModuleSettings:
        with Path(path).open("rb") as handle:
            payload = tomllib.load(handle)
        return cls.model_validate(payload)


def load_settings(path: str | Path = "configs/default.toml") -> ModuleSettings:
    return ModuleSettings.from_toml(path)

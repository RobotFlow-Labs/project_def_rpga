from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from anima_def_rpga.config.settings import ModuleSettings


@dataclass(slots=True)
class AssetIssue:
    severity: str
    name: str
    detail: str


@dataclass(slots=True)
class AssetAuditReport:
    environment: str
    issues: list[AssetIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def add(self, severity: str, name: str, detail: str) -> None:
        self.issues.append(AssetIssue(severity=severity, name=name, detail=detail))


def _detect_environment() -> str:
    if Path("/mnt/forge-data").exists():
        return "GPU_SERVER"
    if Path("/Volumes/AIFlowDev").exists():
        return "MAC_LOCAL"
    return "UNKNOWN"


def audit_assets(settings: ModuleSettings, root: str | Path) -> AssetAuditReport:
    project_root = Path(root)
    report = AssetAuditReport(environment=_detect_environment())

    paper_pdf = project_root / settings.project.paper_pdf
    if not paper_pdf.exists():
        report.add("error", "paper_pdf", f"missing correct paper PDF: {paper_pdf}")

    stale_pdf = project_root / settings.project.stale_paper_pdf
    if stale_pdf.exists():
        report.add("warning", "stale_paper_pdf", f"stale unrelated PDF present: {stale_pdf}")

    data_root = Path(settings.data.datasets_root)
    if not data_root.exists():
        report.add("warning", "datasets_root", f"datasets root not found: {data_root}")

    models_root = Path(settings.data.models_root)
    if not models_root.exists():
        report.add("warning", "models_root", f"models root not found: {models_root}")

    faster_rcnn_checkpoint = settings.detectors.faster_rcnn_checkpoint
    if faster_rcnn_checkpoint and not Path(faster_rcnn_checkpoint).exists():
        report.add(
            "warning",
            "faster_rcnn_checkpoint",
            f"checkpoint missing: {faster_rcnn_checkpoint}",
        )

    sam_checkpoint = settings.detectors.sam_checkpoint
    if sam_checkpoint and not Path(sam_checkpoint).exists():
        report.add("warning", "sam_checkpoint", f"checkpoint missing: {sam_checkpoint}")

    return report

from __future__ import annotations

from pathlib import Path

from anima_def_rpga.assets.manifest import audit_assets
from anima_def_rpga.config.settings import load_settings
from anima_def_rpga.data.schema import BenchmarkProtocol, CaptureRecord, paper_benchmark_protocol


def test_identity_uses_correct_paper_and_package() -> None:
    settings = load_settings("configs/foundation.toml")
    assert settings.project.package_name == "anima_def_rpga"
    assert settings.project.paper_arxiv == "2507.01367"
    assert "HACHIMAN" not in settings.project.codename


def test_protocol_matches_paper_grid() -> None:
    protocol = paper_benchmark_protocol()
    assert protocol.distances_m == [5, 10, 15, 20]
    assert protocol.pitch_deg == [20, 30, 40, 50, 60]
    assert protocol.azimuth_step_deg == 10
    assert protocol.total_views() == 1440


def test_schema_round_trip_and_validation() -> None:
    record = CaptureRecord(
        image_path=Path("capture.png"),
        distance_m=5.0,
        pitch_deg=20,
        azimuth_deg=0,
        weather="sunny",
    )
    restored = CaptureRecord.model_validate_json(record.model_dump_json())
    assert restored == record


def test_asset_audit_warns_about_stale_pdf() -> None:
    settings = load_settings("configs/foundation.toml")
    report = audit_assets(settings, ".")
    assert any(issue.name == "stale_paper_pdf" for issue in report.issues)


def test_protocol_iter_views_is_deterministic() -> None:
    protocol = BenchmarkProtocol()
    views = protocol.iter_views()
    assert views[0].camera_id == "sunny_d5_p20_a0"
    assert views[-1].camera_id == "cloudy_d20_p60_a350"

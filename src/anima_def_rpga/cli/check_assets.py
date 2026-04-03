from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from anima_def_rpga.assets.manifest import audit_assets
from anima_def_rpga.config.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit DEF-RPGA local assets and paper alignment."
    )
    parser.add_argument(
        "--config",
        default="configs/foundation.toml",
        help="Path to TOML settings file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = load_settings(args.config)
    report = audit_assets(settings, Path.cwd())
    console = Console()
    table = Table(title=f"DEF-RPGA asset audit ({report.environment})")
    table.add_column("severity")
    table.add_column("name")
    table.add_column("detail")

    if not report.issues:
        table.add_row("ok", "assets", "all required assets present")
    else:
        for issue in report.issues:
            table.add_row(issue.severity, issue.name, issue.detail)

    console.print(table)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

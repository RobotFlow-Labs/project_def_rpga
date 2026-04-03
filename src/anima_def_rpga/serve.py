from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from anima_def_rpga.assets.manifest import audit_assets
from anima_def_rpga.config.settings import load_settings

app = FastAPI(title="DEF-RPGA")


@app.get("/health")
def health() -> dict[str, object]:
    settings = load_settings()
    report = audit_assets(settings, ".")
    return {
        "module": settings.project.codename,
        "paper_arxiv": settings.project.paper_arxiv,
        "assets_ok": report.ok,
        "issue_count": len(report.issues),
        "environment": report.environment,
    }


def main() -> None:
    settings = load_settings()
    uvicorn.run(app, host=settings.serve.host, port=settings.serve.port)


if __name__ == "__main__":
    main()

"""Server-rendered dashboard page route."""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "web" / "templates"
STATIC_DIR = Path(__file__).resolve().parents[2] / "web" / "static"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(include_in_schema=False)


@lru_cache(maxsize=1)
def _asset_versions() -> dict[str, str]:
    css_path = STATIC_DIR / "css" / "dashboard.css"
    js_path = STATIC_DIR / "js" / "dashboard.js"
    return {
        "css": str(int(css_path.stat().st_mtime)) if css_path.exists() else "0",
        "js": str(int(js_path.stat().st_mtime)) if js_path.exists() else "0",
    }


@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    """Render dashboard landing page."""
    app_version = getattr(request.app.state, "app_version", "0.1.0-dev")
    asset_versions = _asset_versions()
    response = templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "app_version": app_version,
            "refresh_seconds": 20,
            "css_asset_version": asset_versions["css"],
            "js_asset_version": asset_versions["js"],
        },
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

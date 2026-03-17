"""System status route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_runtime_config_store, get_settings
from app.api.schemas import SystemStatusResponse
from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings


router = APIRouter()


@router.get("/system/status", response_model=SystemStatusResponse)
def get_system_status(
    request: Request,
    settings: Settings = Depends(get_settings),
    runtime_store: RuntimeConfigStore = Depends(get_runtime_config_store),
) -> SystemStatusResponse:
    """Return basic system/runtime status details for dashboard."""
    app_version = getattr(request.app.state, "app_version", "0.1.0-dev")
    return SystemStatusResponse(
        app_version=app_version,
        exchange_id=settings.exchange_id,
        decision_horizon=settings.decision_horizon,
        llm_provider=settings.llm_provider,
        llm_enabled=settings.llm_enabled,
        llm_configured=settings.llm_configured,
        runtime_config_path=str(runtime_store.path),
        runtime_override_exists=runtime_store.path.exists(),
    )

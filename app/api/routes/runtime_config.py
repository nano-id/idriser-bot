"""Runtime config routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from app.api.dependencies import get_runtime_config_store
from app.api.schemas import RuntimeConfigResponse, RuntimeConfigUpdateRequest
from app.config.runtime_store import RuntimeConfigStore
from app.models.runtime_config import RuntimeConfig


router = APIRouter()


def _build_response(*, config: RuntimeConfig, store: RuntimeConfigStore) -> RuntimeConfigResponse:
    return RuntimeConfigResponse(
        runtime_config=config,
        runtime_config_path=str(store.path),
        runtime_override_exists=store.path.exists(),
    )


@router.get("/runtime-config", response_model=RuntimeConfigResponse)
def get_runtime_config(store: RuntimeConfigStore = Depends(get_runtime_config_store)) -> RuntimeConfigResponse:
    """Return active runtime config."""
    try:
        current = store.load()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return _build_response(config=current, store=store)


@router.put("/runtime-config", response_model=RuntimeConfigResponse)
def update_runtime_config(
    payload: RuntimeConfigUpdateRequest,
    store: RuntimeConfigStore = Depends(get_runtime_config_store),
) -> RuntimeConfigResponse:
    """Update runtime config using allowed RuntimeConfig fields."""
    try:
        current = store.load()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    merged = current.model_dump()
    merged.update(payload.to_update_dict())
    try:
        updated = RuntimeConfig.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(include_context=False, include_url=False),
        ) from exc

    try:
        store.save(updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    return _build_response(config=updated, store=store)


@router.post("/runtime-config/reset", response_model=RuntimeConfigResponse)
def reset_runtime_config(store: RuntimeConfigStore = Depends(get_runtime_config_store)) -> RuntimeConfigResponse:
    """Reset runtime config to defaults derived from Settings."""
    try:
        defaults = store.reset_to_defaults()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return _build_response(config=defaults, store=store)

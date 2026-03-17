"""Health route."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return service liveness status."""
    return HealthResponse()


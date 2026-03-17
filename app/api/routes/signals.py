"""Signal routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_signal_state_store
from app.api.schemas import LatestAISignalsResponse, LatestSignalsResponse
from app.pipeline.signal_state_store import SignalStateStore


router = APIRouter()


@router.get("/signals/latest", response_model=LatestSignalsResponse)
def get_latest_signals(
    signal_store: SignalStateStore = Depends(get_signal_state_store),
) -> LatestSignalsResponse:
    """Return latest aggregate signals from in-memory store."""
    signals = signal_store.get_latest_signals()
    return LatestSignalsResponse(
        source="in_memory_signal_state",
        placeholder=not bool(signals),
        count=len(signals),
        signals=signals,
    )


@router.get("/signals/ai-support/latest", response_model=LatestAISignalsResponse)
def get_latest_ai_signals(
    signal_store: SignalStateStore = Depends(get_signal_state_store),
) -> LatestAISignalsResponse:
    """Return latest AI support signals from in-memory store."""
    ai_signals = signal_store.get_latest_ai_signals()
    return LatestAISignalsResponse(
        source="in_memory_signal_state",
        placeholder=not bool(ai_signals),
        count=len(ai_signals),
        ai_signals=ai_signals,
    )


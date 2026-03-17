"""Paper simulation journal event models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


PaperEventType = Literal["RUN", "OPEN", "CLOSE", "RESET", "RUNNER", "ERROR"]


class PaperEvent(BaseModel):
    """One paper simulation journal event."""

    event_id: str
    timestamp: datetime
    event_type: PaperEventType
    summary: str
    symbol: str | None = None
    trade_id: str | None = None
    pnl_value: float | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

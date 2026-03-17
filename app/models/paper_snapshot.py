"""Paper portfolio equity snapshot model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PaperSnapshot(BaseModel):
    """One portfolio snapshot used for performance metrics."""

    timestamp: datetime
    equity: float = Field(ge=0)
    cash_balance: float = Field(ge=0)
    open_positions: int = Field(ge=0)
    closed_positions: int = Field(ge=0)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

"""Paper portfolio summary model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaperPortfolio(BaseModel):
    """Aggregated paper-trading account state."""

    cash_balance: float = Field(ge=0)
    equity: float = Field(ge=0)
    open_positions: int = Field(ge=0)
    closed_positions: int = Field(ge=0)
    win_count: int = Field(ge=0)
    loss_count: int = Field(ge=0)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_fees_paid: float = 0.0

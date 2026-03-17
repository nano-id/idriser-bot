"""Paper trade model definitions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


PaperTradeStatus = Literal["OPEN", "CLOSED", "CANCELLED"]
PaperTradeSide = Literal["LONG"]


class PaperTrade(BaseModel):
    """Represents one simulated paper trade lifecycle."""

    trade_id: str
    symbol: str
    decision_horizon: str
    status: PaperTradeStatus = "OPEN"
    side: PaperTradeSide = "LONG"
    entry_price: float = Field(gt=0)
    current_price: float | None = Field(default=None, gt=0)
    exit_price: float | None = Field(default=None, gt=0)
    quantity: float = Field(gt=0)
    notional: float = Field(gt=0)
    opened_at: datetime
    closed_at: datetime | None = None
    stop_loss: float | None = Field(default=None, gt=0)
    take_profit: float | None = Field(default=None, gt=0)
    time_stop_at: datetime | None = None
    pnl_pct: float = 0.0
    pnl_value: float = 0.0
    reason_opened: str
    reason_closed: str | None = None
    entry_fee_paid: float = 0.0
    exit_fee_paid: float = 0.0
    total_fees_paid: float = 0.0
    step2_score: float | None = Field(default=None, ge=0, le=100)
    step3_pass: bool | None = None
    ai_support_score: float | None = Field(default=None, ge=0, le=100)

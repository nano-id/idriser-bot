"""Paper simulation performance metrics."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaperMetrics(BaseModel):
    """Aggregated paper trading metrics for dashboard and API."""

    total_closed_trades: int = Field(ge=0)
    win_count: int = Field(ge=0)
    loss_count: int = Field(ge=0)
    win_rate_pct: float = 0.0
    avg_win_value: float = 0.0
    avg_loss_value: float = 0.0
    expectancy_value: float = 0.0
    profit_factor: float | None = None
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    total_fees_paid: float = 0.0
    net_profit_value: float = 0.0
    total_return_pct: float = 0.0
    avg_hold_minutes: float = 0.0
    current_equity: float = Field(ge=0)
    current_cash_balance: float = Field(ge=0)
    open_positions: int = Field(ge=0)

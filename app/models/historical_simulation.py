"""Historical replay simulation result models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.paper_event import PaperEvent
from app.models.paper_metrics import PaperMetrics
from app.models.paper_snapshot import PaperSnapshot
from app.models.paper_trade import PaperTrade


class HistoricalSignalEvaluation(BaseModel):
    """One decision-point evaluation captured during historical replay."""

    timestamp: datetime
    symbol: str
    decision_horizon: str
    price: float | None = Field(default=None, gt=0)
    mean_signal: float = Field(ge=0, le=1)
    bullish_ratio: float = Field(ge=0, le=1)
    stability_score: float = Field(ge=0, le=1)
    latest_breakout: bool = False
    window_complete: bool = False
    fallback_used: bool = False
    step2_score: float | None = Field(default=None, ge=0, le=100)
    step2_pass: bool | None = None
    regime_status: str | None = None
    step3_pass: bool | None = None
    final_selected: bool | None = None
    reject_stage: str | None = None
    reject_reason_summary: str | None = None
    opened_trades: int = Field(default=0, ge=0)
    closed_trades: int = Field(default=0, ge=0)


class HistoricalSimulationResult(BaseModel):
    """Full result payload for one historical replay run."""

    symbol: str
    start_at: datetime
    end_at: datetime
    decision_horizon: str
    snapshot_timeframe: str
    initial_capital: float = Field(gt=0)
    final_equity: float = Field(ge=0)
    final_cash_balance: float = Field(ge=0)
    total_return_pct: float = 0.0
    candles_processed: int = Field(ge=0)
    evaluation_count: int = Field(ge=0)
    selected_signal_count: int = Field(ge=0)
    opened_trade_count: int = Field(ge=0)
    closed_trade_count: int = Field(ge=0)
    force_closed_at_end: bool = False
    runtime_summary: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    metrics: PaperMetrics
    open_trades: list[PaperTrade] = Field(default_factory=list)
    closed_trades: list[PaperTrade] = Field(default_factory=list)
    events: list[PaperEvent] = Field(default_factory=list)
    snapshots: list[PaperSnapshot] = Field(default_factory=list)
    evaluations: list[HistoricalSignalEvaluation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


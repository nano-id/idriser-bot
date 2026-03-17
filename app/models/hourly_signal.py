"""Model for one hourly aggregate signal built from snapshots."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class HourlySignal(BaseModel):
    """Aggregate signal payload computed from a rolling snapshot window."""

    symbol: str
    decision_horizon: str = "1h"
    base_snapshot_timeframe: str = "5m"
    required_snapshots: int = Field(ge=1, default=1)
    window_size: int = Field(ge=1)
    snapshot_count: int = Field(ge=0)
    window_start: datetime | None = None
    window_end: datetime | None = None
    expected_duration_minutes: int = Field(ge=0)
    actual_duration_minutes: int = Field(ge=0)
    mean_signal: float = Field(ge=0, le=1)
    median_signal: float = Field(ge=0, le=1)
    signal_stddev: float = Field(ge=0)
    bullish_ratio: float = Field(ge=0, le=1)
    last_3_slope: float = 0.0
    stability_score: float = Field(ge=0, le=1)
    fallback_used: bool = False
    latest_breakout: bool = False
    step2_score: float | None = Field(default=None, ge=0, le=100)
    step2_pass: bool | None = None
    step2_entry_signal: bool | None = None
    step2_hard_fail: bool | None = None
    step2_summary: str | None = None
    regime_status: str | None = None
    step3_pass: bool | None = None
    regime_score: float | None = Field(default=None, ge=0, le=100)
    step3_fallback_used: bool | None = None
    step3_summary: str | None = None
    step3_unavailable_risk_metrics: list[str] = Field(default_factory=list)
    final_selected: bool | None = None
    reject_stage: str | None = None
    reject_reason_summary: str | None = None
    aggregate_flags: dict[str, bool | int | float | str | None] = Field(default_factory=dict)
    feature_snapshot: dict[str, float | int | str | bool | None] = Field(default_factory=dict)

"""Model for one market snapshot sampled from exchange candles."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    """Per-symbol snapshot derived from a 5m candle sample."""

    symbol: str
    timestamp: datetime
    timeframe: str
    close: float | None = None
    volume: float | None = None
    volume_ratio: float | None = None
    ema_fast: float | None = None
    ema_slow: float | None = None
    ema_slow_slope_pct: float | None = None
    rsi: float | None = None
    macd_hist: float | None = None
    adx: float | None = None
    atr_pct: float | None = None
    bb_width: float | None = None
    recent_high: float | None = None
    breakout: bool = False
    spread_bps: float | None = None
    raw_flags: dict[str, bool | int | float | str | None] = Field(default_factory=dict)

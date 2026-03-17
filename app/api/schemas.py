"""Typed request/response schemas for dashboard API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ai_signal import AISignal
from app.models.historical_simulation import HistoricalSimulationResult
from app.models.hourly_signal import HourlySignal
from app.models.paper_event import PaperEvent
from app.models.paper_metrics import PaperMetrics
from app.models.paper_portfolio import PaperPortfolio
from app.models.paper_snapshot import PaperSnapshot
from app.models.paper_trade import PaperTrade
from app.models.runtime_config import RuntimeConfig


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str = "ok"
    service: str = "dashboard-api"


class SystemStatusResponse(BaseModel):
    """System status response payload."""

    app_version: str
    exchange_id: str
    decision_horizon: str
    llm_provider: str
    llm_enabled: bool
    llm_configured: bool
    runtime_config_path: str
    runtime_override_exists: bool


class RuntimeConfigResponse(BaseModel):
    """Runtime config read/update/reset response."""

    runtime_config: RuntimeConfig
    runtime_config_path: str
    runtime_override_exists: bool


class RuntimeConfigUpdateRequest(BaseModel):
    """Runtime config patch-like request payload."""

    model_config = ConfigDict(extra="forbid")

    llm_provider: str | None = None
    snapshot_timeframe: str | None = None
    snapshot_interval_minutes: int | None = Field(default=None, ge=1, le=120)
    hourly_aggregation_window: int | None = Field(default=None, ge=1, le=500)
    hourly_min_snapshots: int | None = Field(default=None, ge=1, le=500)
    decision_horizon: str | None = None
    supported_decision_horizons: list[str] | None = None
    engine_enabled: bool | None = None
    engine_universe_size: int | None = Field(default=None, ge=1, le=500)
    engine_refresh_seconds: int | None = Field(default=None, ge=5, le=3600)
    engine_include_step2: bool | None = None
    engine_include_step3: bool | None = None
    engine_include_ai_support: bool | None = None
    engine_max_signals: int | None = Field(default=None, ge=1, le=500)
    paper_bot_enabled: bool | None = None
    paper_initial_capital: float | None = Field(default=None, gt=0)
    paper_max_open_positions: int | None = Field(default=None, ge=1, le=500)
    paper_risk_per_trade_pct: float | None = Field(default=None, gt=0, le=1)
    paper_min_signal_score: float | None = Field(default=None, ge=0, le=1)
    paper_require_final_selected: bool | None = None
    paper_require_step2_pass: bool | None = None
    paper_require_step3_pass: bool | None = None
    paper_require_window_complete: bool | None = None
    paper_fixed_stop_loss_pct: float | None = Field(default=None, gt=0, le=1)
    paper_fixed_take_profit_pct: float | None = Field(default=None, gt=0, le=1)
    paper_atr_stop_multiplier: float | None = Field(default=None, gt=0, le=50)
    paper_risk_reward_ratio: float | None = Field(default=None, gt=0, le=50)
    paper_max_hold_minutes: int | None = Field(default=None, ge=1, le=20_000)
    paper_fee_bps: float | None = Field(default=None, ge=0, le=500)
    paper_slippage_bps: float | None = Field(default=None, ge=0, le=500)
    paper_refresh_seconds: int | None = Field(default=None, ge=5, le=3600)
    paper_sync_engine_before_run: bool | None = None
    aggregation_bullish_threshold: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_trend: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_slope: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_rsi: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_macd: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_adx: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_volume: float | None = Field(default=None, ge=0, le=1)
    aggregation_weight_breakout: float | None = Field(default=None, ge=0, le=1)
    aggregation_stability_stddev_cap: float | None = Field(default=None, gt=0, le=2)
    technical_main_timeframe: str | None = None
    technical_confirmation_timeframe: str | None = None
    technical_use_secondary_confirmation: bool | None = None
    technical_pass_threshold: float | None = Field(default=None, ge=0, le=100)
    technical_ohlcv_limit: int | None = Field(default=None, ge=50, le=2000)
    technical_min_ohlcv_rows: int | None = Field(default=None, ge=50, le=2000)
    technical_ma_fast_period: int | None = Field(default=None, ge=2, le=300)
    technical_ma_slow_period: int | None = Field(default=None, ge=3, le=500)
    technical_ma_slope_lookback: int | None = Field(default=None, ge=2, le=200)
    technical_ma_slope_min_pct: float | None = Field(default=None, ge=-0.2, le=0.2)
    technical_ma_slope_good_pct: float | None = Field(default=None, ge=-0.2, le=0.5)
    technical_adx_period: int | None = Field(default=None, ge=2, le=200)
    technical_adx_min: float | None = Field(default=None, ge=0, le=100)
    technical_adx_strong: float | None = Field(default=None, ge=0, le=100)
    technical_rsi_period: int | None = Field(default=None, ge=2, le=200)
    technical_rsi_bullish_min: float | None = Field(default=None, ge=0, le=100)
    technical_rsi_bullish_max: float | None = Field(default=None, ge=0, le=100)
    technical_rsi_extreme: float | None = Field(default=None, ge=0, le=100)
    technical_macd_fast: int | None = Field(default=None, ge=2, le=200)
    technical_macd_slow: int | None = Field(default=None, ge=3, le=400)
    technical_macd_signal: int | None = Field(default=None, ge=2, le=200)
    technical_stoch_period: int | None = Field(default=None, ge=2, le=200)
    technical_stoch_bullish_min: float | None = Field(default=None, ge=0, le=100)
    technical_stoch_overbought: float | None = Field(default=None, ge=0, le=100)
    technical_atr_period: int | None = Field(default=None, ge=2, le=200)
    technical_atr_pct_min: float | None = Field(default=None, ge=0, le=1)
    technical_atr_pct_max: float | None = Field(default=None, ge=0, le=1)
    technical_bbands_period: int | None = Field(default=None, ge=2, le=300)
    technical_bbands_stddev: float | None = Field(default=None, ge=0.1, le=6)
    technical_bb_width_compression_max: float | None = Field(default=None, ge=0, le=2)
    technical_bb_width_expansion_min: float | None = Field(default=None, ge=0, le=2)
    technical_overextended_above_upper_pct: float | None = Field(default=None, ge=0, le=0.5)
    technical_volume_ma_period: int | None = Field(default=None, ge=2, le=400)
    technical_volume_ratio_min: float | None = Field(default=None, ge=0, le=20)
    technical_volume_ratio_strong: float | None = Field(default=None, ge=0, le=50)
    technical_breakout_lookback: int | None = Field(default=None, ge=5, le=300)
    technical_breakout_buffer_pct: float | None = Field(default=None, ge=0, le=0.2)
    technical_pullback_tolerance_pct: float | None = Field(default=None, ge=0, le=0.5)
    technical_missing_critical_penalty: float | None = Field(default=None, ge=0, le=50)
    technical_secondary_confirmation_penalty: float | None = Field(default=None, ge=0, le=50)
    technical_overextended_penalty: float | None = Field(default=None, ge=0, le=50)
    technical_noisy_penalty: float | None = Field(default=None, ge=0, le=50)
    technical_weight_trend: float | None = Field(default=None, ge=0, le=1)
    technical_weight_momentum: float | None = Field(default=None, ge=0, le=1)
    technical_weight_volatility: float | None = Field(default=None, ge=0, le=1)
    technical_weight_volume: float | None = Field(default=None, ge=0, le=1)
    technical_weight_entry: float | None = Field(default=None, ge=0, le=1)
    technical_critical_indicators: list[str] | None = None
    regime_btc_symbol: str | None = None
    regime_timeframe: str | None = None
    regime_ohlcv_limit: int | None = Field(default=None, ge=50, le=2000)
    regime_min_ohlcv_rows: int | None = Field(default=None, ge=50, le=2000)
    regime_btc_ma_fast_period: int | None = Field(default=None, ge=2, le=400)
    regime_btc_ma_slow_period: int | None = Field(default=None, ge=3, le=800)
    regime_btc_slope_lookback: int | None = Field(default=None, ge=2, le=200)
    regime_btc_slope_min_pct: float | None = Field(default=None, ge=-0.3, le=0.3)
    regime_btc_slope_good_pct: float | None = Field(default=None, ge=-0.3, le=0.5)
    regime_adx_period: int | None = Field(default=None, ge=2, le=200)
    regime_adx_min: float | None = Field(default=None, ge=0, le=100)
    regime_adx_strong: float | None = Field(default=None, ge=0, le=100)
    regime_atr_period: int | None = Field(default=None, ge=2, le=200)
    regime_atr_danger_pct: float | None = Field(default=None, ge=0, le=2)
    regime_drawdown_lookback: int | None = Field(default=None, ge=2, le=500)
    regime_drawdown_danger_pct: float | None = Field(default=None, ge=0, le=1)
    regime_breadth_enabled: bool | None = None
    regime_breadth_timeframe: str | None = None
    regime_breadth_symbol_count: int | None = Field(default=None, ge=1, le=300)
    regime_breadth_min_samples: int | None = Field(default=None, ge=1, le=300)
    regime_breadth_fast_period: int | None = Field(default=None, ge=2, le=300)
    regime_breadth_slow_period: int | None = Field(default=None, ge=3, le=500)
    regime_breadth_bullish_ratio: float | None = Field(default=None, ge=0, le=1)
    regime_breadth_bearish_ratio: float | None = Field(default=None, ge=0, le=1)
    regime_derivatives_enabled: bool | None = None
    regime_derivatives_symbol: str | None = None
    regime_funding_abs_max: float | None = Field(default=None, ge=0, le=1)
    regime_derivatives_neutral_score: float | None = Field(default=None, ge=0, le=1)
    regime_fallback_penalty_points: float | None = Field(default=None, ge=0, le=50)
    regime_score_bullish_threshold: float | None = Field(default=None, ge=0, le=100)
    regime_score_neutral_threshold: float | None = Field(default=None, ge=0, le=100)
    regime_allow_neutral: bool | None = None
    regime_veto_if_bearish: bool | None = None
    regime_veto_if_danger: bool | None = None
    regime_weight_trend: float | None = Field(default=None, ge=0, le=1)
    regime_weight_volatility: float | None = Field(default=None, ge=0, le=1)
    regime_weight_breadth: float | None = Field(default=None, ge=0, le=1)
    regime_weight_derivatives: float | None = Field(default=None, ge=0, le=1)
    deepseek_enabled: bool | None = None
    deepseek_shortlist_limit: int | None = Field(default=None, ge=1, le=200)
    deepseek_min_aggregate_score: float | None = Field(default=None, ge=0, le=1)
    deepseek_model: str | None = None
    deepseek_timeout_seconds: int | None = Field(default=None, ge=1, le=120)
    gemini_model: str | None = None
    gemini_timeout_seconds: int | None = Field(default=None, ge=1, le=120)

    def to_update_dict(self) -> dict[str, object]:
        """Return only explicitly provided values."""
        return self.model_dump(exclude_unset=True)


class LatestSignalsResponse(BaseModel):
    """Latest aggregate signal contract for dashboard."""

    source: str
    placeholder: bool
    count: int
    signals: list[HourlySignal]


class LatestAISignalsResponse(BaseModel):
    """Latest AI support signal contract for dashboard."""

    source: str
    placeholder: bool
    count: int
    ai_signals: list[AISignal]


class EngineStatusResponse(BaseModel):
    """Engine loop and latest run status contract."""

    running: bool
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    latest_signal_count: int
    latest_ai_signal_count: int


class EngineActionResponse(BaseModel):
    """Action response for start/stop/run-once commands."""

    ok: bool = True
    action: str
    status: EngineStatusResponse


class PaperStatusResponse(BaseModel):
    """Paper bot status and latest cycle summary."""

    running: bool
    enabled: bool
    refresh_seconds: int
    sync_engine_before_run: bool
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    last_opened_count: int
    last_closed_count: int
    open_trade_count: int
    closed_trade_count: int
    cash_balance: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float


class PaperRunOnceResponse(BaseModel):
    """Run-once response for paper cycle endpoint."""

    ok: bool = True
    opened_count: int
    closed_count: int
    status: PaperStatusResponse


class PaperActionResponse(BaseModel):
    """Paper runner action response."""

    ok: bool = True
    action: str
    status: PaperStatusResponse


class PaperPortfolioResponse(BaseModel):
    """Paper portfolio response model."""

    portfolio: PaperPortfolio


class PaperTradesResponse(BaseModel):
    """Open/closed paper trades response model."""

    count: int
    trades: list[PaperTrade]


class PaperMetricsResponse(BaseModel):
    """Paper simulation metrics response."""

    metrics: PaperMetrics


class PaperEventsResponse(BaseModel):
    """Paper journal event response."""

    count: int
    events: list[PaperEvent]


class PaperSnapshotsResponse(BaseModel):
    """Paper equity snapshot response."""

    count: int
    snapshots: list[PaperSnapshot]


class PaperExportResponse(BaseModel):
    """Full paper simulation export payload."""

    portfolio: PaperPortfolio
    metrics: PaperMetrics
    open_trades: list[PaperTrade]
    closed_trades: list[PaperTrade]
    events: list[PaperEvent]
    snapshots: list[PaperSnapshot]


class HistoricalSimulationRunRequest(BaseModel):
    """Request payload for one historical replay simulation."""

    symbol: str = Field(min_length=3)
    start_at: datetime
    end_at: datetime
    close_open_positions_at_end: bool = True


class HistoricalSimulationResponse(BaseModel):
    """Historical replay simulation response payload."""

    result: HistoricalSimulationResult | None = None

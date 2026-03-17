"""Runtime-overridable config payload for snapshot and aggregation layers."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.utils.timeframe import normalize_timeframe


class RuntimeConfig(BaseModel):
    """Serializable runtime config for dashboard-driven overrides."""

    llm_provider: str = "disabled"
    snapshot_timeframe: str = "5m"
    snapshot_interval_minutes: int = Field(default=5, ge=1, le=120)
    hourly_aggregation_window: int = Field(default=12, ge=1, le=500)
    hourly_min_snapshots: int = Field(default=12, ge=1, le=500)
    decision_horizon: str = "30m"
    supported_decision_horizons: list[str] = Field(
        default_factory=lambda: ["5m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "8h", "12h", "1d"]
    )
    engine_enabled: bool = False
    engine_universe_size: int = Field(default=30, ge=1, le=500)
    engine_refresh_seconds: int = Field(default=30, ge=5, le=3600)
    engine_include_step2: bool = False
    engine_include_step3: bool = False
    engine_include_ai_support: bool = False
    engine_max_signals: int = Field(default=20, ge=1, le=500)
    paper_bot_enabled: bool = False
    paper_initial_capital: float = Field(default=10_000.0, gt=0)
    paper_max_open_positions: int = Field(default=5, ge=1, le=500)
    paper_risk_per_trade_pct: float = Field(default=0.01, gt=0, le=1)
    paper_min_signal_score: float = Field(default=0.42, ge=0, le=1)
    paper_require_final_selected: bool = True
    paper_require_step2_pass: bool = False
    paper_require_step3_pass: bool = False
    paper_require_window_complete: bool = True
    paper_fixed_stop_loss_pct: float | None = Field(default=None, gt=0, le=1)
    paper_fixed_take_profit_pct: float | None = Field(default=None, gt=0, le=1)
    paper_atr_stop_multiplier: float = Field(default=1.5, gt=0, le=50)
    paper_risk_reward_ratio: float = Field(default=2.0, gt=0, le=50)
    paper_max_hold_minutes: int | None = Field(default=None, ge=1, le=20_000)
    paper_fee_bps: float = Field(default=10.0, ge=0, le=500)
    paper_slippage_bps: float = Field(default=5.0, ge=0, le=500)
    paper_refresh_seconds: int = Field(default=60, ge=5, le=3600)
    paper_sync_engine_before_run: bool = True
    aggregation_bullish_threshold: float = Field(default=0.55, ge=0, le=1)
    aggregation_weight_trend: float = Field(default=0.30, ge=0, le=1)
    aggregation_weight_slope: float = Field(default=0.10, ge=0, le=1)
    aggregation_weight_rsi: float = Field(default=0.20, ge=0, le=1)
    aggregation_weight_macd: float = Field(default=0.15, ge=0, le=1)
    aggregation_weight_adx: float = Field(default=0.10, ge=0, le=1)
    aggregation_weight_volume: float = Field(default=0.10, ge=0, le=1)
    aggregation_weight_breakout: float = Field(default=0.05, ge=0, le=1)
    aggregation_stability_stddev_cap: float = Field(default=0.35, gt=0, le=2)
    technical_main_timeframe: str = "4h"
    technical_confirmation_timeframe: str = "1h"
    technical_use_secondary_confirmation: bool = True
    technical_pass_threshold: float = Field(default=58, ge=0, le=100)
    technical_ohlcv_limit: int = Field(default=300, ge=50, le=2000)
    technical_min_ohlcv_rows: int = Field(default=120, ge=50, le=2000)
    technical_ma_fast_period: int = Field(default=20, ge=2, le=300)
    technical_ma_slow_period: int = Field(default=50, ge=3, le=500)
    technical_ma_slope_lookback: int = Field(default=6, ge=2, le=200)
    technical_ma_slope_min_pct: float = Field(default=0.001, ge=-0.2, le=0.2)
    technical_ma_slope_good_pct: float = Field(default=0.01, ge=-0.2, le=0.5)
    technical_adx_period: int = Field(default=14, ge=2, le=200)
    technical_adx_min: float = Field(default=18, ge=0, le=100)
    technical_adx_strong: float = Field(default=32, ge=0, le=100)
    technical_rsi_period: int = Field(default=14, ge=2, le=200)
    technical_rsi_bullish_min: float = Field(default=50, ge=0, le=100)
    technical_rsi_bullish_max: float = Field(default=74, ge=0, le=100)
    technical_rsi_extreme: float = Field(default=84, ge=0, le=100)
    technical_macd_fast: int = Field(default=12, ge=2, le=200)
    technical_macd_slow: int = Field(default=26, ge=3, le=400)
    technical_macd_signal: int = Field(default=9, ge=2, le=200)
    technical_stoch_period: int = Field(default=14, ge=2, le=200)
    technical_stoch_bullish_min: float = Field(default=45, ge=0, le=100)
    technical_stoch_overbought: float = Field(default=88, ge=0, le=100)
    technical_atr_period: int = Field(default=14, ge=2, le=200)
    technical_atr_pct_min: float = Field(default=0.002, ge=0, le=1)
    technical_atr_pct_max: float = Field(default=0.09, ge=0, le=1)
    technical_bbands_period: int = Field(default=20, ge=2, le=300)
    technical_bbands_stddev: float = Field(default=2.0, ge=0.1, le=6.0)
    technical_bb_width_compression_max: float = Field(default=0.05, ge=0, le=2)
    technical_bb_width_expansion_min: float = Field(default=0.08, ge=0, le=2)
    technical_overextended_above_upper_pct: float = Field(default=0.03, ge=0, le=0.5)
    technical_volume_ma_period: int = Field(default=20, ge=2, le=400)
    technical_volume_ratio_min: float = Field(default=1.10, ge=0, le=20)
    technical_volume_ratio_strong: float = Field(default=1.7, ge=0, le=50)
    technical_breakout_lookback: int = Field(default=20, ge=5, le=300)
    technical_breakout_buffer_pct: float = Field(default=0.001, ge=0, le=0.2)
    technical_pullback_tolerance_pct: float = Field(default=0.03, ge=0, le=0.5)
    technical_missing_critical_penalty: float = Field(default=2.5, ge=0, le=50)
    technical_secondary_confirmation_penalty: float = Field(default=1.5, ge=0, le=50)
    technical_overextended_penalty: float = Field(default=7.0, ge=0, le=50)
    technical_noisy_penalty: float = Field(default=6.0, ge=0, le=50)
    technical_weight_trend: float = Field(default=0.30, ge=0, le=1)
    technical_weight_momentum: float = Field(default=0.25, ge=0, le=1)
    technical_weight_volatility: float = Field(default=0.20, ge=0, le=1)
    technical_weight_volume: float = Field(default=0.15, ge=0, le=1)
    technical_weight_entry: float = Field(default=0.10, ge=0, le=1)
    technical_critical_indicators: list[str] = Field(
        default_factory=lambda: [
            "close",
            "ema_fast",
            "ema_slow",
            "rsi",
            "macd_hist",
            "adx",
            "atr",
            "volume_sma",
            "recent_high",
        ]
    )
    regime_btc_symbol: str = Field(default="BTC/USDT", min_length=1)
    regime_timeframe: str = "4h"
    regime_ohlcv_limit: int = Field(default=300, ge=50, le=2000)
    regime_min_ohlcv_rows: int = Field(default=120, ge=50, le=2000)
    regime_btc_ma_fast_period: int = Field(default=50, ge=2, le=400)
    regime_btc_ma_slow_period: int = Field(default=200, ge=3, le=800)
    regime_btc_slope_lookback: int = Field(default=8, ge=2, le=200)
    regime_btc_slope_min_pct: float = Field(default=0.0, ge=-0.3, le=0.3)
    regime_btc_slope_good_pct: float = Field(default=0.01, ge=-0.3, le=0.5)
    regime_adx_period: int = Field(default=14, ge=2, le=200)
    regime_adx_min: float = Field(default=18, ge=0, le=100)
    regime_adx_strong: float = Field(default=30, ge=0, le=100)
    regime_atr_period: int = Field(default=14, ge=2, le=200)
    regime_atr_danger_pct: float = Field(default=0.10, ge=0, le=2)
    regime_drawdown_lookback: int = Field(default=24, ge=2, le=500)
    regime_drawdown_danger_pct: float = Field(default=0.08, ge=0, le=1)
    regime_breadth_enabled: bool = True
    regime_breadth_timeframe: str = "4h"
    regime_breadth_symbol_count: int = Field(default=20, ge=1, le=300)
    regime_breadth_min_samples: int = Field(default=5, ge=1, le=300)
    regime_breadth_fast_period: int = Field(default=20, ge=2, le=300)
    regime_breadth_slow_period: int = Field(default=50, ge=3, le=500)
    regime_breadth_bullish_ratio: float = Field(default=0.65, ge=0, le=1)
    regime_breadth_bearish_ratio: float = Field(default=0.35, ge=0, le=1)
    regime_derivatives_enabled: bool = True
    regime_derivatives_symbol: str = ""
    regime_funding_abs_max: float = Field(default=0.0015, ge=0, le=1)
    regime_derivatives_neutral_score: float = Field(default=0.50, ge=0, le=1)
    regime_fallback_penalty_points: float = Field(default=4.0, ge=0, le=50)
    regime_score_bullish_threshold: float = Field(default=70, ge=0, le=100)
    regime_score_neutral_threshold: float = Field(default=45, ge=0, le=100)
    regime_allow_neutral: bool = True
    regime_veto_if_bearish: bool = True
    regime_veto_if_danger: bool = True
    regime_weight_trend: float = Field(default=0.45, ge=0, le=1)
    regime_weight_volatility: float = Field(default=0.30, ge=0, le=1)
    regime_weight_breadth: float = Field(default=0.20, ge=0, le=1)
    regime_weight_derivatives: float = Field(default=0.05, ge=0, le=1)
    deepseek_enabled: bool = False
    deepseek_shortlist_limit: int = Field(default=10, ge=1, le=200)
    deepseek_min_aggregate_score: float = Field(default=0.55, ge=0, le=1)
    deepseek_model: str = Field(default="deepseek-chat", min_length=1)
    deepseek_timeout_seconds: int = Field(default=20, ge=1, le=120)
    gemini_model: str = Field(default="gemini-2.0-flash", min_length=1)
    gemini_timeout_seconds: int = Field(default=20, ge=1, le=120)

    @model_validator(mode="after")
    def validate_runtime_config(self) -> "RuntimeConfig":
        self.llm_provider = self.llm_provider.strip().lower()
        if self.llm_provider not in {"disabled", "deepseek", "gemini"}:
            msg = "llm_provider must be one of: disabled, deepseek, gemini"
            raise ValueError(msg)

        try:
            self.snapshot_timeframe = normalize_timeframe(self.snapshot_timeframe)
        except ValueError as exc:
            msg = f"snapshot_timeframe is invalid: {self.snapshot_timeframe}"
            raise ValueError(msg) from exc

        try:
            self.technical_main_timeframe = normalize_timeframe(self.technical_main_timeframe)
        except ValueError as exc:
            msg = f"technical_main_timeframe is invalid: {self.technical_main_timeframe}"
            raise ValueError(msg) from exc

        try:
            self.technical_confirmation_timeframe = normalize_timeframe(
                self.technical_confirmation_timeframe
            )
        except ValueError as exc:
            msg = (
                "technical_confirmation_timeframe is invalid: "
                f"{self.technical_confirmation_timeframe}"
            )
            raise ValueError(msg) from exc

        try:
            self.regime_timeframe = normalize_timeframe(self.regime_timeframe)
        except ValueError as exc:
            msg = f"regime_timeframe is invalid: {self.regime_timeframe}"
            raise ValueError(msg) from exc

        try:
            self.regime_breadth_timeframe = normalize_timeframe(self.regime_breadth_timeframe)
        except ValueError as exc:
            msg = f"regime_breadth_timeframe is invalid: {self.regime_breadth_timeframe}"
            raise ValueError(msg) from exc

        normalized_supported: list[str] = []
        for item in self.supported_decision_horizons:
            try:
                normalized = normalize_timeframe(item)
            except ValueError as exc:
                msg = f"supported_decision_horizons has invalid value: {item}"
                raise ValueError(msg) from exc
            if normalized not in normalized_supported:
                normalized_supported.append(normalized)

        if not normalized_supported:
            msg = "supported_decision_horizons cannot be empty"
            raise ValueError(msg)

        self.supported_decision_horizons = normalized_supported

        try:
            self.decision_horizon = normalize_timeframe(self.decision_horizon)
        except ValueError as exc:
            msg = f"decision_horizon is invalid: {self.decision_horizon}"
            raise ValueError(msg) from exc

        if self.decision_horizon not in self.supported_decision_horizons:
            msg = f"decision_horizon must be one of {self.supported_decision_horizons}"
            raise ValueError(msg)

        if self.engine_max_signals > self.engine_universe_size:
            msg = "engine_max_signals must be <= engine_universe_size"
            raise ValueError(msg)

        if self.paper_max_open_positions > self.engine_universe_size:
            msg = "paper_max_open_positions must be <= engine_universe_size"
            raise ValueError(msg)

        if (self.paper_risk_per_trade_pct * self.paper_max_open_positions) > 1.0:
            msg = "paper_risk_per_trade_pct * paper_max_open_positions must be <= 1.0"
            raise ValueError(msg)

        if (
            self.paper_fixed_stop_loss_pct is not None
            and self.paper_fixed_take_profit_pct is not None
            and self.paper_fixed_take_profit_pct <= self.paper_fixed_stop_loss_pct
        ):
            msg = "paper_fixed_take_profit_pct must be > paper_fixed_stop_loss_pct when both are set"
            raise ValueError(msg)

        if self.hourly_min_snapshots > self.hourly_aggregation_window:
            msg = "hourly_min_snapshots must be <= hourly_aggregation_window"
            raise ValueError(msg)

        if self.technical_ma_fast_period >= self.technical_ma_slow_period:
            msg = "technical_ma_fast_period must be < technical_ma_slow_period"
            raise ValueError(msg)

        if self.technical_ohlcv_limit < self.technical_min_ohlcv_rows:
            msg = "technical_ohlcv_limit must be >= technical_min_ohlcv_rows"
            raise ValueError(msg)

        if self.technical_ma_slope_min_pct > self.technical_ma_slope_good_pct:
            msg = "technical_ma_slope_min_pct must be <= technical_ma_slope_good_pct"
            raise ValueError(msg)

        if self.technical_adx_min > self.technical_adx_strong:
            msg = "technical_adx_min must be <= technical_adx_strong"
            raise ValueError(msg)

        if self.technical_rsi_bullish_min > self.technical_rsi_bullish_max:
            msg = "technical_rsi_bullish_min must be <= technical_rsi_bullish_max"
            raise ValueError(msg)

        if self.technical_macd_fast >= self.technical_macd_slow:
            msg = "technical_macd_fast must be < technical_macd_slow"
            raise ValueError(msg)

        if self.technical_stoch_bullish_min > self.technical_stoch_overbought:
            msg = "technical_stoch_bullish_min must be <= technical_stoch_overbought"
            raise ValueError(msg)

        if self.technical_atr_pct_min > self.technical_atr_pct_max:
            msg = "technical_atr_pct_min must be <= technical_atr_pct_max"
            raise ValueError(msg)

        if self.technical_bb_width_compression_max > self.technical_bb_width_expansion_min:
            msg = "technical_bb_width_compression_max must be <= technical_bb_width_expansion_min"
            raise ValueError(msg)

        self.technical_critical_indicators = [
            str(item).strip() for item in self.technical_critical_indicators if str(item).strip()
        ]
        if not self.technical_critical_indicators:
            msg = "technical_critical_indicators cannot be empty"
            raise ValueError(msg)

        total_weight = (
            self.aggregation_weight_trend
            + self.aggregation_weight_slope
            + self.aggregation_weight_rsi
            + self.aggregation_weight_macd
            + self.aggregation_weight_adx
            + self.aggregation_weight_volume
            + self.aggregation_weight_breakout
        )
        if not 0.99 <= total_weight <= 1.01:
            msg = "aggregation weights must sum to 1.0"
            raise ValueError(msg)

        technical_weight_total = (
            self.technical_weight_trend
            + self.technical_weight_momentum
            + self.technical_weight_volatility
            + self.technical_weight_volume
            + self.technical_weight_entry
        )
        if not 0.99 <= technical_weight_total <= 1.01:
            msg = "technical weights must sum to 1.0"
            raise ValueError(msg)

        if self.regime_score_neutral_threshold > self.regime_score_bullish_threshold:
            msg = "regime_score_neutral_threshold must be <= regime_score_bullish_threshold"
            raise ValueError(msg)

        if self.regime_ohlcv_limit < self.regime_min_ohlcv_rows:
            msg = "regime_ohlcv_limit must be >= regime_min_ohlcv_rows"
            raise ValueError(msg)

        if self.regime_btc_ma_fast_period >= self.regime_btc_ma_slow_period:
            msg = "regime_btc_ma_fast_period must be < regime_btc_ma_slow_period"
            raise ValueError(msg)

        if self.regime_btc_slope_min_pct > self.regime_btc_slope_good_pct:
            msg = "regime_btc_slope_min_pct must be <= regime_btc_slope_good_pct"
            raise ValueError(msg)

        if self.regime_adx_min > self.regime_adx_strong:
            msg = "regime_adx_min must be <= regime_adx_strong"
            raise ValueError(msg)

        if self.regime_breadth_fast_period >= self.regime_breadth_slow_period:
            msg = "regime_breadth_fast_period must be < regime_breadth_slow_period"
            raise ValueError(msg)

        if self.regime_breadth_bearish_ratio >= self.regime_breadth_bullish_ratio:
            msg = "regime_breadth_bearish_ratio must be < regime_breadth_bullish_ratio"
            raise ValueError(msg)

        regime_weight_total = (
            self.regime_weight_trend
            + self.regime_weight_volatility
            + self.regime_weight_breadth
            + self.regime_weight_derivatives
        )
        if not 0.99 <= regime_weight_total <= 1.01:
            msg = "regime weights must sum to 1.0"
            raise ValueError(msg)

        self.deepseek_model = self.deepseek_model.strip()
        if not self.deepseek_model:
            msg = "deepseek_model cannot be empty"
            raise ValueError(msg)

        self.gemini_model = self.gemini_model.strip()
        if not self.gemini_model:
            msg = "gemini_model cannot be empty"
            raise ValueError(msg)

        return self

    @classmethod
    def from_settings(cls, settings) -> "RuntimeConfig":
        """Build runtime payload from Settings-like object."""
        return cls(
            llm_provider=settings.llm_provider,
            snapshot_timeframe=settings.snapshot_timeframe,
            snapshot_interval_minutes=settings.snapshot_interval_minutes,
            hourly_aggregation_window=settings.hourly_aggregation_window,
            hourly_min_snapshots=settings.hourly_min_snapshots,
            decision_horizon=settings.decision_horizon,
            supported_decision_horizons=settings.supported_decision_horizons,
            engine_enabled=settings.engine_enabled,
            engine_universe_size=settings.engine_universe_size,
            engine_refresh_seconds=settings.engine_refresh_seconds,
            engine_include_step2=settings.engine_include_step2,
            engine_include_step3=settings.engine_include_step3,
            engine_include_ai_support=settings.engine_include_ai_support,
            engine_max_signals=settings.engine_max_signals,
            paper_bot_enabled=settings.paper_bot_enabled,
            paper_initial_capital=settings.paper_initial_capital,
            paper_max_open_positions=settings.paper_max_open_positions,
            paper_risk_per_trade_pct=settings.paper_risk_per_trade_pct,
            paper_min_signal_score=settings.paper_min_signal_score,
            paper_require_final_selected=settings.paper_require_final_selected,
            paper_require_step2_pass=settings.paper_require_step2_pass,
            paper_require_step3_pass=settings.paper_require_step3_pass,
            paper_require_window_complete=settings.paper_require_window_complete,
            paper_fixed_stop_loss_pct=settings.paper_fixed_stop_loss_pct,
            paper_fixed_take_profit_pct=settings.paper_fixed_take_profit_pct,
            paper_atr_stop_multiplier=settings.paper_atr_stop_multiplier,
            paper_risk_reward_ratio=settings.paper_risk_reward_ratio,
            paper_max_hold_minutes=settings.paper_max_hold_minutes,
            paper_fee_bps=settings.paper_fee_bps,
            paper_slippage_bps=settings.paper_slippage_bps,
            paper_refresh_seconds=settings.paper_refresh_seconds,
            paper_sync_engine_before_run=settings.paper_sync_engine_before_run,
            aggregation_bullish_threshold=settings.aggregation_bullish_threshold,
            aggregation_weight_trend=settings.aggregation_weight_trend,
            aggregation_weight_slope=settings.aggregation_weight_slope,
            aggregation_weight_rsi=settings.aggregation_weight_rsi,
            aggregation_weight_macd=settings.aggregation_weight_macd,
            aggregation_weight_adx=settings.aggregation_weight_adx,
            aggregation_weight_volume=settings.aggregation_weight_volume,
            aggregation_weight_breakout=settings.aggregation_weight_breakout,
            aggregation_stability_stddev_cap=settings.aggregation_stability_stddev_cap,
            technical_main_timeframe=settings.technical_main_timeframe,
            technical_confirmation_timeframe=settings.technical_confirmation_timeframe,
            technical_use_secondary_confirmation=settings.technical_use_secondary_confirmation,
            technical_pass_threshold=settings.technical_pass_threshold,
            technical_ohlcv_limit=settings.technical_ohlcv_limit,
            technical_min_ohlcv_rows=settings.technical_min_ohlcv_rows,
            technical_ma_fast_period=settings.technical_ma_fast_period,
            technical_ma_slow_period=settings.technical_ma_slow_period,
            technical_ma_slope_lookback=settings.technical_ma_slope_lookback,
            technical_ma_slope_min_pct=settings.technical_ma_slope_min_pct,
            technical_ma_slope_good_pct=settings.technical_ma_slope_good_pct,
            technical_adx_period=settings.technical_adx_period,
            technical_adx_min=settings.technical_adx_min,
            technical_adx_strong=settings.technical_adx_strong,
            technical_rsi_period=settings.technical_rsi_period,
            technical_rsi_bullish_min=settings.technical_rsi_bullish_min,
            technical_rsi_bullish_max=settings.technical_rsi_bullish_max,
            technical_rsi_extreme=settings.technical_rsi_extreme,
            technical_macd_fast=settings.technical_macd_fast,
            technical_macd_slow=settings.technical_macd_slow,
            technical_macd_signal=settings.technical_macd_signal,
            technical_stoch_period=settings.technical_stoch_period,
            technical_stoch_bullish_min=settings.technical_stoch_bullish_min,
            technical_stoch_overbought=settings.technical_stoch_overbought,
            technical_atr_period=settings.technical_atr_period,
            technical_atr_pct_min=settings.technical_atr_pct_min,
            technical_atr_pct_max=settings.technical_atr_pct_max,
            technical_bbands_period=settings.technical_bbands_period,
            technical_bbands_stddev=settings.technical_bbands_stddev,
            technical_bb_width_compression_max=settings.technical_bb_width_compression_max,
            technical_bb_width_expansion_min=settings.technical_bb_width_expansion_min,
            technical_overextended_above_upper_pct=settings.technical_overextended_above_upper_pct,
            technical_volume_ma_period=settings.technical_volume_ma_period,
            technical_volume_ratio_min=settings.technical_volume_ratio_min,
            technical_volume_ratio_strong=settings.technical_volume_ratio_strong,
            technical_breakout_lookback=settings.technical_breakout_lookback,
            technical_breakout_buffer_pct=settings.technical_breakout_buffer_pct,
            technical_pullback_tolerance_pct=settings.technical_pullback_tolerance_pct,
            technical_missing_critical_penalty=settings.technical_missing_critical_penalty,
            technical_secondary_confirmation_penalty=settings.technical_secondary_confirmation_penalty,
            technical_overextended_penalty=settings.technical_overextended_penalty,
            technical_noisy_penalty=settings.technical_noisy_penalty,
            technical_weight_trend=settings.technical_weight_trend,
            technical_weight_momentum=settings.technical_weight_momentum,
            technical_weight_volatility=settings.technical_weight_volatility,
            technical_weight_volume=settings.technical_weight_volume,
            technical_weight_entry=settings.technical_weight_entry,
            technical_critical_indicators=settings.technical_critical_indicators,
            regime_btc_symbol=settings.regime_btc_symbol,
            regime_timeframe=settings.regime_timeframe,
            regime_ohlcv_limit=settings.regime_ohlcv_limit,
            regime_min_ohlcv_rows=settings.regime_min_ohlcv_rows,
            regime_btc_ma_fast_period=settings.regime_btc_ma_fast_period,
            regime_btc_ma_slow_period=settings.regime_btc_ma_slow_period,
            regime_btc_slope_lookback=settings.regime_btc_slope_lookback,
            regime_btc_slope_min_pct=settings.regime_btc_slope_min_pct,
            regime_btc_slope_good_pct=settings.regime_btc_slope_good_pct,
            regime_adx_period=settings.regime_adx_period,
            regime_adx_min=settings.regime_adx_min,
            regime_adx_strong=settings.regime_adx_strong,
            regime_atr_period=settings.regime_atr_period,
            regime_atr_danger_pct=settings.regime_atr_danger_pct,
            regime_drawdown_lookback=settings.regime_drawdown_lookback,
            regime_drawdown_danger_pct=settings.regime_drawdown_danger_pct,
            regime_breadth_enabled=settings.regime_breadth_enabled,
            regime_breadth_timeframe=settings.regime_breadth_timeframe,
            regime_breadth_symbol_count=settings.regime_breadth_symbol_count,
            regime_breadth_min_samples=settings.regime_breadth_min_samples,
            regime_breadth_fast_period=settings.regime_breadth_fast_period,
            regime_breadth_slow_period=settings.regime_breadth_slow_period,
            regime_breadth_bullish_ratio=settings.regime_breadth_bullish_ratio,
            regime_breadth_bearish_ratio=settings.regime_breadth_bearish_ratio,
            regime_derivatives_enabled=settings.regime_derivatives_enabled,
            regime_derivatives_symbol=settings.regime_derivatives_symbol,
            regime_funding_abs_max=settings.regime_funding_abs_max,
            regime_derivatives_neutral_score=settings.regime_derivatives_neutral_score,
            regime_fallback_penalty_points=settings.regime_fallback_penalty_points,
            regime_score_bullish_threshold=settings.regime_score_bullish_threshold,
            regime_score_neutral_threshold=settings.regime_score_neutral_threshold,
            regime_allow_neutral=settings.regime_allow_neutral,
            regime_veto_if_bearish=settings.regime_veto_if_bearish,
            regime_veto_if_danger=settings.regime_veto_if_danger,
            regime_weight_trend=settings.regime_weight_trend,
            regime_weight_volatility=settings.regime_weight_volatility,
            regime_weight_breadth=settings.regime_weight_breadth,
            regime_weight_derivatives=settings.regime_weight_derivatives,
            deepseek_enabled=settings.deepseek_enabled,
            deepseek_shortlist_limit=settings.deepseek_shortlist_limit,
            deepseek_min_aggregate_score=settings.deepseek_min_aggregate_score,
            deepseek_model=settings.deepseek_model,
            deepseek_timeout_seconds=settings.deepseek_timeout_seconds,
            gemini_model=settings.gemini_model,
            gemini_timeout_seconds=settings.gemini_timeout_seconds,
        )

    def to_settings_overrides(self) -> dict[str, object]:
        """Return values compatible with `Settings(...)` constructor overrides."""
        return self.model_dump()

    @property
    def ai_shortlist_limit(self) -> int:
        """Provider-agnostic alias over backward-compatible setting name."""
        return self.deepseek_shortlist_limit

    @property
    def ai_min_aggregate_score(self) -> float:
        """Provider-agnostic alias over backward-compatible setting name."""
        return self.deepseek_min_aggregate_score

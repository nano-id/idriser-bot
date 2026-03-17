"""Application settings for the active snapshot + Step2/Step3 core."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.utils.timeframe import normalize_timeframe


class Settings(BaseSettings):
    """Runtime settings loaded from environment and `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    llm_provider: str = Field(
        default="disabled",
        alias="LLM_PROVIDER",
    )
    exchange_id: str = Field(default="binance", alias="EXCHANGE_ID")
    universe_size: int = Field(default=50, ge=1, le=500, alias="UNIVERSE_SIZE")
    universe_quote_assets: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["USDT"],
        alias="UNIVERSE_QUOTE_ASSETS",
    )
    fallback_symbols: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "BNB/USDT",
            "ADA/USDT",
            "XRP/USDT",
            "DOGE/USDT",
        ],
        alias="FALLBACK_SYMBOLS",
    )
    excluded_base_suffixes: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["UP", "DOWN", "BULL", "BEAR", "3L", "3S", "5L", "5S"],
        alias="EXCLUDED_BASE_SUFFIXES",
    )
    excluded_base_prefixes: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["1000"],
        alias="EXCLUDED_BASE_PREFIXES",
    )
    excluded_symbol_keywords: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["PERP", "FUTURES"],
        alias="EXCLUDED_SYMBOL_KEYWORDS",
    )

    request_timeout_seconds: int = Field(default=15, ge=1, le=120, alias="REQUEST_TIMEOUT_SECONDS")
    request_max_retries: int = Field(default=3, ge=0, le=10, alias="REQUEST_MAX_RETRIES")
    request_backoff_seconds: float = Field(default=0.8, ge=0, le=10, alias="REQUEST_BACKOFF_SECONDS")
    output_dir: str = Field(default="logs", alias="OUTPUT_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    deepseek_enabled: bool = Field(default=False, alias="DEEPSEEK_ENABLED")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    deepseek_timeout_seconds: int = Field(default=20, ge=1, le=120, alias="DEEPSEEK_TIMEOUT_SECONDS")
    deepseek_max_retries: int = Field(default=2, ge=0, le=10, alias="DEEPSEEK_MAX_RETRIES")
    deepseek_shortlist_limit: int = Field(default=10, ge=1, le=200, alias="DEEPSEEK_SHORTLIST_LIMIT")
    deepseek_min_aggregate_score: float = Field(
        default=0.55,
        ge=0,
        le=1,
        alias="DEEPSEEK_MIN_AGGREGATE_SCORE",
    )
    deepseek_temperature: float = Field(default=0.1, ge=0, le=2, alias="DEEPSEEK_TEMPERATURE")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_base_url: str = Field(default="https://generativelanguage.googleapis.com", alias="GEMINI_BASE_URL")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    gemini_timeout_seconds: int = Field(default=20, ge=1, le=120, alias="GEMINI_TIMEOUT_SECONDS")
    gemini_max_retries: int = Field(default=2, ge=0, le=10, alias="GEMINI_MAX_RETRIES")
    gemini_temperature: float = Field(default=0.1, ge=0, le=2, alias="GEMINI_TEMPERATURE")

    snapshot_timeframe: str = Field(default="5m", alias="SNAPSHOT_TIMEFRAME")
    snapshot_interval_minutes: int = Field(default=5, ge=1, le=120, alias="SNAPSHOT_INTERVAL_MINUTES")
    # Backward-compatible names kept for transition.
    hourly_aggregation_window: int = Field(default=12, ge=1, le=500, alias="HOURLY_AGGREGATION_WINDOW")
    hourly_min_snapshots: int = Field(default=12, ge=1, le=500, alias="HOURLY_MIN_SNAPSHOTS")
    decision_horizon: str = Field(default="30m", alias="DECISION_HORIZON")
    supported_decision_horizons: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["5m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "8h", "12h", "1d"],
        alias="SUPPORTED_DECISION_HORIZONS",
    )
    engine_enabled: bool = Field(default=False, alias="ENGINE_ENABLED")
    engine_universe_size: int = Field(default=30, ge=1, le=500, alias="ENGINE_UNIVERSE_SIZE")
    engine_refresh_seconds: int = Field(default=30, ge=5, le=3600, alias="ENGINE_REFRESH_SECONDS")
    engine_include_step2: bool = Field(default=False, alias="ENGINE_INCLUDE_STEP2")
    engine_include_step3: bool = Field(default=False, alias="ENGINE_INCLUDE_STEP3")
    engine_include_ai_support: bool = Field(default=False, alias="ENGINE_INCLUDE_AI_SUPPORT")
    engine_max_signals: int = Field(default=20, ge=1, le=500, alias="ENGINE_MAX_SIGNALS")
    paper_bot_enabled: bool = Field(default=False, alias="PAPER_BOT_ENABLED")
    paper_initial_capital: float = Field(default=10_000.0, gt=0, alias="PAPER_INITIAL_CAPITAL")
    paper_max_open_positions: int = Field(default=5, ge=1, le=500, alias="PAPER_MAX_OPEN_POSITIONS")
    paper_risk_per_trade_pct: float = Field(default=0.01, gt=0, le=1, alias="PAPER_RISK_PER_TRADE_PCT")
    paper_min_signal_score: float = Field(default=0.42, ge=0, le=1, alias="PAPER_MIN_SIGNAL_SCORE")
    paper_require_final_selected: bool = Field(default=True, alias="PAPER_REQUIRE_FINAL_SELECTED")
    paper_require_step2_pass: bool = Field(default=False, alias="PAPER_REQUIRE_STEP2_PASS")
    paper_require_step3_pass: bool = Field(default=False, alias="PAPER_REQUIRE_STEP3_PASS")
    paper_require_window_complete: bool = Field(default=True, alias="PAPER_REQUIRE_WINDOW_COMPLETE")
    paper_fixed_stop_loss_pct: float | None = Field(default=None, gt=0, le=1, alias="PAPER_FIXED_STOP_LOSS_PCT")
    paper_fixed_take_profit_pct: float | None = Field(default=None, gt=0, le=1, alias="PAPER_FIXED_TAKE_PROFIT_PCT")
    paper_atr_stop_multiplier: float = Field(default=1.5, gt=0, le=50, alias="PAPER_ATR_STOP_MULTIPLIER")
    paper_risk_reward_ratio: float = Field(default=2.0, gt=0, le=50, alias="PAPER_RISK_REWARD_RATIO")
    paper_max_hold_minutes: int | None = Field(default=None, ge=1, le=20_000, alias="PAPER_MAX_HOLD_MINUTES")
    paper_fee_bps: float = Field(default=10.0, ge=0, le=500, alias="PAPER_FEE_BPS")
    paper_slippage_bps: float = Field(default=5.0, ge=0, le=500, alias="PAPER_SLIPPAGE_BPS")
    paper_refresh_seconds: int = Field(default=60, ge=5, le=3600, alias="PAPER_REFRESH_SECONDS")
    paper_sync_engine_before_run: bool = Field(default=True, alias="PAPER_SYNC_ENGINE_BEFORE_RUN")

    aggregation_bullish_threshold: float = Field(
        default=0.55,
        ge=0,
        le=1,
        alias="AGGREGATION_BULLISH_THRESHOLD",
    )
    aggregation_weight_trend: float = Field(default=0.30, ge=0, le=1, alias="AGGREGATION_WEIGHT_TREND")
    aggregation_weight_slope: float = Field(default=0.10, ge=0, le=1, alias="AGGREGATION_WEIGHT_SLOPE")
    aggregation_weight_rsi: float = Field(default=0.20, ge=0, le=1, alias="AGGREGATION_WEIGHT_RSI")
    aggregation_weight_macd: float = Field(default=0.15, ge=0, le=1, alias="AGGREGATION_WEIGHT_MACD")
    aggregation_weight_adx: float = Field(default=0.10, ge=0, le=1, alias="AGGREGATION_WEIGHT_ADX")
    aggregation_weight_volume: float = Field(default=0.10, ge=0, le=1, alias="AGGREGATION_WEIGHT_VOLUME")
    aggregation_weight_breakout: float = Field(default=0.05, ge=0, le=1, alias="AGGREGATION_WEIGHT_BREAKOUT")
    aggregation_stability_stddev_cap: float = Field(
        default=0.35,
        gt=0,
        le=2,
        alias="AGGREGATION_STABILITY_STDDEV_CAP",
    )

    technical_main_timeframe: str = Field(default="4h", alias="TECHNICAL_MAIN_TIMEFRAME")
    technical_confirmation_timeframe: str = Field(default="1h", alias="TECHNICAL_CONFIRMATION_TIMEFRAME")
    technical_use_secondary_confirmation: bool = Field(
        default=True,
        alias="TECHNICAL_USE_SECONDARY_CONFIRMATION",
    )
    technical_pass_threshold: float = Field(default=58, ge=0, le=100, alias="TECHNICAL_PASS_THRESHOLD")
    technical_ohlcv_limit: int = Field(default=300, ge=50, le=2000, alias="TECHNICAL_OHLCV_LIMIT")
    technical_min_ohlcv_rows: int = Field(default=120, ge=50, le=2000, alias="TECHNICAL_MIN_OHLCV_ROWS")
    technical_ma_fast_period: int = Field(default=20, ge=2, le=300, alias="TECHNICAL_MA_FAST_PERIOD")
    technical_ma_slow_period: int = Field(default=50, ge=3, le=500, alias="TECHNICAL_MA_SLOW_PERIOD")
    technical_ma_slope_lookback: int = Field(default=6, ge=2, le=200, alias="TECHNICAL_MA_SLOPE_LOOKBACK")
    technical_ma_slope_min_pct: float = Field(
        default=0.001,
        ge=-0.2,
        le=0.2,
        alias="TECHNICAL_MA_SLOPE_MIN_PCT",
    )
    technical_ma_slope_good_pct: float = Field(
        default=0.01,
        ge=-0.2,
        le=0.5,
        alias="TECHNICAL_MA_SLOPE_GOOD_PCT",
    )
    technical_adx_period: int = Field(default=14, ge=2, le=200, alias="TECHNICAL_ADX_PERIOD")
    technical_adx_min: float = Field(default=18, ge=0, le=100, alias="TECHNICAL_ADX_MIN")
    technical_adx_strong: float = Field(default=32, ge=0, le=100, alias="TECHNICAL_ADX_STRONG")
    technical_rsi_period: int = Field(default=14, ge=2, le=200, alias="TECHNICAL_RSI_PERIOD")
    technical_rsi_bullish_min: float = Field(default=50, ge=0, le=100, alias="TECHNICAL_RSI_BULLISH_MIN")
    technical_rsi_bullish_max: float = Field(default=74, ge=0, le=100, alias="TECHNICAL_RSI_BULLISH_MAX")
    technical_rsi_extreme: float = Field(default=84, ge=0, le=100, alias="TECHNICAL_RSI_EXTREME")
    technical_macd_fast: int = Field(default=12, ge=2, le=200, alias="TECHNICAL_MACD_FAST")
    technical_macd_slow: int = Field(default=26, ge=3, le=400, alias="TECHNICAL_MACD_SLOW")
    technical_macd_signal: int = Field(default=9, ge=2, le=200, alias="TECHNICAL_MACD_SIGNAL")
    technical_stoch_period: int = Field(default=14, ge=2, le=200, alias="TECHNICAL_STOCH_PERIOD")
    technical_stoch_bullish_min: float = Field(default=45, ge=0, le=100, alias="TECHNICAL_STOCH_BULLISH_MIN")
    technical_stoch_overbought: float = Field(default=88, ge=0, le=100, alias="TECHNICAL_STOCH_OVERBOUGHT")
    technical_atr_period: int = Field(default=14, ge=2, le=200, alias="TECHNICAL_ATR_PERIOD")
    technical_atr_pct_min: float = Field(default=0.002, ge=0, le=1, alias="TECHNICAL_ATR_PCT_MIN")
    technical_atr_pct_max: float = Field(default=0.09, ge=0, le=1, alias="TECHNICAL_ATR_PCT_MAX")
    technical_bbands_period: int = Field(default=20, ge=2, le=300, alias="TECHNICAL_BBANDS_PERIOD")
    technical_bbands_stddev: float = Field(default=2.0, ge=0.1, le=6.0, alias="TECHNICAL_BBANDS_STDDEV")
    technical_bb_width_compression_max: float = Field(
        default=0.05,
        ge=0,
        le=2,
        alias="TECHNICAL_BB_WIDTH_COMPRESSION_MAX",
    )
    technical_bb_width_expansion_min: float = Field(
        default=0.08,
        ge=0,
        le=2,
        alias="TECHNICAL_BB_WIDTH_EXPANSION_MIN",
    )
    technical_overextended_above_upper_pct: float = Field(
        default=0.03,
        ge=0,
        le=0.5,
        alias="TECHNICAL_OVEREXTENDED_ABOVE_UPPER_PCT",
    )
    technical_volume_ma_period: int = Field(default=20, ge=2, le=400, alias="TECHNICAL_VOLUME_MA_PERIOD")
    technical_volume_ratio_min: float = Field(default=1.10, ge=0, le=20, alias="TECHNICAL_VOLUME_RATIO_MIN")
    technical_volume_ratio_strong: float = Field(default=1.7, ge=0, le=50, alias="TECHNICAL_VOLUME_RATIO_STRONG")
    technical_breakout_lookback: int = Field(default=20, ge=5, le=300, alias="TECHNICAL_BREAKOUT_LOOKBACK")
    technical_breakout_buffer_pct: float = Field(
        default=0.001,
        ge=0,
        le=0.2,
        alias="TECHNICAL_BREAKOUT_BUFFER_PCT",
    )
    technical_pullback_tolerance_pct: float = Field(
        default=0.03,
        ge=0,
        le=0.5,
        alias="TECHNICAL_PULLBACK_TOLERANCE_PCT",
    )
    technical_missing_critical_penalty: float = Field(
        default=1.5,
        ge=0,
        le=50,
        alias="TECHNICAL_MISSING_CRITICAL_PENALTY",
    )
    technical_secondary_confirmation_penalty: float = Field(
        default=1.5,
        ge=0,
        le=50,
        alias="TECHNICAL_SECONDARY_CONFIRMATION_PENALTY",
    )
    technical_overextended_penalty: float = Field(
        default=7.0,
        ge=0,
        le=50,
        alias="TECHNICAL_OVEREXTENDED_PENALTY",
    )
    technical_noisy_penalty: float = Field(default=6.0, ge=0, le=50, alias="TECHNICAL_NOISY_PENALTY")
    technical_weight_trend: float = Field(default=0.30, ge=0, le=1, alias="TECHNICAL_WEIGHT_TREND")
    technical_weight_momentum: float = Field(default=0.25, ge=0, le=1, alias="TECHNICAL_WEIGHT_MOMENTUM")
    technical_weight_volatility: float = Field(default=0.20, ge=0, le=1, alias="TECHNICAL_WEIGHT_VOLATILITY")
    technical_weight_volume: float = Field(default=0.15, ge=0, le=1, alias="TECHNICAL_WEIGHT_VOLUME")
    technical_weight_entry: float = Field(default=0.10, ge=0, le=1, alias="TECHNICAL_WEIGHT_ENTRY")
    technical_critical_indicators: Annotated[list[str], NoDecode] = Field(
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
        ],
        alias="TECHNICAL_CRITICAL_INDICATORS",
    )

    regime_btc_symbol: str = Field(default="BTC/USDT", alias="REGIME_BTC_SYMBOL")
    regime_timeframe: str = Field(default="4h", alias="REGIME_TIMEFRAME")
    regime_ohlcv_limit: int = Field(default=300, ge=50, le=2000, alias="REGIME_OHLCV_LIMIT")
    regime_min_ohlcv_rows: int = Field(default=120, ge=50, le=2000, alias="REGIME_MIN_OHLCV_ROWS")
    regime_btc_ma_fast_period: int = Field(default=50, ge=2, le=400, alias="REGIME_BTC_MA_FAST_PERIOD")
    regime_btc_ma_slow_period: int = Field(default=200, ge=3, le=800, alias="REGIME_BTC_MA_SLOW_PERIOD")
    regime_btc_slope_lookback: int = Field(default=8, ge=2, le=200, alias="REGIME_BTC_SLOPE_LOOKBACK")
    regime_btc_slope_min_pct: float = Field(default=0.0, ge=-0.3, le=0.3, alias="REGIME_BTC_SLOPE_MIN_PCT")
    regime_btc_slope_good_pct: float = Field(default=0.01, ge=-0.3, le=0.5, alias="REGIME_BTC_SLOPE_GOOD_PCT")
    regime_adx_period: int = Field(default=14, ge=2, le=200, alias="REGIME_ADX_PERIOD")
    regime_adx_min: float = Field(default=18, ge=0, le=100, alias="REGIME_ADX_MIN")
    regime_adx_strong: float = Field(default=30, ge=0, le=100, alias="REGIME_ADX_STRONG")
    regime_atr_period: int = Field(default=14, ge=2, le=200, alias="REGIME_ATR_PERIOD")
    regime_atr_danger_pct: float = Field(default=0.10, ge=0, le=2, alias="REGIME_ATR_DANGER_PCT")
    regime_drawdown_lookback: int = Field(default=24, ge=2, le=500, alias="REGIME_DRAWDOWN_LOOKBACK")
    regime_drawdown_danger_pct: float = Field(default=0.08, ge=0, le=1, alias="REGIME_DRAWDOWN_DANGER_PCT")
    regime_breadth_enabled: bool = Field(default=True, alias="REGIME_BREADTH_ENABLED")
    regime_breadth_timeframe: str = Field(default="4h", alias="REGIME_BREADTH_TIMEFRAME")
    regime_breadth_symbol_count: int = Field(default=20, ge=1, le=300, alias="REGIME_BREADTH_SYMBOL_COUNT")
    regime_breadth_min_samples: int = Field(default=5, ge=1, le=300, alias="REGIME_BREADTH_MIN_SAMPLES")
    regime_breadth_fast_period: int = Field(default=20, ge=2, le=300, alias="REGIME_BREADTH_FAST_PERIOD")
    regime_breadth_slow_period: int = Field(default=50, ge=3, le=500, alias="REGIME_BREADTH_SLOW_PERIOD")
    regime_breadth_bullish_ratio: float = Field(default=0.65, ge=0, le=1, alias="REGIME_BREADTH_BULLISH_RATIO")
    regime_breadth_bearish_ratio: float = Field(default=0.35, ge=0, le=1, alias="REGIME_BREADTH_BEARISH_RATIO")
    regime_derivatives_enabled: bool = Field(default=True, alias="REGIME_DERIVATIVES_ENABLED")
    regime_derivatives_symbol: str = Field(default="", alias="REGIME_DERIVATIVES_SYMBOL")
    regime_funding_abs_max: float = Field(default=0.0015, ge=0, le=1, alias="REGIME_FUNDING_ABS_MAX")
    regime_derivatives_neutral_score: float = Field(
        default=0.50,
        ge=0,
        le=1,
        alias="REGIME_DERIVATIVES_NEUTRAL_SCORE",
    )
    regime_fallback_penalty_points: float = Field(default=4.0, ge=0, le=50, alias="REGIME_FALLBACK_PENALTY_POINTS")
    regime_weight_trend: float = Field(default=0.45, ge=0, le=1, alias="REGIME_WEIGHT_TREND")
    regime_weight_volatility: float = Field(default=0.30, ge=0, le=1, alias="REGIME_WEIGHT_VOLATILITY")
    regime_weight_breadth: float = Field(default=0.20, ge=0, le=1, alias="REGIME_WEIGHT_BREADTH")
    regime_weight_derivatives: float = Field(default=0.05, ge=0, le=1, alias="REGIME_WEIGHT_DERIVATIVES")
    regime_score_bullish_threshold: float = Field(
        default=70,
        ge=0,
        le=100,
        alias="REGIME_SCORE_BULLISH_THRESHOLD",
    )
    regime_score_neutral_threshold: float = Field(
        default=45,
        ge=0,
        le=100,
        alias="REGIME_SCORE_NEUTRAL_THRESHOLD",
    )
    regime_allow_neutral: bool = Field(default=True, alias="REGIME_ALLOW_NEUTRAL")
    regime_veto_if_bearish: bool = Field(default=True, alias="REGIME_VETO_IF_BEARISH")
    regime_veto_if_danger: bool = Field(default=True, alias="REGIME_VETO_IF_DANGER")

    @field_validator(
        "universe_quote_assets",
        "fallback_symbols",
        "excluded_base_suffixes",
        "excluded_base_prefixes",
        "excluded_symbol_keywords",
        "supported_decision_horizons",
        "technical_critical_indicators",
        mode="before",
    )
    @classmethod
    def parse_csv_list(cls, value: Any) -> list[str] | Any:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        self.llm_provider = self.llm_provider.strip().lower()
        if self.llm_provider not in {"disabled", "deepseek", "gemini"}:
            msg = "LLM_PROVIDER must be one of: disabled, deepseek, gemini"
            raise ValueError(msg)

        technical_weight_total = (
            self.technical_weight_trend
            + self.technical_weight_momentum
            + self.technical_weight_volatility
            + self.technical_weight_volume
            + self.technical_weight_entry
        )
        if not 0.99 <= technical_weight_total <= 1.01:
            msg = "Technical weights must sum to 1.0"
            raise ValueError(msg)

        if self.technical_ma_fast_period >= self.technical_ma_slow_period:
            msg = "TECHNICAL_MA_FAST_PERIOD must be smaller than TECHNICAL_MA_SLOW_PERIOD"
            raise ValueError(msg)

        if self.technical_rsi_bullish_min > self.technical_rsi_bullish_max:
            msg = "TECHNICAL_RSI_BULLISH_MIN must be <= TECHNICAL_RSI_BULLISH_MAX"
            raise ValueError(msg)

        if self.technical_adx_min > self.technical_adx_strong:
            msg = "TECHNICAL_ADX_MIN must be <= TECHNICAL_ADX_STRONG"
            raise ValueError(msg)

        if self.regime_btc_ma_fast_period >= self.regime_btc_ma_slow_period:
            msg = "REGIME_BTC_MA_FAST_PERIOD must be smaller than REGIME_BTC_MA_SLOW_PERIOD"
            raise ValueError(msg)

        if self.regime_breadth_fast_period >= self.regime_breadth_slow_period:
            msg = "REGIME_BREADTH_FAST_PERIOD must be smaller than REGIME_BREADTH_SLOW_PERIOD"
            raise ValueError(msg)

        if self.regime_breadth_bearish_ratio >= self.regime_breadth_bullish_ratio:
            msg = "REGIME_BREADTH_BEARISH_RATIO must be smaller than REGIME_BREADTH_BULLISH_RATIO"
            raise ValueError(msg)

        if self.regime_score_neutral_threshold > self.regime_score_bullish_threshold:
            msg = "REGIME_SCORE_NEUTRAL_THRESHOLD must be <= REGIME_SCORE_BULLISH_THRESHOLD"
            raise ValueError(msg)

        regime_weight_total = (
            self.regime_weight_trend
            + self.regime_weight_volatility
            + self.regime_weight_breadth
            + self.regime_weight_derivatives
        )
        if not 0.99 <= regime_weight_total <= 1.01:
            msg = "Regime weights must sum to 1.0"
            raise ValueError(msg)

        try:
            self.snapshot_timeframe = normalize_timeframe(self.snapshot_timeframe)
        except ValueError as exc:
            msg = f"SNAPSHOT_TIMEFRAME is invalid: {self.snapshot_timeframe}"
            raise ValueError(msg) from exc

        normalized_supported: list[str] = []
        for horizon in self.supported_decision_horizons:
            try:
                normalized = normalize_timeframe(horizon)
            except ValueError as exc:
                msg = f"SUPPORTED_DECISION_HORIZONS contains invalid value: {horizon}"
                raise ValueError(msg) from exc
            if normalized not in normalized_supported:
                normalized_supported.append(normalized)

        if not normalized_supported:
            msg = "SUPPORTED_DECISION_HORIZONS cannot be empty"
            raise ValueError(msg)
        self.supported_decision_horizons = normalized_supported

        try:
            self.decision_horizon = normalize_timeframe(self.decision_horizon)
        except ValueError as exc:
            msg = f"DECISION_HORIZON is invalid: {self.decision_horizon}"
            raise ValueError(msg) from exc

        if self.decision_horizon not in self.supported_decision_horizons:
            msg = f"DECISION_HORIZON must be one of {self.supported_decision_horizons}"
            raise ValueError(msg)

        if self.engine_max_signals > self.engine_universe_size:
            msg = "ENGINE_MAX_SIGNALS must be <= ENGINE_UNIVERSE_SIZE"
            raise ValueError(msg)

        if self.paper_max_open_positions > self.engine_universe_size:
            msg = "PAPER_MAX_OPEN_POSITIONS must be <= ENGINE_UNIVERSE_SIZE"
            raise ValueError(msg)

        if (self.paper_risk_per_trade_pct * self.paper_max_open_positions) > 1.0:
            msg = "PAPER_RISK_PER_TRADE_PCT * PAPER_MAX_OPEN_POSITIONS must be <= 1.0"
            raise ValueError(msg)

        if (
            self.paper_fixed_stop_loss_pct is not None
            and self.paper_fixed_take_profit_pct is not None
            and self.paper_fixed_take_profit_pct <= self.paper_fixed_stop_loss_pct
        ):
            msg = "PAPER_FIXED_TAKE_PROFIT_PCT must be > PAPER_FIXED_STOP_LOSS_PCT when both are set"
            raise ValueError(msg)

        if self.hourly_min_snapshots > self.hourly_aggregation_window:
            msg = "HOURLY_MIN_SNAPSHOTS must be <= HOURLY_AGGREGATION_WINDOW"
            raise ValueError(msg)

        aggregation_weight_total = (
            self.aggregation_weight_trend
            + self.aggregation_weight_slope
            + self.aggregation_weight_rsi
            + self.aggregation_weight_macd
            + self.aggregation_weight_adx
            + self.aggregation_weight_volume
            + self.aggregation_weight_breakout
        )
        if not 0.99 <= aggregation_weight_total <= 1.01:
            msg = "Aggregation weights must sum to 1.0"
            raise ValueError(msg)

        self.deepseek_base_url = self.deepseek_base_url.strip().rstrip("/")
        if not self.deepseek_base_url:
            msg = "DEEPSEEK_BASE_URL cannot be empty"
            raise ValueError(msg)

        self.deepseek_model = self.deepseek_model.strip()
        if not self.deepseek_model:
            msg = "DEEPSEEK_MODEL cannot be empty"
            raise ValueError(msg)

        self.gemini_base_url = self.gemini_base_url.strip().rstrip("/")
        if not self.gemini_base_url:
            msg = "GEMINI_BASE_URL cannot be empty"
            raise ValueError(msg)

        self.gemini_model = self.gemini_model.strip()
        if not self.gemini_model:
            msg = "GEMINI_MODEL cannot be empty"
            raise ValueError(msg)

        return self

    @property
    def technical_weights(self) -> dict[str, float]:
        """Return Step 2 category weights."""
        return {
            "trend": self.technical_weight_trend,
            "momentum": self.technical_weight_momentum,
            "volatility": self.technical_weight_volatility,
            "volume": self.technical_weight_volume,
            "entry": self.technical_weight_entry,
        }

    @property
    def regime_weights(self) -> dict[str, float]:
        """Return Step 3 regime scoring weights."""
        return {
            "trend": self.regime_weight_trend,
            "volatility": self.regime_weight_volatility,
            "breadth": self.regime_weight_breadth,
            "derivatives": self.regime_weight_derivatives,
        }

    @property
    def aggregation_weights(self) -> dict[str, float]:
        """Return snapshot aggregation component weights."""
        return {
            "trend": self.aggregation_weight_trend,
            "slope": self.aggregation_weight_slope,
            "rsi": self.aggregation_weight_rsi,
            "macd": self.aggregation_weight_macd,
            "adx": self.aggregation_weight_adx,
            "volume": self.aggregation_weight_volume,
            "breakout": self.aggregation_weight_breakout,
        }

    @property
    def llm_enabled(self) -> bool:
        """Return effective LLM enablement flag."""
        if self.llm_provider == "disabled":
            return False
        if self.llm_provider == "deepseek":
            return self.deepseek_enabled
        return True

    @property
    def llm_configured(self) -> bool:
        """Return whether active provider has required credentials."""
        if self.llm_provider == "deepseek":
            return bool(self.deepseek_api_key.strip())
        if self.llm_provider == "gemini":
            return bool(self.gemini_api_key.strip())
        return False

    @property
    def ai_shortlist_limit(self) -> int:
        """Provider-agnostic alias over backward-compatible setting name."""
        return self.deepseek_shortlist_limit

    @property
    def ai_min_aggregate_score(self) -> float:
        """Provider-agnostic alias over backward-compatible setting name."""
        return self.deepseek_min_aggregate_score


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()

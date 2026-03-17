"""Configuration loading tests."""

from __future__ import annotations

import pytest

from app.config.settings import Settings


def test_settings_load_csv_and_thresholds(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("UNIVERSE_QUOTE_ASSETS", "USDT,USDC")
    monkeypatch.setenv("SNAPSHOT_TIMEFRAME", "5m")
    monkeypatch.setenv("SNAPSHOT_INTERVAL_MINUTES", "5")
    monkeypatch.setenv("HOURLY_AGGREGATION_WINDOW", "12")
    monkeypatch.setenv("HOURLY_MIN_SNAPSHOTS", "12")
    monkeypatch.setenv("DECISION_HORIZON", "1H")
    monkeypatch.setenv("SUPPORTED_DECISION_HORIZONS", "5m,15m,30M,1h,2H,4H,1D")
    monkeypatch.setenv("ENGINE_ENABLED", "true")
    monkeypatch.setenv("ENGINE_UNIVERSE_SIZE", "40")
    monkeypatch.setenv("ENGINE_REFRESH_SECONDS", "45")
    monkeypatch.setenv("ENGINE_INCLUDE_STEP2", "true")
    monkeypatch.setenv("ENGINE_INCLUDE_STEP3", "false")
    monkeypatch.setenv("ENGINE_INCLUDE_AI_SUPPORT", "true")
    monkeypatch.setenv("ENGINE_MAX_SIGNALS", "12")
    monkeypatch.setenv("TECHNICAL_OHLCV_LIMIT", "400")
    monkeypatch.setenv("TECHNICAL_MIN_OHLCV_ROWS", "140")
    monkeypatch.setenv("TECHNICAL_MA_SLOPE_LOOKBACK", "8")
    monkeypatch.setenv("TECHNICAL_MA_SLOPE_MIN_PCT", "0.002")
    monkeypatch.setenv("TECHNICAL_MA_SLOPE_GOOD_PCT", "0.015")
    monkeypatch.setenv("TECHNICAL_ADX_PERIOD", "16")
    monkeypatch.setenv("TECHNICAL_RSI_PERIOD", "12")
    monkeypatch.setenv("TECHNICAL_RSI_EXTREME", "84")
    monkeypatch.setenv("TECHNICAL_MACD_FAST", "10")
    monkeypatch.setenv("TECHNICAL_MACD_SLOW", "24")
    monkeypatch.setenv("TECHNICAL_MACD_SIGNAL", "8")
    monkeypatch.setenv("TECHNICAL_STOCH_PERIOD", "12")
    monkeypatch.setenv("TECHNICAL_STOCH_BULLISH_MIN", "48")
    monkeypatch.setenv("TECHNICAL_STOCH_OVERBOUGHT", "88")
    monkeypatch.setenv("TECHNICAL_ATR_PERIOD", "12")
    monkeypatch.setenv("TECHNICAL_ATR_PCT_MIN", "0.003")
    monkeypatch.setenv("TECHNICAL_ATR_PCT_MAX", "0.08")
    monkeypatch.setenv("TECHNICAL_BBANDS_PERIOD", "18")
    monkeypatch.setenv("TECHNICAL_BBANDS_STDDEV", "2.2")
    monkeypatch.setenv("TECHNICAL_BB_WIDTH_COMPRESSION_MAX", "0.04")
    monkeypatch.setenv("TECHNICAL_BB_WIDTH_EXPANSION_MIN", "0.09")
    monkeypatch.setenv("TECHNICAL_OVEREXTENDED_ABOVE_UPPER_PCT", "0.025")
    monkeypatch.setenv("TECHNICAL_VOLUME_MA_PERIOD", "24")
    monkeypatch.setenv("TECHNICAL_PULLBACK_TOLERANCE_PCT", "0.02")
    monkeypatch.setenv("TECHNICAL_MISSING_CRITICAL_PENALTY", "3.0")
    monkeypatch.setenv("TECHNICAL_SECONDARY_CONFIRMATION_PENALTY", "6.0")
    monkeypatch.setenv("TECHNICAL_OVEREXTENDED_PENALTY", "8.0")
    monkeypatch.setenv("TECHNICAL_NOISY_PENALTY", "5.0")
    monkeypatch.setenv("TECHNICAL_CRITICAL_INDICATORS", "close,ema_fast,ema_slow,rsi,macd_hist")
    monkeypatch.setenv("REGIME_OHLCV_LIMIT", "420")
    monkeypatch.setenv("REGIME_MIN_OHLCV_ROWS", "140")
    monkeypatch.setenv("REGIME_BTC_MA_FAST_PERIOD", "55")
    monkeypatch.setenv("REGIME_BTC_MA_SLOW_PERIOD", "210")
    monkeypatch.setenv("REGIME_BTC_SLOPE_LOOKBACK", "10")
    monkeypatch.setenv("REGIME_BTC_SLOPE_MIN_PCT", "0.001")
    monkeypatch.setenv("REGIME_BTC_SLOPE_GOOD_PCT", "0.02")
    monkeypatch.setenv("REGIME_ADX_PERIOD", "16")
    monkeypatch.setenv("REGIME_ADX_MIN", "20")
    monkeypatch.setenv("REGIME_ADX_STRONG", "34")
    monkeypatch.setenv("REGIME_ATR_PERIOD", "16")
    monkeypatch.setenv("REGIME_DRAWDOWN_LOOKBACK", "30")
    monkeypatch.setenv("REGIME_BREADTH_TIMEFRAME", "2h")
    monkeypatch.setenv("REGIME_BREADTH_SYMBOL_COUNT", "18")
    monkeypatch.setenv("REGIME_BREADTH_MIN_SAMPLES", "6")
    monkeypatch.setenv("REGIME_BREADTH_FAST_PERIOD", "18")
    monkeypatch.setenv("REGIME_BREADTH_SLOW_PERIOD", "48")
    monkeypatch.setenv("REGIME_BREADTH_BULLISH_RATIO", "0.7")
    monkeypatch.setenv("REGIME_BREADTH_BEARISH_RATIO", "0.3")
    monkeypatch.setenv("REGIME_DERIVATIVES_SYMBOL", "BTC/USDT:USDT")
    monkeypatch.setenv("REGIME_FUNDING_ABS_MAX", "0.002")
    monkeypatch.setenv("REGIME_DERIVATIVES_NEUTRAL_SCORE", "0.55")
    monkeypatch.setenv("REGIME_FALLBACK_PENALTY_POINTS", "5.0")
    monkeypatch.setenv("PAPER_BOT_ENABLED", "true")
    monkeypatch.setenv("PAPER_INITIAL_CAPITAL", "15000")
    monkeypatch.setenv("PAPER_MAX_OPEN_POSITIONS", "4")
    monkeypatch.setenv("PAPER_RISK_PER_TRADE_PCT", "0.02")
    monkeypatch.setenv("PAPER_MIN_SIGNAL_SCORE", "0.63")
    monkeypatch.setenv("PAPER_REQUIRE_STEP2_PASS", "true")
    monkeypatch.setenv("PAPER_REQUIRE_STEP3_PASS", "false")
    monkeypatch.setenv("PAPER_REQUIRE_WINDOW_COMPLETE", "true")
    monkeypatch.setenv("PAPER_ATR_STOP_MULTIPLIER", "1.8")
    monkeypatch.setenv("PAPER_RISK_REWARD_RATIO", "2.3")
    monkeypatch.setenv("PAPER_MAX_HOLD_MINUTES", "300")
    monkeypatch.setenv("AGGREGATION_BULLISH_THRESHOLD", "0.6")
    monkeypatch.setenv("AGGREGATION_WEIGHT_TREND", "0.30")
    monkeypatch.setenv("AGGREGATION_WEIGHT_SLOPE", "0.10")
    monkeypatch.setenv("AGGREGATION_WEIGHT_RSI", "0.20")
    monkeypatch.setenv("AGGREGATION_WEIGHT_MACD", "0.15")
    monkeypatch.setenv("AGGREGATION_WEIGHT_ADX", "0.10")
    monkeypatch.setenv("AGGREGATION_WEIGHT_VOLUME", "0.10")
    monkeypatch.setenv("AGGREGATION_WEIGHT_BREAKOUT", "0.05")
    monkeypatch.setenv("AGGREGATION_STABILITY_STDDEV_CAP", "0.4")
    monkeypatch.setenv("DEEPSEEK_ENABLED", "true")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_TIMEOUT_SECONDS", "25")
    monkeypatch.setenv("DEEPSEEK_MAX_RETRIES", "2")
    monkeypatch.setenv("DEEPSEEK_SHORTLIST_LIMIT", "8")
    monkeypatch.setenv("DEEPSEEK_MIN_AGGREGATE_SCORE", "0.62")
    monkeypatch.setenv("DEEPSEEK_TEMPERATURE", "0.15")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.0-flash")
    monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", "22")
    monkeypatch.setenv("GEMINI_MAX_RETRIES", "3")
    monkeypatch.setenv("GEMINI_TEMPERATURE", "0.2")

    settings = Settings(_env_file=None)
    assert settings.universe_quote_assets == ["USDT", "USDC"]
    assert settings.snapshot_timeframe == "5m"
    assert settings.snapshot_interval_minutes == 5
    assert settings.hourly_aggregation_window == 12
    assert settings.hourly_min_snapshots == 12
    assert settings.decision_horizon == "1h"
    assert settings.supported_decision_horizons == ["5m", "15m", "30m", "1h", "2h", "4h", "1d"]
    assert settings.engine_enabled is True
    assert settings.engine_universe_size == 40
    assert settings.engine_refresh_seconds == 45
    assert settings.engine_include_step2 is True
    assert settings.engine_include_step3 is False
    assert settings.engine_include_ai_support is True
    assert settings.engine_max_signals == 12
    assert settings.technical_ohlcv_limit == 400
    assert settings.technical_min_ohlcv_rows == 140
    assert settings.technical_ma_slope_lookback == 8
    assert settings.technical_ma_slope_min_pct == 0.002
    assert settings.technical_ma_slope_good_pct == 0.015
    assert settings.technical_adx_period == 16
    assert settings.technical_rsi_period == 12
    assert settings.technical_rsi_extreme == 84
    assert settings.technical_macd_fast == 10
    assert settings.technical_macd_slow == 24
    assert settings.technical_macd_signal == 8
    assert settings.technical_stoch_period == 12
    assert settings.technical_stoch_bullish_min == 48
    assert settings.technical_stoch_overbought == 88
    assert settings.technical_atr_period == 12
    assert settings.technical_atr_pct_min == 0.003
    assert settings.technical_atr_pct_max == 0.08
    assert settings.technical_bbands_period == 18
    assert settings.technical_bbands_stddev == 2.2
    assert settings.technical_bb_width_compression_max == 0.04
    assert settings.technical_bb_width_expansion_min == 0.09
    assert settings.technical_overextended_above_upper_pct == 0.025
    assert settings.technical_volume_ma_period == 24
    assert settings.technical_pullback_tolerance_pct == 0.02
    assert settings.technical_missing_critical_penalty == 3.0
    assert settings.technical_secondary_confirmation_penalty == 6.0
    assert settings.technical_overextended_penalty == 8.0
    assert settings.technical_noisy_penalty == 5.0
    assert settings.technical_critical_indicators == ["close", "ema_fast", "ema_slow", "rsi", "macd_hist"]
    assert settings.regime_ohlcv_limit == 420
    assert settings.regime_min_ohlcv_rows == 140
    assert settings.regime_btc_ma_fast_period == 55
    assert settings.regime_btc_ma_slow_period == 210
    assert settings.regime_btc_slope_lookback == 10
    assert settings.regime_btc_slope_min_pct == 0.001
    assert settings.regime_btc_slope_good_pct == 0.02
    assert settings.regime_adx_period == 16
    assert settings.regime_adx_min == 20
    assert settings.regime_adx_strong == 34
    assert settings.regime_atr_period == 16
    assert settings.regime_drawdown_lookback == 30
    assert settings.regime_breadth_timeframe == "2h"
    assert settings.regime_breadth_symbol_count == 18
    assert settings.regime_breadth_min_samples == 6
    assert settings.regime_breadth_fast_period == 18
    assert settings.regime_breadth_slow_period == 48
    assert settings.regime_breadth_bullish_ratio == 0.7
    assert settings.regime_breadth_bearish_ratio == 0.3
    assert settings.regime_derivatives_symbol == "BTC/USDT:USDT"
    assert settings.regime_funding_abs_max == 0.002
    assert settings.regime_derivatives_neutral_score == 0.55
    assert settings.regime_fallback_penalty_points == 5.0
    assert settings.paper_bot_enabled is True
    assert settings.paper_initial_capital == 15000
    assert settings.paper_max_open_positions == 4
    assert settings.paper_risk_per_trade_pct == 0.02
    assert settings.paper_min_signal_score == 0.63
    assert settings.paper_require_step2_pass is True
    assert settings.paper_require_step3_pass is False
    assert settings.paper_require_window_complete is True
    assert settings.paper_atr_stop_multiplier == 1.8
    assert settings.paper_risk_reward_ratio == 2.3
    assert settings.paper_max_hold_minutes == 300
    assert settings.aggregation_bullish_threshold == 0.6
    assert settings.aggregation_stability_stddev_cap == 0.4
    assert settings.llm_provider == "gemini"
    assert settings.deepseek_enabled is True
    assert settings.deepseek_api_key == "test-key"
    assert settings.deepseek_base_url == "https://api.deepseek.com"
    assert settings.deepseek_model == "deepseek-chat"
    assert settings.deepseek_timeout_seconds == 25
    assert settings.deepseek_max_retries == 2
    assert settings.deepseek_shortlist_limit == 8
    assert settings.deepseek_min_aggregate_score == 0.62
    assert settings.deepseek_temperature == 0.15
    assert settings.gemini_api_key == "gemini-test-key"
    assert settings.gemini_base_url == "https://generativelanguage.googleapis.com"
    assert settings.gemini_model == "gemini-2.0-flash"
    assert settings.gemini_timeout_seconds == 22
    assert settings.gemini_max_retries == 3
    assert settings.gemini_temperature == 0.2


def test_settings_reject_unsupported_decision_horizon() -> None:
    with pytest.raises(ValueError, match="DECISION_HORIZON is invalid"):
        Settings(_env_file=None, decision_horizon="7w")


def test_settings_reject_invalid_llm_provider() -> None:
    with pytest.raises(ValueError, match="LLM_PROVIDER must be one of"):
        Settings(_env_file=None, llm_provider="openai")


def test_settings_reject_engine_max_signals_over_universe_size() -> None:
    with pytest.raises(ValueError, match="ENGINE_MAX_SIGNALS must be <= ENGINE_UNIVERSE_SIZE"):
        Settings(_env_file=None, engine_universe_size=10, engine_max_signals=20)


def test_settings_reject_overallocated_paper_risk() -> None:
    with pytest.raises(ValueError, match="PAPER_RISK_PER_TRADE_PCT \\* PAPER_MAX_OPEN_POSITIONS must be <= 1.0"):
        Settings(_env_file=None, paper_risk_per_trade_pct=0.3, paper_max_open_positions=4)

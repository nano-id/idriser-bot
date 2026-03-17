"""Runtime config store and time-gap aggregation tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.models.market_snapshot import MarketSnapshot
from app.models.runtime_config import RuntimeConfig
from app.pipeline.hourly_signal_aggregator import HourlySignalAggregator


def _snapshot_with_signal(*, symbol: str, timestamp: datetime, signal: float) -> MarketSnapshot:
    return MarketSnapshot(
        symbol=symbol,
        timestamp=timestamp,
        timeframe="5m",
        close=100.0,
        volume=1_000.0,
        volume_ratio=1.2,
        ema_fast=101.0,
        ema_slow=100.0,
        ema_slow_slope_pct=0.01,
        rsi=58.0,
        macd_hist=0.4,
        adx=24.0,
        atr_pct=0.01,
        bb_width=0.08,
        recent_high=101.0,
        breakout=False,
        spread_bps=5.0,
        raw_flags={"signal_override": signal},
    )


def test_runtime_config_store_save_load_and_reset(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        engine_enabled=False,
        engine_universe_size=30,
        engine_refresh_seconds=30,
        engine_include_step2=False,
        engine_include_step3=False,
        engine_include_ai_support=False,
        engine_max_signals=20,
        paper_bot_enabled=False,
        paper_initial_capital=12_000,
        paper_max_open_positions=4,
        paper_risk_per_trade_pct=0.02,
        paper_min_signal_score=0.60,
        paper_require_step2_pass=False,
        paper_require_step3_pass=True,
        paper_require_window_complete=True,
        paper_atr_stop_multiplier=1.7,
        paper_risk_reward_ratio=2.4,
        paper_max_hold_minutes=180,
        snapshot_interval_minutes=5,
        hourly_aggregation_window=12,
        hourly_min_snapshots=12,
        aggregation_bullish_threshold=0.55,
        deepseek_enabled=False,
        deepseek_shortlist_limit=10,
        deepseek_min_aggregate_score=0.55,
        deepseek_model="deepseek-chat",
        deepseek_timeout_seconds=20,
        gemini_model="gemini-2.0-flash",
        gemini_timeout_seconds=25,
    )
    store_path = tmp_path / "runtime_config.json"
    store = RuntimeConfigStore(path=store_path, settings=settings)

    defaults = store.load()
    assert defaults.hourly_aggregation_window == 12
    assert defaults.aggregation_bullish_threshold == 0.55
    assert defaults.llm_provider == "gemini"
    assert defaults.engine_enabled is False
    assert defaults.engine_universe_size == 30
    assert defaults.engine_refresh_seconds == 30
    assert defaults.engine_max_signals == 20
    assert defaults.paper_bot_enabled is False
    assert defaults.paper_initial_capital == 12_000
    assert defaults.paper_max_open_positions == 4
    assert defaults.paper_risk_per_trade_pct == 0.02
    assert defaults.paper_require_step3_pass is True
    assert defaults.paper_atr_stop_multiplier == 1.7
    assert defaults.paper_risk_reward_ratio == 2.4
    assert defaults.paper_max_hold_minutes == 180
    assert defaults.deepseek_enabled is False
    assert defaults.deepseek_shortlist_limit == 10
    assert defaults.deepseek_min_aggregate_score == 0.55
    assert defaults.gemini_model == "gemini-2.0-flash"
    assert defaults.gemini_timeout_seconds == 25
    assert "deepseek_api_key" not in defaults.model_dump()
    assert "gemini_api_key" not in defaults.model_dump()

    changed = defaults.model_copy(
        update={
            "engine_enabled": True,
            "engine_universe_size": 25,
            "engine_refresh_seconds": 40,
            "engine_include_step2": True,
            "engine_include_step3": True,
            "engine_include_ai_support": False,
            "engine_max_signals": 8,
            "paper_bot_enabled": True,
            "paper_initial_capital": 8_000,
            "paper_max_open_positions": 3,
            "paper_risk_per_trade_pct": 0.015,
            "paper_min_signal_score": 0.68,
            "paper_require_step2_pass": True,
            "paper_require_step3_pass": False,
            "paper_require_window_complete": True,
            "paper_atr_stop_multiplier": 2.0,
            "paper_risk_reward_ratio": 2.5,
            "paper_max_hold_minutes": 120,
            "hourly_aggregation_window": 18,
            "hourly_min_snapshots": 15,
            "aggregation_bullish_threshold": 0.62,
            "llm_provider": "deepseek",
            "deepseek_enabled": True,
            "deepseek_shortlist_limit": 5,
            "deepseek_min_aggregate_score": 0.65,
            "gemini_model": "gemini-2.0-flash",
            "gemini_timeout_seconds": 30,
        }
    )
    store.save(changed)

    loaded = store.load()
    assert loaded.hourly_aggregation_window == 18
    assert loaded.hourly_min_snapshots == 15
    assert loaded.aggregation_bullish_threshold == 0.62
    assert loaded.llm_provider == "deepseek"
    assert loaded.engine_enabled is True
    assert loaded.engine_universe_size == 25
    assert loaded.engine_refresh_seconds == 40
    assert loaded.engine_include_step2 is True
    assert loaded.engine_include_step3 is True
    assert loaded.engine_include_ai_support is False
    assert loaded.engine_max_signals == 8
    assert loaded.paper_bot_enabled is True
    assert loaded.paper_initial_capital == 8_000
    assert loaded.paper_max_open_positions == 3
    assert loaded.paper_risk_per_trade_pct == 0.015
    assert loaded.paper_min_signal_score == 0.68
    assert loaded.paper_require_step2_pass is True
    assert loaded.paper_require_step3_pass is False
    assert loaded.paper_require_window_complete is True
    assert loaded.paper_atr_stop_multiplier == 2.0
    assert loaded.paper_risk_reward_ratio == 2.5
    assert loaded.paper_max_hold_minutes == 120
    assert loaded.deepseek_enabled is True
    assert loaded.deepseek_shortlist_limit == 5
    assert loaded.deepseek_min_aggregate_score == 0.65
    assert loaded.gemini_model == "gemini-2.0-flash"
    assert loaded.gemini_timeout_seconds == 30
    assert "deepseek_api_key" not in loaded.model_dump()
    assert "gemini_api_key" not in loaded.model_dump()

    reset = store.reset_to_defaults()
    assert reset.hourly_aggregation_window == 12
    assert reset.hourly_min_snapshots == 12
    assert reset.aggregation_bullish_threshold == 0.55
    assert reset.llm_provider == "gemini"
    assert reset.engine_enabled is False
    assert reset.paper_bot_enabled is False
    assert reset.deepseek_enabled is False


def test_aggregation_detects_time_gap_even_with_12_snapshots() -> None:
    settings = Settings(
        _env_file=None,
        snapshot_interval_minutes=5,
        hourly_aggregation_window=12,
        hourly_min_snapshots=12,
    )
    aggregator = HourlySignalAggregator(settings=settings)
    base_time = datetime(2026, 1, 1, tzinfo=UTC)

    snapshots: list[MarketSnapshot] = []
    for idx in range(12):
        minute_offset = idx * 5
        if idx >= 6:
            minute_offset += 5
        snapshots.append(
            _snapshot_with_signal(
                symbol="BTC/USDT",
                timestamp=base_time + timedelta(minutes=minute_offset),
                signal=0.7,
            )
        )

    result = aggregator.aggregate(symbol="BTC/USDT", snapshots=snapshots)

    assert result.snapshot_count == 12
    assert result.expected_duration_minutes == 60
    assert result.actual_duration_minutes == 65
    assert result.aggregate_flags["insufficient_snapshots"] is False
    assert result.aggregate_flags["time_gap_detected"] is True
    assert result.aggregate_flags["window_complete"] is False
    assert result.aggregate_flags["fallback_used"] is True


def test_runtime_config_rejects_invalid_weight_sum() -> None:
    with pytest.raises(ValidationError, match="aggregation weights must sum to 1.0"):
        RuntimeConfig(
            aggregation_weight_trend=0.4,
            aggregation_weight_slope=0.2,
            aggregation_weight_rsi=0.2,
            aggregation_weight_macd=0.2,
            aggregation_weight_adx=0.1,
            aggregation_weight_volume=0.1,
            aggregation_weight_breakout=0.1,
        )


def test_runtime_config_rejects_min_snapshots_over_window() -> None:
    with pytest.raises(ValidationError, match="hourly_min_snapshots must be <= hourly_aggregation_window"):
        RuntimeConfig(hourly_aggregation_window=8, hourly_min_snapshots=12)


def test_runtime_config_rejects_engine_max_signals_over_universe_size() -> None:
    with pytest.raises(ValidationError, match="engine_max_signals must be <= engine_universe_size"):
        RuntimeConfig(engine_universe_size=10, engine_max_signals=25)


def test_runtime_config_rejects_invalid_regime_breadth_thresholds() -> None:
    with pytest.raises(ValidationError, match="regime_breadth_bearish_ratio must be < regime_breadth_bullish_ratio"):
        RuntimeConfig(regime_breadth_bearish_ratio=0.7, regime_breadth_bullish_ratio=0.6)


def test_runtime_config_rejects_overallocated_paper_risk() -> None:
    with pytest.raises(ValidationError, match="paper_risk_per_trade_pct \\* paper_max_open_positions must be <= 1.0"):
        RuntimeConfig(paper_risk_per_trade_pct=0.4, paper_max_open_positions=3)


def test_runtime_config_store_rejects_malformed_json(tmp_path: Path) -> None:
    settings = Settings(_env_file=None)
    path = tmp_path / "runtime_config.json"
    path.write_text("{bad-json", encoding="utf-8")
    store = RuntimeConfigStore(path=path, settings=settings)

    with pytest.raises(ValueError, match="Runtime config JSON is malformed"):
        store.load()


def test_runtime_config_store_rejects_invalid_payload(tmp_path: Path) -> None:
    settings = Settings(_env_file=None)
    path = tmp_path / "runtime_config.json"
    path.write_text('{"decision_horizon":"7w"}', encoding="utf-8")
    store = RuntimeConfigStore(path=path, settings=settings)

    with pytest.raises(ValueError, match="Runtime config payload is invalid"):
        store.load()

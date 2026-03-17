"""Hourly signal aggregator tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from statistics import pstdev

import pytest

from app.config.settings import Settings
from app.models.market_snapshot import MarketSnapshot
from app.pipeline.hourly_signal_aggregator import HourlySignalAggregator
from app.utils.indicators import clamp


def _snapshot_with_signal(*, symbol: str, index: int, signal: float) -> MarketSnapshot:
    return MarketSnapshot(
        symbol=symbol,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index * 5),
        timeframe="5m",
        close=100 + index,
        volume=1_000 + (index * 10),
        volume_ratio=1.2,
        ema_fast=100 + index,
        ema_slow=99 + index,
        ema_slow_slope_pct=0.01,
        rsi=60,
        macd_hist=0.5,
        adx=30,
        atr_pct=0.01,
        bb_width=0.08,
        recent_high=100 + index,
        breakout=False,
        spread_bps=4.0,
        raw_flags={"signal_override": signal},
    )


def test_aggregate_from_12_snapshots_computes_core_metrics() -> None:
    settings = Settings(
        _env_file=None,
        hourly_aggregation_window=12,
        hourly_min_snapshots=12,
    )
    aggregator = HourlySignalAggregator(settings=settings)
    signals = [0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9, 0.6, 0.55, 0.45, 0.65, 0.75]
    snapshots = [
        _snapshot_with_signal(symbol="BTC/USDT", index=idx, signal=value)
        for idx, value in enumerate(signals)
    ]

    result = aggregator.aggregate(symbol="BTC/USDT", snapshots=snapshots)

    expected_stddev = pstdev(signals)
    expected_stability = clamp(
        (0.65 * (1 - clamp(expected_stddev / settings.aggregation_stability_stddev_cap, 0.0, 1.0))) + 0.35,
        0.0,
        1.0,
    )

    assert result.snapshot_count == 12
    assert result.expected_duration_minutes == 60
    assert result.actual_duration_minutes == 60
    assert result.mean_signal == pytest.approx(0.575, abs=1e-6)
    assert result.median_signal == pytest.approx(0.6, abs=1e-6)
    assert result.bullish_ratio == pytest.approx(8 / 12, abs=1e-6)
    assert result.stability_score == pytest.approx(round(expected_stability, 6), abs=1e-6)
    assert result.aggregate_flags["insufficient_snapshots"] is False
    assert result.aggregate_flags["window_complete"] is True
    assert result.aggregate_flags["time_gap_detected"] is False


def test_aggregate_handles_missing_snapshots_with_safe_fallback() -> None:
    settings = Settings(
        _env_file=None,
        hourly_aggregation_window=12,
        hourly_min_snapshots=12,
    )
    aggregator = HourlySignalAggregator(settings=settings)
    signals = [0.80, 0.70, 0.78, 0.74, 0.76, 0.79, 0.81, 0.77]
    snapshots = [
        _snapshot_with_signal(symbol="ETH/USDT", index=idx, signal=value)
        for idx, value in enumerate(signals)
    ]

    result = aggregator.aggregate(symbol="ETH/USDT", snapshots=snapshots)

    assert result.snapshot_count == 8
    assert result.mean_signal == pytest.approx(sum(signals) / len(signals), abs=1e-6)
    assert result.aggregate_flags["insufficient_snapshots"] is True
    assert result.aggregate_flags["fallback_used"] is True
    assert 0 <= result.stability_score < 1


@pytest.mark.parametrize(
    ("horizon", "expected_required"),
    [
        ("15m", 3),
        ("30m", 6),
        ("1h", 12),
        ("4h", 48),
    ],
)
def test_required_snapshot_count_for_supported_horizons(horizon: str, expected_required: int) -> None:
    settings = Settings(_env_file=None, snapshot_interval_minutes=5, decision_horizon="1h")
    aggregator = HourlySignalAggregator(settings=settings)
    snapshots = [
        _snapshot_with_signal(symbol="BTC/USDT", index=idx, signal=0.7)
        for idx in range(60)
    ]

    result = aggregator.aggregate(symbol="BTC/USDT", snapshots=snapshots, decision_horizon=horizon)

    assert result.decision_horizon == horizon
    assert result.required_snapshots == expected_required
    assert result.window_size == expected_required
    assert result.snapshot_count == expected_required
    assert result.expected_duration_minutes == expected_required * settings.snapshot_interval_minutes


def test_unsupported_decision_horizon_raises_validation_error() -> None:
    settings = Settings(_env_file=None, snapshot_interval_minutes=5, decision_horizon="1h")
    aggregator = HourlySignalAggregator(settings=settings)
    snapshots = [_snapshot_with_signal(symbol="BTC/USDT", index=0, signal=0.5)]

    with pytest.raises(ValueError, match="Unsupported timeframe format"):
        aggregator.aggregate(symbol="BTC/USDT", snapshots=snapshots, decision_horizon="7w")

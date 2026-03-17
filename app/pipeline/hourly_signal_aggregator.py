"""Aggregate hourly signals from rolling market snapshots."""

from __future__ import annotations

from statistics import fmean, median, pstdev
from datetime import datetime
from typing import Sequence

from app.config.settings import Settings
from app.models.hourly_signal import HourlySignal
from app.models.market_snapshot import MarketSnapshot
from app.utils.indicators import clamp
from app.utils.timeframe import normalize_timeframe, required_snapshots_for_horizon


class HourlySignalAggregator:
    """Convert recent snapshots into decision-horizon aggregate signals."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings

    def aggregate(
        self,
        *,
        symbol: str,
        snapshots: Sequence[MarketSnapshot],
        decision_horizon: str | None = None,
    ) -> HourlySignal:
        """Aggregate latest configured window for one symbol and horizon."""
        horizon = self._resolve_horizon(decision_horizon)
        required_snapshots = required_snapshots_for_horizon(
            decision_horizon=horizon,
            snapshot_interval_minutes=self.settings.snapshot_interval_minutes,
        )
        sorted_snapshots = sorted(
            (item for item in snapshots if item.symbol == symbol),
            key=lambda item: item.timestamp,
        )
        window = list(sorted_snapshots[-required_snapshots:])
        signal_values = [self._snapshot_signal(snapshot) for snapshot in window]
        window_start = window[0].timestamp if window else None
        window_end = window[-1].timestamp if window else None
        expected_duration_minutes = self.settings.snapshot_interval_minutes * required_snapshots
        actual_duration_minutes = self._actual_duration_minutes(window)
        time_gap_detected = self._has_time_gap(window)
        duration_deviation_minutes = abs(actual_duration_minutes - expected_duration_minutes)
        duration_tolerance_minutes = max(1, self.settings.snapshot_interval_minutes // 2)
        insufficient_snapshots = len(window) < required_snapshots
        window_complete = bool(
            len(window) >= required_snapshots
            and not time_gap_detected
            and duration_deviation_minutes <= duration_tolerance_minutes
        )
        fallback_used = insufficient_snapshots or time_gap_detected or not window_complete

        if signal_values:
            mean_signal = fmean(signal_values)
            median_signal = float(median(signal_values))
            signal_stddev = float(pstdev(signal_values)) if len(signal_values) > 1 else 0.0
            bullish_ratio = (
                sum(1 for item in signal_values if item >= self.settings.aggregation_bullish_threshold)
                / len(signal_values)
            )
            last_3_slope = self._last_three_slope(signal_values)
            stability_score = self._stability_score(
                snapshot_count=len(window),
                required_snapshots=required_snapshots,
                signal_stddev=signal_stddev,
            )
            feature_snapshot = self._feature_snapshot(window=window, signal_values=signal_values)
        else:
            mean_signal = 0.0
            median_signal = 0.0
            signal_stddev = 0.0
            bullish_ratio = 0.0
            last_3_slope = 0.0
            stability_score = 0.0
            feature_snapshot = {"latest_timestamp": None}

        aggregate_flags: dict[str, bool | int | float | str | None] = {
            "window_complete": window_complete,
            "insufficient_snapshots": insufficient_snapshots,
            "time_gap_detected": time_gap_detected,
            "fallback_used": fallback_used,
            "bullish_bias": bullish_ratio >= self.settings.aggregation_bullish_threshold,
            "signal_threshold": self.settings.aggregation_bullish_threshold,
            "duration_deviation_minutes": duration_deviation_minutes,
            "duration_tolerance_minutes": duration_tolerance_minutes,
            "required_snapshots": required_snapshots,
        }

        return HourlySignal(
            symbol=symbol,
            decision_horizon=horizon,
            base_snapshot_timeframe=self.settings.snapshot_timeframe,
            required_snapshots=required_snapshots,
            window_size=required_snapshots,
            snapshot_count=len(window),
            window_start=window_start,
            window_end=window_end,
            expected_duration_minutes=expected_duration_minutes,
            actual_duration_minutes=actual_duration_minutes,
            mean_signal=round(mean_signal, 6),
            median_signal=round(median_signal, 6),
            signal_stddev=round(signal_stddev, 6),
            bullish_ratio=round(bullish_ratio, 6),
            last_3_slope=round(last_3_slope, 6),
            stability_score=round(stability_score, 6),
            fallback_used=fallback_used,
            latest_breakout=bool(feature_snapshot.get("latest_breakout", False)),
            aggregate_flags=aggregate_flags,
            feature_snapshot=feature_snapshot,
        )

    def aggregate_many(
        self,
        *,
        snapshots_by_symbol: dict[str, Sequence[MarketSnapshot]],
        decision_horizon: str | None = None,
    ) -> dict[str, HourlySignal]:
        """Aggregate signals for all symbols in payload."""
        result: dict[str, HourlySignal] = {}
        for symbol, snapshots in snapshots_by_symbol.items():
            result[symbol] = self.aggregate(
                symbol=symbol,
                snapshots=snapshots,
                decision_horizon=decision_horizon,
            )
        return result

    def _snapshot_signal(self, snapshot: MarketSnapshot) -> float:
        raw_override = snapshot.raw_flags.get("signal_override")
        if isinstance(raw_override, (float, int)):
            return clamp(float(raw_override), 0.0, 1.0)

        weighted_parts: list[tuple[float, float]] = []
        weights = self.settings.aggregation_weights
        trend = self._trend_component(snapshot)
        if trend is not None:
            weighted_parts.append((weights["trend"], trend))

        slope = self._slope_component(snapshot)
        if slope is not None:
            weighted_parts.append((weights["slope"], slope))

        rsi_component = self._rsi_component(snapshot)
        if rsi_component is not None:
            weighted_parts.append((weights["rsi"], rsi_component))

        macd_component = self._macd_component(snapshot)
        if macd_component is not None:
            weighted_parts.append((weights["macd"], macd_component))

        adx_component = self._adx_component(snapshot)
        if adx_component is not None:
            weighted_parts.append((weights["adx"], adx_component))

        volume_component = self._volume_component(snapshot)
        if volume_component is not None:
            weighted_parts.append((weights["volume"], volume_component))

        weighted_parts.append((weights["breakout"], 1.0 if snapshot.breakout else 0.0))

        weight_sum = sum(weight for weight, _ in weighted_parts)
        if weight_sum <= 0:
            return 0.0
        score = sum(weight * value for weight, value in weighted_parts) / weight_sum
        return clamp(score, 0.0, 1.0)

    @staticmethod
    def _trend_component(snapshot: MarketSnapshot) -> float | None:
        if snapshot.ema_fast is None or snapshot.ema_slow is None:
            return None
        return 1.0 if snapshot.ema_fast > snapshot.ema_slow else 0.0

    def _slope_component(self, snapshot: MarketSnapshot) -> float | None:
        if snapshot.ema_slow_slope_pct is None:
            return None
        min_pct = self.settings.technical_ma_slope_min_pct
        strong_pct = self.settings.technical_ma_slope_good_pct
        if strong_pct <= min_pct:
            return 1.0 if snapshot.ema_slow_slope_pct >= min_pct else 0.0
        return clamp((snapshot.ema_slow_slope_pct - min_pct) / (strong_pct - min_pct), 0.0, 1.0)

    @staticmethod
    def _rsi_component(snapshot: MarketSnapshot) -> float | None:
        if snapshot.rsi is None:
            return None
        return clamp((snapshot.rsi - 40) / 30, 0.0, 1.0)

    @staticmethod
    def _macd_component(snapshot: MarketSnapshot) -> float | None:
        if snapshot.macd_hist is None:
            return None
        return 1.0 if snapshot.macd_hist > 0 else 0.0

    def _adx_component(self, snapshot: MarketSnapshot) -> float | None:
        if snapshot.adx is None:
            return None
        min_value = self.settings.technical_adx_min
        strong_value = self.settings.technical_adx_strong
        if strong_value <= min_value:
            return 1.0 if snapshot.adx >= min_value else 0.0
        return clamp((snapshot.adx - min_value) / (strong_value - min_value), 0.0, 1.0)

    def _volume_component(self, snapshot: MarketSnapshot) -> float | None:
        if snapshot.volume_ratio is None:
            return None
        min_value = self.settings.technical_volume_ratio_min
        strong_value = self.settings.technical_volume_ratio_strong
        if strong_value <= min_value:
            return 1.0 if snapshot.volume_ratio >= min_value else 0.0
        return clamp((snapshot.volume_ratio - min_value) / (strong_value - min_value), 0.0, 1.0)

    @staticmethod
    def _last_three_slope(signal_values: Sequence[float]) -> float:
        if len(signal_values) < 3:
            return 0.0
        last_three = signal_values[-3:]
        return (last_three[-1] - last_three[0]) / 2

    def _stability_score(self, *, snapshot_count: int, required_snapshots: int, signal_stddev: float) -> float:
        completeness = clamp(snapshot_count / max(1, required_snapshots), 0.0, 1.0)
        consistency = 1 - clamp(signal_stddev / self.settings.aggregation_stability_stddev_cap, 0.0, 1.0)
        return clamp((0.65 * consistency) + (0.35 * completeness), 0.0, 1.0)

    def _has_time_gap(self, window: Sequence[MarketSnapshot]) -> bool:
        if len(window) < 2:
            return False
        expected_step_seconds = self.settings.snapshot_interval_minutes * 60
        allowed_gap_seconds = int(expected_step_seconds * 1.5)
        for previous, current in zip(window, window[1:]):
            diff_seconds = int((current.timestamp - previous.timestamp).total_seconds())
            if diff_seconds > allowed_gap_seconds:
                return True
        return False

    def _actual_duration_minutes(self, window: Sequence[MarketSnapshot]) -> int:
        if not window:
            return 0
        if len(window) == 1:
            return self.settings.snapshot_interval_minutes
        start = window[0].timestamp
        end = window[-1].timestamp
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            return 0
        covered = int((end - start).total_seconds() // 60)
        return covered + self.settings.snapshot_interval_minutes

    def _resolve_horizon(self, decision_horizon: str | None) -> str:
        horizon_candidate = decision_horizon or self.settings.decision_horizon
        normalized = normalize_timeframe(horizon_candidate)
        if normalized not in self.settings.supported_decision_horizons:
            msg = f"Unsupported decision horizon: {normalized}"
            raise ValueError(msg)
        return normalized

    @staticmethod
    def _feature_snapshot(
        *,
        window: Sequence[MarketSnapshot],
        signal_values: Sequence[float],
    ) -> dict[str, float | int | str | bool | None]:
        latest = window[-1]
        return {
            "latest_timestamp": latest.timestamp.isoformat(),
            "timeframe": latest.timeframe,
            "latest_close": latest.close,
            "latest_atr_pct": latest.atr_pct,
            "latest_volume_ratio": latest.volume_ratio,
            "latest_rsi": latest.rsi,
            "latest_macd_hist": latest.macd_hist,
            "latest_adx": latest.adx,
            "latest_breakout": latest.breakout,
            "signal_min": round(min(signal_values), 6),
            "signal_max": round(max(signal_values), 6),
        }

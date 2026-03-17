"""Collect per-symbol market snapshots from CCXT OHLCV data."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pandas as pd

from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.config.settings import Settings
from app.models.market_snapshot import MarketSnapshot
from app.utils.indicators import adx, atr, bollinger_bands, ema, macd, ohlcv_to_dataframe, relative_slope_pct, rsi


LOGGER = logging.getLogger(__name__)


class MarketSnapshotCollector:
    """Build 5m snapshot rows from exchange candles."""

    def __init__(
        self,
        *,
        settings: Settings,
        market_data_client: CCXTMarketDataClient,
    ) -> None:
        self.settings = settings
        self.market_data_client = market_data_client

    def collect_latest(self, symbol: str) -> MarketSnapshot | None:
        """Collect only the latest available snapshot for a symbol."""
        snapshots = self.collect_recent(symbol=symbol, snapshot_count=1)
        return snapshots[-1] if snapshots else None

    def collect_recent(self, *, symbol: str, snapshot_count: int | None = None) -> list[MarketSnapshot]:
        """Collect latest N snapshots by reusing one OHLCV pull."""
        target_count = snapshot_count or self.settings.hourly_aggregation_window
        if target_count <= 0:
            return []

        limit = self._required_history_rows(target_count)
        try:
            rows = self.market_data_client.fetch_ohlcv(
                symbol=symbol,
                timeframe=self.settings.snapshot_timeframe,
                limit=limit,
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Snapshot OHLCV alinamadi %s: %s", symbol, exc)
            return []

        frame = self._build_indicator_frame(ohlcv_to_dataframe(rows))
        if frame.empty:
            return []

        start_index = max(0, len(frame) - target_count)
        snapshots: list[MarketSnapshot] = []
        for idx in range(start_index, len(frame)):
            snapshots.append(self._build_snapshot(symbol=symbol, frame=frame, index=idx))
        return snapshots

    def collect_for_symbols(
        self,
        *,
        symbols: list[str],
        snapshot_count: int | None = None,
    ) -> dict[str, list[MarketSnapshot]]:
        """Collect snapshots for multiple symbols."""
        payload: dict[str, list[MarketSnapshot]] = {}
        for symbol in symbols:
            payload[symbol] = self.collect_recent(symbol=symbol, snapshot_count=snapshot_count)
        return payload

    def _build_indicator_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        frame = df.copy()
        frame["ema_fast"] = ema(frame["close"], self.settings.technical_ma_fast_period)
        frame["ema_slow"] = ema(frame["close"], self.settings.technical_ma_slow_period)
        frame["rsi"] = rsi(frame["close"], self.settings.technical_rsi_period)
        _, _, frame["macd_hist"] = macd(
            frame["close"],
            self.settings.technical_macd_fast,
            self.settings.technical_macd_slow,
            self.settings.technical_macd_signal,
        )
        frame["atr"] = atr(
            frame["high"],
            frame["low"],
            frame["close"],
            self.settings.technical_atr_period,
        )
        frame["atr_pct"] = frame["atr"] / frame["close"].replace(0, pd.NA)
        adx_series, _, _ = adx(
            frame["high"],
            frame["low"],
            frame["close"],
            self.settings.technical_adx_period,
        )
        frame["adx"] = adx_series
        _, _, _, frame["bb_width"] = bollinger_bands(
            frame["close"],
            self.settings.technical_bbands_period,
            self.settings.technical_bbands_stddev,
        )
        frame["volume_sma"] = frame["volume"].rolling(
            window=self.settings.technical_volume_ma_period,
            min_periods=self.settings.technical_volume_ma_period,
        ).mean()
        return frame

    def _build_snapshot(self, *, symbol: str, frame: pd.DataFrame, index: int) -> MarketSnapshot:
        row = frame.iloc[index]
        lookback_frame = frame.iloc[: index + 1]

        close = self._safe_float(row.get("close"))
        volume = self._safe_float(row.get("volume"))
        volume_sma = self._safe_float(row.get("volume_sma"))
        volume_ratio = (volume / volume_sma) if volume is not None and volume_sma and volume_sma > 0 else None

        recent_high = self._recent_high(frame=frame, index=index)
        breakout = bool(
            close is not None
            and recent_high is not None
            and close > recent_high * (1 + self.settings.technical_breakout_buffer_pct)
        )

        ema_slow_slope_pct = relative_slope_pct(
            lookback_frame["ema_slow"],
            self.settings.technical_ma_slope_lookback,
        )
        spread_bps = self._candle_range_bps(
            high=self._safe_float(row.get("high")),
            low=self._safe_float(row.get("low")),
            close=close,
        )

        core_values = [
            close,
            volume,
            self._safe_float(row.get("ema_fast")),
            self._safe_float(row.get("ema_slow")),
            self._safe_float(row.get("rsi")),
            self._safe_float(row.get("macd_hist")),
            self._safe_float(row.get("adx")),
            self._safe_float(row.get("atr_pct")),
            self._safe_float(row.get("bb_width")),
            recent_high,
        ]
        missing_core_count = sum(1 for item in core_values if item is None)

        return MarketSnapshot(
            symbol=symbol,
            timestamp=self._safe_timestamp(row.get("timestamp")),
            timeframe=self.settings.snapshot_timeframe,
            close=close,
            volume=volume,
            volume_ratio=self._round_or_none(volume_ratio, 6),
            ema_fast=self._safe_float(row.get("ema_fast")),
            ema_slow=self._safe_float(row.get("ema_slow")),
            ema_slow_slope_pct=self._round_or_none(ema_slow_slope_pct, 6),
            rsi=self._safe_float(row.get("rsi")),
            macd_hist=self._safe_float(row.get("macd_hist")),
            adx=self._safe_float(row.get("adx")),
            atr_pct=self._safe_float(row.get("atr_pct")),
            bb_width=self._safe_float(row.get("bb_width")),
            recent_high=recent_high,
            breakout=breakout,
            spread_bps=self._round_or_none(spread_bps, 3),
            raw_flags={
                "data_source": "ccxt_ohlcv",
                "indicator_fallback": len(frame) < self.settings.technical_min_ohlcv_rows,
                "missing_core_count": missing_core_count,
                "breakout": breakout,
                "spread_proxy_used": True,
            },
        )

    def _recent_high(self, *, frame: pd.DataFrame, index: int) -> float | None:
        lookback = self.settings.technical_breakout_lookback
        start = max(0, index - lookback)
        window = frame.iloc[start:index]
        if window.empty:
            return None
        return self._safe_float(window["high"].max())

    def _required_history_rows(self, snapshot_count: int) -> int:
        indicator_warmup = max(
            self.settings.technical_ma_slow_period + self.settings.technical_ma_slope_lookback,
            self.settings.technical_macd_slow + self.settings.technical_macd_signal,
            self.settings.technical_bbands_period,
            self.settings.technical_rsi_period,
            self.settings.technical_adx_period,
            self.settings.technical_atr_period,
            self.settings.technical_volume_ma_period,
            self.settings.technical_breakout_lookback,
        )
        minimum = max(self.settings.technical_min_ohlcv_rows, snapshot_count)
        return max(minimum, indicator_warmup + snapshot_count + 1)

    @staticmethod
    def _candle_range_bps(*, high: float | None, low: float | None, close: float | None) -> float | None:
        if high is None or low is None or close is None or close <= 0:
            return None
        return ((high - low) / close) * 10_000

    @staticmethod
    def _safe_timestamp(value: object) -> datetime:
        if isinstance(value, pd.Timestamp):
            if value.tzinfo is None:
                return value.tz_localize(UTC).to_pydatetime()
            return value.to_pydatetime()
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)
            return value
        return datetime.now(tz=UTC)

    @staticmethod
    def _safe_float(value: object) -> float | None:
        try:
            if value is None or pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _round_or_none(value: float | None, digits: int) -> float | None:
        if value is None:
            return None
        return round(value, digits)

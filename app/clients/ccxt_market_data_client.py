"""CCXT market-data client for OHLCV retrieval."""

from __future__ import annotations

import logging
import time
from datetime import datetime

import ccxt


LOGGER = logging.getLogger(__name__)


class CCXTMarketDataClient:
    """Fetch OHLCV candles with retry support."""

    def __init__(
        self,
        *,
        exchange_id: str,
        timeout_seconds: int,
        max_retries: int,
        backoff_seconds: float,
    ) -> None:
        if not hasattr(ccxt, exchange_id):
            msg = f"Exchange '{exchange_id}' is not supported by ccxt"
            raise ValueError(msg)

        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class(
            {
                "enableRateLimit": True,
                "timeout": timeout_seconds * 1000,
            }
        )
        self.exchange_id = exchange_id
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self._markets_loaded = False

    def fetch_ohlcv(self, *, symbol: str, timeframe: str, limit: int) -> list[list[float]]:
        """Fetch OHLCV candles for a symbol and timeframe."""
        self._ensure_markets_loaded()
        return self._fetch_ohlcv_with_retry(symbol=symbol, timeframe=timeframe, limit=limit)

    def fetch_ohlcv_range(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: datetime | int,
        end: datetime | int,
        limit_per_call: int = 1000,
    ) -> list[list[float]]:
        """Fetch OHLCV rows across a historical time range using pagination."""
        self._ensure_markets_loaded()
        start_ms = self._to_milliseconds(start)
        end_ms = self._to_milliseconds(end)
        if end_ms <= start_ms:
            return []

        rows: list[list[float]] = []
        seen_timestamps: set[int] = set()
        cursor = start_ms
        last_timestamp: int | None = None
        timeframe_ms = self.exchange.parse_timeframe(timeframe) * 1000

        while cursor <= end_ms:
            batch = self._fetch_ohlcv_with_retry(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit_per_call,
                since=cursor,
            )
            if not batch:
                break

            progressed = False
            for row in batch:
                if not row:
                    continue
                timestamp = int(row[0])
                if timestamp > end_ms:
                    continue
                if timestamp < start_ms or timestamp in seen_timestamps:
                    continue
                rows.append(row)
                seen_timestamps.add(timestamp)
                progressed = True
                last_timestamp = timestamp

            if last_timestamp is None:
                break

            next_cursor = last_timestamp + max(1, timeframe_ms)
            if not progressed or next_cursor <= cursor:
                break
            cursor = next_cursor

        return rows

    def _fetch_ohlcv_with_retry(
        self,
        *,
        symbol: str,
        timeframe: str,
        limit: int,
        since: int | None = None,
    ) -> list[list[float]]:
        """Fetch OHLCV with retry support and optional pagination cursor."""
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                data = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=limit,
                )
                return data or []
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                LOGGER.warning(
                    "OHLCV fetch failed %s/%s for %s %s on %s: %s",
                    attempt,
                    self.max_retries + 1,
                    symbol,
                    timeframe,
                    self.exchange_id,
                    exc,
                )
                if attempt <= self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)

        msg = f"Failed to fetch OHLCV for {symbol} {timeframe}: {last_error}"
        raise RuntimeError(msg)

    def fetch_funding_rate(self, *, symbol: str) -> float | None:
        """Fetch current funding rate if exchange supports it."""
        self._ensure_markets_loaded()
        try:
            has_method = self.exchange.has.get("fetchFundingRate", False)
        except Exception:  # noqa: BLE001
            has_method = False
        if not has_method:
            return None

        try:
            payload = self.exchange.fetch_funding_rate(symbol)
            if not isinstance(payload, dict):
                return None
            value = payload.get("fundingRate")
            if value is None:
                return None
            return float(value)
        except Exception as exc:  # noqa: BLE001
            LOGGER.info("Funding rate unavailable for %s on %s: %s", symbol, self.exchange_id, exc)
            return None

    def fetch_open_interest(self, *, symbol: str) -> float | None:
        """Fetch open interest if exchange supports it."""
        self._ensure_markets_loaded()
        try:
            has_method = self.exchange.has.get("fetchOpenInterest", False)
        except Exception:  # noqa: BLE001
            has_method = False
        if not has_method:
            return None

        try:
            payload = self.exchange.fetch_open_interest(symbol)
            if not isinstance(payload, dict):
                return None
            value = payload.get("openInterestAmount")
            if value is None:
                value = payload.get("openInterestValue")
            if value is None:
                return None
            return float(value)
        except Exception as exc:  # noqa: BLE001
            LOGGER.info("Open interest unavailable for %s on %s: %s", symbol, self.exchange_id, exc)
            return None

    def close(self) -> None:
        """Close underlying CCXT client session."""
        try:
            self.exchange.close()
        except Exception:  # noqa: BLE001
            pass

    def _ensure_markets_loaded(self) -> None:
        if self._markets_loaded:
            return
        self.exchange.load_markets()
        self._markets_loaded = True

    @staticmethod
    def _to_milliseconds(value: datetime | int) -> int:
        if isinstance(value, datetime):
            return int(value.timestamp() * 1000)
        return int(value)

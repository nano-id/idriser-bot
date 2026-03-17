"""Historical replay market-data client backed by preloaded OHLCV rows."""

from __future__ import annotations

from datetime import UTC, datetime


class ReplayMarketDataClient:
    """Serve rolling historical OHLCV windows up to the active replay timestamp."""

    def __init__(
        self,
        *,
        rows_by_key: dict[tuple[str, str], list[list[float]]],
        funding_by_symbol: dict[str, float] | None = None,
        open_interest_by_symbol: dict[str, float] | None = None,
    ) -> None:
        self.rows_by_key = {
            (symbol, timeframe): sorted(rows, key=lambda item: item[0])
            for (symbol, timeframe), rows in rows_by_key.items()
        }
        self.funding_by_symbol = funding_by_symbol or {}
        self.open_interest_by_symbol = open_interest_by_symbol or {}
        self._current_time = datetime.now(tz=UTC)

    def set_current_time(self, current_time: datetime) -> None:
        """Advance replay time to the current candle boundary."""
        self._current_time = current_time.astimezone(UTC)

    def fetch_ohlcv(self, *, symbol: str, timeframe: str, limit: int) -> list[list[float]]:
        """Return latest rows available up to the active replay timestamp."""
        key = (symbol, timeframe)
        rows = self.rows_by_key.get(key, [])
        if limit <= 0 or not rows:
            return []
        cutoff_ms = int(self._current_time.timestamp() * 1000)
        visible = [row for row in rows if int(row[0]) <= cutoff_ms]
        return visible[-limit:]

    def fetch_funding_rate(self, *, symbol: str) -> float | None:
        """Return replay funding rate if provided, otherwise unavailable."""
        return self.funding_by_symbol.get(symbol)

    def fetch_open_interest(self, *, symbol: str) -> float | None:
        """Return replay open interest if provided, otherwise unavailable."""
        return self.open_interest_by_symbol.get(symbol)


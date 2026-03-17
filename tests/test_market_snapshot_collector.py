"""Market snapshot collector tests with mocked OHLCV."""

from __future__ import annotations

from app.config.settings import Settings
from app.pipeline.market_snapshot_collector import MarketSnapshotCollector


class FakeMarketDataClient:
    """Simple CCXT client stub for snapshot tests."""

    def __init__(self, data_map: dict[tuple[str, str], list[list[float]]], *, should_fail: bool = False) -> None:
        self.data_map = data_map
        self.should_fail = should_fail

    def fetch_ohlcv(self, *, symbol: str, timeframe: str, limit: int) -> list[list[float]]:
        if self.should_fail:
            msg = "forced fetch failure"
            raise RuntimeError(msg)
        return self.data_map.get((symbol, timeframe), [])[:limit]


def _build_ohlcv(
    *,
    length: int,
    start_price: float,
    drift: float,
    final_spike_pct: float = 0.0,
) -> list[list[float]]:
    rows: list[list[float]] = []
    close = start_price
    base_volume = 1_000.0
    for idx in range(length):
        close = close + drift
        if idx == length - 1 and final_spike_pct:
            close = close * (1 + final_spike_pct)
        open_price = close * 0.998
        high = close * 1.004
        low = close * 0.996
        volume = base_volume + idx * 6
        rows.append([1_700_000_000_000 + idx * 300_000, open_price, high, low, close, volume])
    return rows


def test_collect_recent_builds_12_snapshots_with_expected_fields() -> None:
    settings = Settings(_env_file=None, snapshot_timeframe="5m", technical_min_ohlcv_rows=50)
    rows = _build_ohlcv(length=200, start_price=100, drift=0.7, final_spike_pct=0.015)
    client = FakeMarketDataClient({("BTC/USDT", "5m"): rows})
    collector = MarketSnapshotCollector(settings=settings, market_data_client=client)  # type: ignore[arg-type]

    snapshots = collector.collect_recent(symbol="BTC/USDT", snapshot_count=12)

    assert len(snapshots) == 12
    latest = snapshots[-1]
    assert latest.symbol == "BTC/USDT"
    assert latest.timeframe == "5m"
    assert latest.close is not None
    assert latest.volume is not None
    assert latest.ema_fast is not None
    assert latest.ema_slow is not None
    assert latest.rsi is not None
    assert latest.macd_hist is not None
    assert latest.adx is not None
    assert latest.atr_pct is not None
    assert latest.bb_width is not None
    assert latest.raw_flags["data_source"] == "ccxt_ohlcv"


def test_collect_recent_safe_fallback_on_fetch_failure() -> None:
    settings = Settings(_env_file=None, snapshot_timeframe="5m")
    client = FakeMarketDataClient({}, should_fail=True)
    collector = MarketSnapshotCollector(settings=settings, market_data_client=client)  # type: ignore[arg-type]

    snapshots = collector.collect_recent(symbol="ETH/USDT", snapshot_count=12)

    assert snapshots == []

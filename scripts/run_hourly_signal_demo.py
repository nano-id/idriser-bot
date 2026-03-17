"""Demo: collect 5m snapshots and build 1h aggregates for major pairs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.config.settings import Settings
from app.pipeline.hourly_signal_aggregator import HourlySignalAggregator
from app.pipeline.market_snapshot_collector import MarketSnapshotCollector


def main() -> None:
    settings = Settings()
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]

    market_data_client = CCXTMarketDataClient(
        exchange_id=settings.exchange_id,
        timeout_seconds=settings.request_timeout_seconds,
        max_retries=settings.request_max_retries,
        backoff_seconds=settings.request_backoff_seconds,
    )
    collector = MarketSnapshotCollector(settings=settings, market_data_client=market_data_client)
    aggregator = HourlySignalAggregator(settings=settings)

    payload: dict[str, object] = {}
    try:
        for symbol in symbols:
            snapshots = collector.collect_recent(
                symbol=symbol,
                snapshot_count=settings.hourly_aggregation_window,
            )
            hourly_signal = aggregator.aggregate(symbol=symbol, snapshots=snapshots)
            payload[symbol] = {
                "snapshot_count": len(snapshots),
                "snapshots": [item.model_dump(mode="json") for item in snapshots],
                "hourly_signal": hourly_signal.model_dump(mode="json"),
            }
    finally:
        market_data_client.close()

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

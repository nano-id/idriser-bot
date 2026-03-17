"""Demo: build multi-horizon aggregate signals for one symbol."""

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
from app.utils.timeframe import required_snapshots_for_horizon


def main() -> None:
    settings = Settings()
    symbol = "BTC/USDT"
    horizons = ["15m", "1h", "4h"]

    required_counts = {
        horizon: required_snapshots_for_horizon(
            decision_horizon=horizon,
            snapshot_interval_minutes=settings.snapshot_interval_minutes,
        )
        for horizon in horizons
    }
    max_required = max(required_counts.values())

    market_data_client = CCXTMarketDataClient(
        exchange_id=settings.exchange_id,
        timeout_seconds=settings.request_timeout_seconds,
        max_retries=settings.request_max_retries,
        backoff_seconds=settings.request_backoff_seconds,
    )
    collector = MarketSnapshotCollector(settings=settings, market_data_client=market_data_client)
    aggregator = HourlySignalAggregator(settings=settings)

    try:
        snapshots = collector.collect_recent(symbol=symbol, snapshot_count=max_required)
        horizons_payload: dict[str, object] = {}
        for horizon in horizons:
            signal = aggregator.aggregate(
                symbol=symbol,
                snapshots=snapshots,
                decision_horizon=horizon,
            )
            horizons_payload[horizon] = signal.model_dump(mode="json")
    finally:
        market_data_client.close()

    print(
        json.dumps(
            {
                "symbol": symbol,
                "snapshot_count": len(snapshots),
                "required_snapshots": required_counts,
                "signals": horizons_payload,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

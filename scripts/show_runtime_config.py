"""Show effective runtime config used by snapshot/aggregation layers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.utils.timeframe import required_snapshots_for_horizon, timeframe_to_minutes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show runtime config overrides")
    parser.add_argument(
        "--path",
        type=str,
        default="runtime/runtime_config.json",
        help="Runtime config JSON file path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings()
    store = RuntimeConfigStore(path=args.path, settings=settings)
    runtime_config = store.load()
    horizon_minutes = timeframe_to_minutes(runtime_config.decision_horizon)
    required_snapshots = required_snapshots_for_horizon(
        decision_horizon=runtime_config.decision_horizon,
        snapshot_interval_minutes=runtime_config.snapshot_interval_minutes,
    )
    print(
        json.dumps(
            {
                "path": str(Path(args.path).resolve()),
                "decision_horizon": runtime_config.decision_horizon,
                "supported_decision_horizons": runtime_config.supported_decision_horizons,
                "decision_horizon_minutes": horizon_minutes,
                "required_snapshots": required_snapshots,
                "runtime_config": runtime_config.model_dump(mode="json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

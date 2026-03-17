"""Demo: provider-agnostic optional AI support scoring for shortlisted symbols."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import Settings
from app.models.hourly_signal import HourlySignal
from app.pipeline.ai_support_service import AISupportService


def _sample_signal(
    *,
    symbol: str,
    horizon: str,
    mean_signal: float,
    bullish_ratio: float,
    stability_score: float,
    breakout: bool,
) -> HourlySignal:
    now = datetime.now(tz=UTC)
    return HourlySignal(
        symbol=symbol,
        decision_horizon=horizon,
        base_snapshot_timeframe="5m",
        required_snapshots=12,
        window_size=12,
        snapshot_count=12,
        window_start=now,
        window_end=now,
        expected_duration_minutes=60,
        actual_duration_minutes=60,
        mean_signal=mean_signal,
        median_signal=mean_signal,
        signal_stddev=0.08,
        bullish_ratio=bullish_ratio,
        last_3_slope=0.02,
        stability_score=stability_score,
        aggregate_flags={"window_complete": True},
        feature_snapshot={"latest_breakout": breakout},
    )


def main() -> None:
    settings = Settings()
    service = AISupportService(settings=settings)
    horizon = settings.decision_horizon

    aggregate_signals = [
        _sample_signal(
            symbol="BTC/USDT",
            horizon=horizon,
            mean_signal=0.74,
            bullish_ratio=0.83,
            stability_score=0.89,
            breakout=True,
        ),
        _sample_signal(
            symbol="ETH/USDT",
            horizon=horizon,
            mean_signal=0.68,
            bullish_ratio=0.75,
            stability_score=0.84,
            breakout=False,
        ),
        _sample_signal(
            symbol="BNB/USDT",
            horizon=horizon,
            mean_signal=0.61,
            bullish_ratio=0.67,
            stability_score=0.79,
            breakout=False,
        ),
    ]

    if not settings.llm_enabled:
        print(
            json.dumps(
                {
                    "status": "skipped",
                    "reason": "llm_disabled",
                    "llm_provider": settings.llm_provider,
                    "llm_enabled": settings.llm_enabled,
                    "symbol_count": len(aggregate_signals),
                },
                indent=2,
            )
        )
        return

    results = service.evaluate_shortlist(aggregate_signals=aggregate_signals)
    print(
        json.dumps(
            {
                "status": "ok",
                "llm_provider": settings.llm_provider,
                "llm_enabled": settings.llm_enabled,
                "llm_configured": settings.llm_configured,
                "result_count": len(results),
                "results": [item.model_dump(mode="json") for item in results],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


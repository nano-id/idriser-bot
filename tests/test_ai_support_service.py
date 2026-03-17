"""Provider-agnostic AI support service tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.clients.ai_client_factory import create_ai_support_client
from app.clients.gemini_client import GeminiClient
from app.config.settings import Settings
from app.models.hourly_signal import HourlySignal
from app.pipeline.ai_support_service import AISupportService


class FakeAIClient:
    """Deterministic fake AI client."""

    def __init__(self, *, is_configured: bool, payload: dict[str, object] | None = None) -> None:
        self.is_configured = is_configured
        self.payload = payload or {
            "support_score": 82.0,
            "narrative_strength": 75.0,
            "risk_label": "LOW",
            "summary": "Supportive signal context.",
            "warnings": [],
            "fallback_used": False,
            "raw_response_excerpt": "{\"ok\":true}",
        }

    def evaluate_context(self, *, context: dict[str, object]) -> dict[str, object]:
        return dict(self.payload)


def _hourly_signal(*, symbol: str, mean_signal: float) -> HourlySignal:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return HourlySignal(
        symbol=symbol,
        decision_horizon="1h",
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
        signal_stddev=0.06,
        bullish_ratio=0.75,
        last_3_slope=0.02,
        stability_score=0.86,
        aggregate_flags={"window_complete": True},
        feature_snapshot={"latest_breakout": True},
    )


def test_factory_selects_gemini_client() -> None:
    settings = Settings(_env_file=None, llm_provider="gemini")
    client = create_ai_support_client(settings=settings)
    assert isinstance(client, GeminiClient)


def test_ai_support_service_returns_empty_when_provider_disabled() -> None:
    settings = Settings(_env_file=None, llm_provider="disabled", deepseek_enabled=True)
    service = AISupportService(settings=settings)
    aggregates = [_hourly_signal(symbol="BTC/USDT", mean_signal=0.72)]

    results = service.evaluate_shortlist(aggregate_signals=aggregates)

    assert results == []


def test_ai_support_service_gemini_missing_key_returns_fallback() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        gemini_api_key="",
        deepseek_shortlist_limit=5,
        deepseek_min_aggregate_score=0.50,
    )
    service = AISupportService(settings=settings)
    aggregates = [_hourly_signal(symbol="BTC/USDT", mean_signal=0.72)]

    results = service.evaluate_shortlist(aggregate_signals=aggregates)

    assert len(results) == 1
    assert results[0].symbol == "BTC/USDT"
    assert results[0].fallback_used is True
    assert "gemini_missing_api_key" in results[0].warnings


def test_ai_support_service_applies_threshold_and_limit() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        gemini_api_key="test-key",
        deepseek_shortlist_limit=1,
        deepseek_min_aggregate_score=0.60,
    )
    fake_client = FakeAIClient(is_configured=True)
    service = AISupportService(settings=settings, client=fake_client)  # type: ignore[arg-type]
    aggregates = [
        _hourly_signal(symbol="BTC/USDT", mean_signal=0.77),
        _hourly_signal(symbol="ETH/USDT", mean_signal=0.62),
        _hourly_signal(symbol="BNB/USDT", mean_signal=0.45),
    ]

    results = service.evaluate_shortlist(aggregate_signals=aggregates)

    assert len(results) == 1
    assert results[0].symbol == "BTC/USDT"
    assert results[0].fallback_used is False
    assert results[0].risk_label == "LOW"
    assert results[0].support_score == 82.0


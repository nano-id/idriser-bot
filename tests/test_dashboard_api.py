"""Dashboard API tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.config.settings import Settings
from app.models.ai_signal import AISignal
from app.models.hourly_signal import HourlySignal
from app.pipeline.engine_runner import EngineRunnerStatus


def _build_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        deepseek_enabled=True,
        deepseek_api_key="test-secret-key",
        deepseek_model="deepseek-chat",
        gemini_api_key="gemini-secret-key",
        gemini_model="gemini-2.0-flash",
    )
    runtime_path = tmp_path / "runtime_config.json"
    app = create_app(settings=settings, runtime_config_path=runtime_path)
    return TestClient(app)


def _build_hourly_signal(symbol: str, mean_signal: float = 0.7) -> HourlySignal:
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
        signal_stddev=0.02,
        bullish_ratio=0.7,
        last_3_slope=0.01,
        stability_score=0.9,
        fallback_used=False,
        latest_breakout=True,
        aggregate_flags={"window_complete": True, "fallback_used": False},
        feature_snapshot={"latest_breakout": True},
    )


def _build_ai_signal(symbol: str) -> AISignal:
    return AISignal(
        symbol=symbol,
        decision_horizon="1h",
        provider="gemini",
        support_score=70.0,
        narrative_strength=65.0,
        risk_label="MEDIUM",
        summary="support",
        warnings=[],
        fallback_used=False,
        raw_response_excerpt="{}",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_health_endpoint_ok(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "dashboard-api"


def test_get_runtime_config_success(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        response = client.get("/runtime-config")
    assert response.status_code == 200
    payload = response.json()
    assert "runtime_config" in payload
    assert payload["runtime_config"]["decision_horizon"] == "1h"
    assert "deepseek_api_key" not in payload["runtime_config"]


def test_put_runtime_config_updates_values(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        update_response = client.put(
            "/runtime-config",
            json={
                "llm_provider": "gemini",
                "engine_enabled": True,
                "engine_universe_size": 25,
                "engine_refresh_seconds": 40,
                "engine_include_step2": True,
                "engine_include_step3": False,
                "engine_include_ai_support": True,
                "engine_max_signals": 10,
                "hourly_aggregation_window": 18,
                "hourly_min_snapshots": 12,
                "deepseek_enabled": False,
                "deepseek_shortlist_limit": 4,
                "deepseek_min_aggregate_score": 0.66,
                "deepseek_model": "deepseek-chat",
                "deepseek_timeout_seconds": 30,
                "gemini_model": "gemini-2.0-flash",
                "gemini_timeout_seconds": 35,
            },
        )
        assert update_response.status_code == 200
        payload = update_response.json()
        assert payload["runtime_config"]["engine_enabled"] is True
        assert payload["runtime_config"]["engine_universe_size"] == 25
        assert payload["runtime_config"]["engine_refresh_seconds"] == 40
        assert payload["runtime_config"]["engine_max_signals"] == 10
        assert payload["runtime_config"]["hourly_aggregation_window"] == 18
        assert payload["runtime_config"]["deepseek_shortlist_limit"] == 4
        assert payload["runtime_config"]["llm_provider"] == "gemini"
        assert payload["runtime_config"]["gemini_timeout_seconds"] == 35
        assert "deepseek_api_key" not in payload["runtime_config"]
        assert "gemini_api_key" not in payload["runtime_config"]

        verify_response = client.get("/runtime-config")
        assert verify_response.status_code == 200
        verify_payload = verify_response.json()
        assert verify_payload["runtime_config"]["engine_enabled"] is True
        assert verify_payload["runtime_config"]["hourly_aggregation_window"] == 18
        assert verify_payload["runtime_config"]["deepseek_enabled"] is False


def test_put_runtime_config_invalid_payload_returns_4xx(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        response = client.put(
            "/runtime-config",
            json={
                "hourly_aggregation_window": 5,
                "hourly_min_snapshots": 6,
                "aggregation_weight_trend": 0.8,
                "aggregation_weight_slope": 0.1,
                "aggregation_weight_rsi": 0.1,
                "aggregation_weight_macd": 0.1,
                "aggregation_weight_adx": 0.1,
                "aggregation_weight_volume": 0.1,
                "aggregation_weight_breakout": 0.1,
            },
        )
    assert response.status_code in {400, 422}


def test_runtime_config_reset_works(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        client.put(
            "/runtime-config",
            json={
                "engine_enabled": True,
                "engine_universe_size": 15,
                "hourly_aggregation_window": 18,
                "hourly_min_snapshots": 12,
                "deepseek_shortlist_limit": 2,
            },
        )
        response = client.post("/runtime-config/reset")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_config"]["engine_enabled"] is False
    assert payload["runtime_config"]["engine_universe_size"] == 30
    assert payload["runtime_config"]["hourly_aggregation_window"] == 12
    assert payload["runtime_config"]["deepseek_shortlist_limit"] == 10


def test_runtime_config_and_system_responses_hide_secret_fields(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        runtime_response = client.get("/runtime-config")
        system_response = client.get("/system/status")

    assert runtime_response.status_code == 200
    runtime_payload = runtime_response.json()
    assert "deepseek_api_key" not in runtime_payload["runtime_config"]
    assert "gemini_api_key" not in runtime_payload["runtime_config"]
    assert "DEEPSEEK_API_KEY" not in str(runtime_payload)
    assert "GEMINI_API_KEY" not in str(runtime_payload)

    assert system_response.status_code == 200
    system_payload = system_response.json()
    assert system_payload["llm_provider"] == "gemini"
    assert system_payload["llm_enabled"] is True
    assert system_payload["llm_configured"] is True
    assert "DEEPSEEK_API_KEY" not in str(system_payload)
    assert "GEMINI_API_KEY" not in str(system_payload)


def test_signals_latest_contract_returns_placeholder(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        response = client.get("/signals/latest")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "in_memory_signal_state"
    assert payload["placeholder"] is True
    assert payload["count"] == 0
    assert payload["signals"] == []


def test_ai_signals_latest_contract_returns_placeholder(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        response = client.get("/signals/ai-support/latest")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "in_memory_signal_state"
    assert payload["placeholder"] is True
    assert payload["count"] == 0
    assert payload["ai_signals"] == []


def test_system_status_reports_llm_not_configured_when_key_missing(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        gemini_api_key="",
    )
    app = create_app(settings=settings, runtime_config_path=tmp_path / "runtime_config.json")
    with TestClient(app) as client:
        response = client.get("/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["llm_provider"] == "gemini"
    assert payload["llm_enabled"] is True
    assert payload["llm_configured"] is False


def test_engine_endpoints_and_run_once_feed_signal_state(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        signal_store = client.app.state.services.signal_state_store

        class FakeRunner:
            def __init__(self) -> None:
                self._running = False
                self._last_run_at: datetime | None = None
                self._last_success_at: datetime | None = None
                self._last_error: str | None = None
                self._signal_count = 0
                self._ai_signal_count = 0

            def status(self) -> EngineRunnerStatus:
                return EngineRunnerStatus(
                    running=self._running,
                    last_run_at=self._last_run_at,
                    last_success_at=self._last_success_at,
                    last_error=self._last_error,
                    latest_signal_count=self._signal_count,
                    latest_ai_signal_count=self._ai_signal_count,
                )

            def run_once(self) -> EngineRunnerStatus:
                now = datetime(2026, 1, 2, tzinfo=UTC)
                signal_store.set_latest_signals([_build_hourly_signal("BTC/USDT", 0.82)])
                signal_store.set_latest_ai_signals([_build_ai_signal("BTC/USDT")])
                self._last_run_at = now
                self._last_success_at = now
                self._signal_count = 1
                self._ai_signal_count = 1
                self._last_error = None
                return self.status()

            def start(self) -> EngineRunnerStatus:
                self._running = True
                return self.status()

            def stop(self) -> EngineRunnerStatus:
                self._running = False
                return self.status()

        client.app.state.services.engine_runner = FakeRunner()

        status_before = client.get("/engine/status")
        assert status_before.status_code == 200
        assert status_before.json()["running"] is False

        run_once_response = client.post("/engine/run-once")
        assert run_once_response.status_code == 200
        run_payload = run_once_response.json()
        assert run_payload["action"] == "run_once"
        assert run_payload["status"]["latest_signal_count"] == 1
        assert run_payload["status"]["latest_ai_signal_count"] == 1

        latest_signals = client.get("/signals/latest")
        assert latest_signals.status_code == 200
        assert latest_signals.json()["placeholder"] is False
        assert latest_signals.json()["count"] == 1

        latest_ai = client.get("/signals/ai-support/latest")
        assert latest_ai.status_code == 200
        assert latest_ai.json()["placeholder"] is False
        assert latest_ai.json()["count"] == 1

        start_response = client.post("/engine/start")
        assert start_response.status_code == 200
        assert start_response.json()["status"]["running"] is True

        stop_response = client.post("/engine/stop")
        assert stop_response.status_code == 200
        assert stop_response.json()["status"]["running"] is False

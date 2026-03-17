"""Dashboard web page tests."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.config.settings import Settings


def _build_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        gemini_api_key="test-key",
        gemini_model="gemini-2.0-flash",
    )
    runtime_path = tmp_path / "runtime_config.json"
    return TestClient(create_app(settings=settings, runtime_config_path=runtime_path))


def test_dashboard_root_renders_sections(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "ID-Riser" in html
    assert "System Status" in html
    assert "Runtime Config" in html
    assert "Latest Aggregate Signals" in html
    assert "Latest AI Signals" in html
    assert "Paper Bot Status" in html
    assert "Paper Portfolio" in html
    assert "Paper Performance" in html
    assert "Historical Replay" in html
    assert "Historical Evaluations" in html
    assert "Simulation Journal" in html
    assert "Open Trades" in html
    assert "Closed Trades" in html
    assert "Controls" in html
    assert "Run Once" in html
    assert "Run Paper Cycle" in html
    assert "Run Historical Simulation" in html
    assert "Start Simulation" in html
    assert "Stop Simulation" in html
    assert "Step1" in html
    assert "Step2" in html
    assert "Step3" in html
    assert "How to use this page" in html
    assert "Data Flow" in html
    assert "Required Snapshots" in html
    assert "Weight Total" in html
    assert "Simulation Controls" not in html
    assert "Engine Controls" not in html
    assert "Engine Running" in html
    assert "language-selector" in html
    assert "Türkçe" in html
    assert "Search anything" not in html


def test_dashboard_static_assets_served(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        css_response = client.get("/static/css/dashboard.css")
        js_response = client.get("/static/js/dashboard.js")

    assert css_response.status_code == 200
    assert "layout-shell" in css_response.text
    assert js_response.status_code == 200
    assert "refreshAll" in js_response.text
    assert "onEngineRunOnce" in js_response.text
    assert "onPaperRunOnce" in js_response.text
    assert "onPaperStart" in js_response.text
    assert "onPaperStop" in js_response.text
    assert "onHistoricalRun" in js_response.text
    assert "LANGUAGE_STORAGE_KEY" in js_response.text
    assert "setLanguage" in js_response.text


def test_dashboard_stays_available_after_runtime_config_submit(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        put_response = client.put(
            "/runtime-config",
            json={
                "llm_provider": "gemini",
                "decision_horizon": "1h",
                "hourly_aggregation_window": 12,
                "hourly_min_snapshots": 12,
                "aggregation_bullish_threshold": 0.55,
                "deepseek_enabled": False,
                "deepseek_shortlist_limit": 6,
                "deepseek_min_aggregate_score": 0.60,
                "deepseek_model": "deepseek-chat",
                "deepseek_timeout_seconds": 20,
                "gemini_model": "gemini-2.0-flash",
                "gemini_timeout_seconds": 20,
            },
        )
        page_response = client.get("/")

    assert put_response.status_code == 200
    assert page_response.status_code == 200

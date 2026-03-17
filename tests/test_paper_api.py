"""Paper API endpoint tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.config.settings import Settings
from app.models.historical_simulation import HistoricalSimulationResult
from app.models.hourly_signal import HourlySignal
from app.models.paper_metrics import PaperMetrics


def _build_signal(*, mean_signal: float, latest_close: float) -> HourlySignal:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return HourlySignal(
        symbol="BTC/USDT",
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
        bullish_ratio=0.8,
        last_3_slope=0.01,
        stability_score=0.9,
        fallback_used=False,
        latest_breakout=True,
        step2_score=75.0,
        step2_pass=True,
        regime_status="BULLISH",
        step3_pass=True,
        regime_score=80.0,
        final_selected=True,
        aggregate_flags={"window_complete": True},
        feature_snapshot={"latest_close": latest_close, "latest_atr_pct": 0.02},
    )


def _build_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        _env_file=None,
        llm_provider="gemini",
        gemini_api_key="test-key",
        paper_bot_enabled=True,
        paper_initial_capital=10_000,
        paper_max_open_positions=3,
        paper_risk_per_trade_pct=0.01,
        paper_min_signal_score=0.6,
    )
    app = create_app(settings=settings, runtime_config_path=tmp_path / "runtime_config.json")
    return TestClient(app)


def test_paper_api_run_cycle_and_reset(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        signal_store = client.app.state.services.signal_state_store
        signal_store.set_latest_signals([_build_signal(mean_signal=0.82, latest_close=100.0)])

        status_response = client.get("/paper/status")
        assert status_response.status_code == 200
        assert "enabled" in status_response.json()

        run_once_response = client.post("/paper/run-once?sync_engine_before_run=false")
        assert run_once_response.status_code == 200
        run_payload = run_once_response.json()
        assert run_payload["opened_count"] == 1
        assert run_payload["status"]["open_trade_count"] >= 1

        portfolio_response = client.get("/paper/portfolio")
        assert portfolio_response.status_code == 200
        assert portfolio_response.json()["portfolio"]["open_positions"] >= 1

        open_trades_response = client.get("/paper/trades/open")
        assert open_trades_response.status_code == 200
        assert open_trades_response.json()["count"] >= 1

        events_after_open = client.get("/paper/events?limit=10")
        assert events_after_open.status_code == 200
        assert events_after_open.json()["count"] >= 2

        signal_store.set_latest_signals([_build_signal(mean_signal=0.2, latest_close=96.0)])
        close_response = client.post("/paper/run-once?sync_engine_before_run=false")
        assert close_response.status_code == 200

        closed_trades_response = client.get("/paper/trades/closed")
        assert closed_trades_response.status_code == 200
        assert closed_trades_response.json()["count"] >= 1

        metrics_response = client.get("/paper/metrics")
        assert metrics_response.status_code == 200
        metrics_payload = metrics_response.json()["metrics"]
        assert metrics_payload["total_closed_trades"] >= 1
        assert "max_drawdown_pct" in metrics_payload
        assert "total_fees_paid" in metrics_payload

        snapshots_response = client.get("/paper/snapshots?limit=20")
        assert snapshots_response.status_code == 200
        assert snapshots_response.json()["count"] >= 1

        export_response = client.get("/paper/export")
        assert export_response.status_code == 200
        export_payload = export_response.json()
        assert "portfolio" in export_payload
        assert "metrics" in export_payload
        assert "closed_trades" in export_payload
        assert "events" in export_payload
        assert "snapshots" in export_payload

        runtime_response = client.put(
            "/runtime-config",
            json={
                "paper_sync_engine_before_run": False,
                "paper_refresh_seconds": 5,
                "paper_fee_bps": 12,
                "paper_slippage_bps": 6,
            },
        )
        assert runtime_response.status_code == 200

        start_response = client.post("/paper/start")
        assert start_response.status_code == 200
        assert start_response.json()["status"]["running"] is True
        assert start_response.json()["status"]["last_success_at"] is not None

        stop_response = client.post("/paper/stop")
        assert stop_response.status_code == 200
        assert stop_response.json()["status"]["running"] is False

        reset_response = client.post("/paper/reset")
        assert reset_response.status_code == 200
        reset_payload = reset_response.json()
        assert reset_payload["open_trade_count"] == 0
        assert reset_payload["closed_trade_count"] == 0

        portfolio_after_reset = client.get("/paper/portfolio")
        assert portfolio_after_reset.status_code == 200
        portfolio_payload = portfolio_after_reset.json()["portfolio"]
        assert portfolio_payload["open_positions"] == 0
        assert portfolio_payload["closed_positions"] == 0

        events_after_reset = client.get("/paper/events?limit=10")
        assert events_after_reset.status_code == 200
        assert any(event["event_type"] == "RESET" for event in events_after_reset.json()["events"])


def test_historical_simulation_api_returns_latest_result(tmp_path: Path) -> None:
    with _build_client(tmp_path) as client:
        services = client.app.state.services

        class FakeHistoricalSimulationEngine:
            def run(self, *, symbol: str, start_at: datetime, end_at: datetime, close_open_positions_at_end: bool = True) -> HistoricalSimulationResult:
                return HistoricalSimulationResult(
                    symbol=symbol,
                    start_at=start_at,
                    end_at=end_at,
                    decision_horizon="15m",
                    snapshot_timeframe="1m",
                    initial_capital=10_000,
                    final_equity=11_250,
                    final_cash_balance=11_250,
                    total_return_pct=12.5,
                    candles_processed=120,
                    evaluation_count=24,
                    selected_signal_count=8,
                    opened_trade_count=5,
                    closed_trade_count=5,
                    force_closed_at_end=True,
                    runtime_summary={"decision_horizon": "15m"},
                    metrics=PaperMetrics(
                        total_closed_trades=5,
                        win_count=4,
                        loss_count=1,
                        win_rate_pct=80.0,
                        avg_win_value=120.0,
                        avg_loss_value=-40.0,
                        expectancy_value=88.0,
                        profit_factor=3.0,
                        best_trade_pct=5.5,
                        worst_trade_pct=-1.2,
                        max_drawdown_pct=2.0,
                        total_fees_paid=15.0,
                        net_profit_value=1250.0,
                        total_return_pct=12.5,
                        avg_hold_minutes=55.0,
                        current_equity=11_250,
                        current_cash_balance=11_250,
                        open_positions=0,
                    ),
                )

        services.historical_simulation_engine = FakeHistoricalSimulationEngine()

        run_response = client.post(
            "/paper/historical/run",
            json={
                "symbol": "ETH/USDT",
                "start_at": "2026-01-01T00:00:00Z",
                "end_at": "2026-01-05T00:00:00Z",
                "close_open_positions_at_end": True,
            },
        )
        assert run_response.status_code == 200
        run_payload = run_response.json()["result"]
        assert run_payload["symbol"] == "ETH/USDT"
        assert run_payload["final_equity"] == 11250
        assert run_payload["metrics"]["win_rate_pct"] == 80.0

        latest_response = client.get("/paper/historical/latest")
        assert latest_response.status_code == 200
        latest_payload = latest_response.json()["result"]
        assert latest_payload["symbol"] == "ETH/USDT"
        assert latest_payload["selected_signal_count"] == 8

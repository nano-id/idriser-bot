"""Paper runner tests."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path

from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.models.hourly_signal import HourlySignal
from app.pipeline.engine_runner import EngineRunnerStatus
from app.pipeline.paper_journal_store import PaperJournalStore
from app.pipeline.paper_portfolio_store import PaperPortfolioStore
from app.pipeline.paper_runner import PaperRunner
from app.pipeline.paper_trade_engine import PaperTradeEngine
from app.pipeline.signal_state_store import SignalStateStore


def _build_signal(*, mean_signal: float = 0.82, latest_close: float = 100.0) -> HourlySignal:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return HourlySignal(
        symbol="BTC/USDT",
        decision_horizon="1h",
        base_snapshot_timeframe="1m",
        required_snapshots=60,
        window_size=60,
        snapshot_count=60,
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
        step2_score=74.0,
        step2_pass=True,
        regime_status="BULLISH",
        step3_pass=True,
        regime_score=78.0,
        final_selected=True,
        aggregate_flags={"window_complete": True},
        feature_snapshot={"latest_close": latest_close, "latest_atr_pct": 0.02},
    )


class FakeEngineRunner:
    def __init__(self, *, signal_store: SignalStateStore, running: bool = False) -> None:
        self.signal_store = signal_store
        self._running = running
        self.run_calls = 0

    def status(self) -> EngineRunnerStatus:
        return EngineRunnerStatus(
            running=self._running,
            last_run_at=None,
            last_success_at=None,
            last_error=None,
            latest_signal_count=0,
            latest_ai_signal_count=0,
        )

    def run_once(self) -> EngineRunnerStatus:
        self.run_calls += 1
        self.signal_store.set_latest_signals([_build_signal()])
        return self.status()


def _build_runner(tmp_path: Path) -> tuple[PaperRunner, SignalStateStore, FakeEngineRunner]:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_initial_capital=10_000,
        paper_max_open_positions=3,
        paper_risk_per_trade_pct=0.01,
        paper_min_signal_score=0.6,
        paper_refresh_seconds=5,
        paper_sync_engine_before_run=True,
    )
    signal_store = SignalStateStore()
    runtime_store = RuntimeConfigStore(path=tmp_path / "runtime_config.json", settings=settings)
    portfolio_store = PaperPortfolioStore(initial_capital=settings.paper_initial_capital)
    journal_store = PaperJournalStore()
    paper_engine = PaperTradeEngine(
        settings=settings,
        runtime_config_store=runtime_store,
        signal_state_store=signal_store,
        portfolio_store=portfolio_store,
        journal_store=journal_store,
    )
    fake_engine_runner = FakeEngineRunner(signal_store=signal_store)
    runner = PaperRunner(
        settings=settings,
        runtime_config_store=runtime_store,
        paper_engine=paper_engine,
        engine_runner=fake_engine_runner,  # type: ignore[arg-type]
    )
    return runner, signal_store, fake_engine_runner


def test_paper_runner_run_once_can_skip_engine_sync(tmp_path: Path) -> None:
    runner, signal_store, fake_engine_runner = _build_runner(tmp_path)
    signal_store.set_latest_signals([_build_signal()])

    status = runner.run_once(sync_engine_before_run=False)

    assert fake_engine_runner.run_calls == 0
    assert status.last_opened_count == 1
    assert status.open_trade_count == 1


def test_paper_runner_background_start_and_stop(tmp_path: Path) -> None:
    runner, _, fake_engine_runner = _build_runner(tmp_path)

    started = runner.start()
    assert started.running is True
    assert started.last_success_at is not None
    assert started.last_opened_count >= 1

    deadline = time.time() + 2.5
    while time.time() < deadline:
        status = runner.status()
        if status.last_success_at is not None:
            break
        time.sleep(0.05)

    stopped = runner.stop()

    assert fake_engine_runner.run_calls >= 1
    assert stopped.running is False
    assert stopped.last_success_at is not None

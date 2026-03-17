"""Engine runner lifecycle and status tests."""

from __future__ import annotations

import time
from datetime import UTC, datetime

import pytest

from app.pipeline.dashboard_signal_engine import EngineRunResult
from app.pipeline.engine_runner import EngineRunner


class FakeEngine:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.calls = 0

    def run_once(self) -> EngineRunResult:
        self.calls += 1
        if self.should_fail:
            msg = "forced_engine_failure"
            raise RuntimeError(msg)
        now = datetime(2026, 1, 1, tzinfo=UTC)
        return EngineRunResult(
            run_at=now,
            signal_count=3,
            ai_signal_count=1,
            processed_symbols=5,
            refresh_seconds=1,
            errors=[],
        )


def test_engine_runner_run_once_updates_status() -> None:
    runner = EngineRunner(engine=FakeEngine(), refresh_seconds=5)

    status = runner.run_once()

    assert status.running is False
    assert status.last_run_at is not None
    assert status.last_success_at is not None
    assert status.last_error is None
    assert status.latest_signal_count == 3
    assert status.latest_ai_signal_count == 1


def test_engine_runner_start_and_stop() -> None:
    engine = FakeEngine()
    runner = EngineRunner(engine=engine, refresh_seconds=1)

    start_status = runner.start()
    assert start_status.running is True
    assert start_status.last_run_at is not None
    assert start_status.last_success_at is not None
    assert start_status.latest_signal_count == 3
    assert start_status.latest_ai_signal_count == 1
    assert engine.calls >= 1

    time.sleep(0.15)
    mid_status = runner.status()
    assert mid_status.running is True

    stop_status = runner.stop()
    assert stop_status.running is False
    assert engine.calls >= 1


def test_engine_runner_start_failure_rolls_back_running_state() -> None:
    runner = EngineRunner(engine=FakeEngine(should_fail=True), refresh_seconds=1)

    with pytest.raises(RuntimeError, match="forced_engine_failure"):
        runner.start()

    status = runner.status()
    assert status.running is False
    assert status.last_run_at is not None
    assert status.last_error is not None


def test_engine_runner_failure_sets_last_error() -> None:
    runner = EngineRunner(engine=FakeEngine(should_fail=True), refresh_seconds=5)

    with pytest.raises(RuntimeError, match="forced_engine_failure"):
        runner.run_once()

    status = runner.status()
    assert status.last_run_at is not None
    assert status.last_error is not None
    assert "forced_engine_failure" in status.last_error

"""Background runner for periodic paper simulation cycles."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from threading import Event, RLock, Thread

from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.models.runtime_config import RuntimeConfig
from app.pipeline.engine_runner import EngineRunner
from app.pipeline.paper_trade_engine import PaperTradeEngine
from app.utils.runtime import utc_now


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PaperRunnerStatus:
    """Serializable status snapshot for paper simulation controls."""

    running: bool
    enabled: bool
    refresh_seconds: int
    sync_engine_before_run: bool
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    last_opened_count: int
    last_closed_count: int
    open_trade_count: int
    closed_trade_count: int
    cash_balance: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float


class PaperRunner:
    """Start/stop/run-once wrapper around PaperTradeEngine."""

    def __init__(
        self,
        *,
        settings: Settings,
        runtime_config_store: RuntimeConfigStore,
        paper_engine: PaperTradeEngine,
        engine_runner: EngineRunner,
    ) -> None:
        self.settings = settings
        self.runtime_config_store = runtime_config_store
        self.paper_engine = paper_engine
        self.engine_runner = engine_runner

        self._lock = RLock()
        self._stop_event = Event()
        self._thread: Thread | None = None

        self._running = False
        self._refresh_seconds = settings.paper_refresh_seconds
        self._sync_engine_before_run = settings.paper_sync_engine_before_run
        self._last_run_at: datetime | None = None
        self._last_success_at: datetime | None = None
        self._last_error: str | None = None
        self._last_opened_count = 0
        self._last_closed_count = 0

    def start(self) -> PaperRunnerStatus:
        with self._lock:
            if self._running:
                return self.status()
            self._running = True
            self._stop_event.clear()

        try:
            self._execute_once()
        except Exception:
            with self._lock:
                self._running = False
                self._thread = None
            raise

        with self._lock:
            self._thread = Thread(target=self._run_loop, name="paper-runner", daemon=True)
            self._thread.start()
            LOGGER.info("Paper runner started")
            return self._status_unlocked()

    def stop(self) -> PaperRunnerStatus:
        thread: Thread | None = None
        with self._lock:
            self._stop_event.set()
            thread = self._thread

        if thread is not None:
            thread.join(timeout=max(2.0, float(self._refresh_seconds) + 1.0))

        with self._lock:
            self._running = False
            self._thread = None
            LOGGER.info("Paper runner stopped")
            return self._status_unlocked()

    def run_once(self, *, sync_engine_before_run: bool | None = None) -> PaperRunnerStatus:
        self._execute_once(sync_override=sync_engine_before_run)
        return self.status()

    def status(self) -> PaperRunnerStatus:
        with self._lock:
            return self._status_unlocked()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            wait_seconds = self._refresh_seconds
            if self._stop_event.wait(timeout=wait_seconds):
                break

            try:
                self._execute_once()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Paper loop run failed: %s", exc)

        with self._lock:
            self._running = False

    def _execute_once(self, *, sync_override: bool | None = None) -> None:
        self._refresh_seconds, self._sync_engine_before_run = self._load_runner_config()
        effective_sync = self._sync_engine_before_run if sync_override is None else sync_override
        if effective_sync and not self.engine_runner.status().running:
            self.engine_runner.run_once()

        try:
            result = self.paper_engine.run_once()
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                self._last_run_at = utc_now()
                self._last_error = str(exc)
            raise

        with self._lock:
            self._last_run_at = result.run_at
            self._last_success_at = result.run_at
            self._last_error = result.status.last_error
            self._last_opened_count = result.opened_count
            self._last_closed_count = result.closed_count

    def _load_runner_config(self) -> tuple[int, bool]:
        try:
            runtime = self.runtime_config_store.load()
        except Exception:  # noqa: BLE001
            runtime = RuntimeConfig.from_settings(self.settings)
        return runtime.paper_refresh_seconds, runtime.paper_sync_engine_before_run

    def _status_unlocked(self) -> PaperRunnerStatus:
        base_status = self.paper_engine.status()
        return PaperRunnerStatus(
            running=self._running,
            enabled=base_status.enabled,
            refresh_seconds=self._refresh_seconds,
            sync_engine_before_run=self._sync_engine_before_run,
            last_run_at=self._last_run_at,
            last_success_at=self._last_success_at,
            last_error=self._last_error or base_status.last_error,
            last_opened_count=self._last_opened_count,
            last_closed_count=self._last_closed_count,
            open_trade_count=base_status.open_trade_count,
            closed_trade_count=base_status.closed_trade_count,
            cash_balance=base_status.cash_balance,
            equity=base_status.equity,
            realized_pnl=base_status.realized_pnl,
            unrealized_pnl=base_status.unrealized_pnl,
        )

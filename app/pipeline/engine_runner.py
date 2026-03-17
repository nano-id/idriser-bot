"""Background runner for periodic dashboard signal engine scans."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from threading import Event, RLock, Thread

from app.pipeline.dashboard_signal_engine import DashboardSignalEngine
from app.utils.runtime import utc_now


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class EngineRunnerStatus:
    """Serializable status snapshot for engine controls."""

    running: bool
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    latest_signal_count: int
    latest_ai_signal_count: int


class EngineRunner:
    """Start/stop/run-once wrapper around DashboardSignalEngine."""

    def __init__(
        self,
        *,
        engine: DashboardSignalEngine,
        refresh_seconds: int,
    ) -> None:
        self.engine = engine
        self._refresh_seconds = max(1, int(refresh_seconds))

        self._lock = RLock()
        self._stop_event = Event()
        self._thread: Thread | None = None

        self._running = False
        self._last_run_at: datetime | None = None
        self._last_success_at: datetime | None = None
        self._last_error: str | None = None
        self._latest_signal_count = 0
        self._latest_ai_signal_count = 0

    def start(self) -> EngineRunnerStatus:
        """Start background loop and perform one immediate scan."""
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
            self._thread = Thread(target=self._run_loop, name="dashboard-engine-runner", daemon=True)
            self._thread.start()
            LOGGER.info("Engine runner started")
            return self._status_unlocked()

    def stop(self) -> EngineRunnerStatus:
        """Stop background loop if active."""
        thread: Thread | None = None
        with self._lock:
            self._stop_event.set()
            thread = self._thread

        if thread is not None:
            thread.join(timeout=max(2.0, float(self._refresh_seconds) + 1.0))

        with self._lock:
            self._running = False
            self._thread = None
            LOGGER.info("Engine runner stopped")
            return self._status_unlocked()

    def run_once(self) -> EngineRunnerStatus:
        """Run engine once synchronously and update status fields."""
        self._execute_once()
        return self.status()

    def status(self) -> EngineRunnerStatus:
        """Return current runner status."""
        with self._lock:
            return self._status_unlocked()

    def _status_unlocked(self) -> EngineRunnerStatus:
        return EngineRunnerStatus(
            running=self._running,
            last_run_at=self._last_run_at,
            last_success_at=self._last_success_at,
            last_error=self._last_error,
            latest_signal_count=self._latest_signal_count,
            latest_ai_signal_count=self._latest_ai_signal_count,
        )

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            wait_seconds = self._refresh_seconds
            if self._stop_event.wait(timeout=wait_seconds):
                break

            try:
                self._execute_once()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Engine loop run failed: %s", exc)

        with self._lock:
            self._running = False

    def _execute_once(self) -> None:
        try:
            result = self.engine.run_once()
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                self._last_run_at = utc_now()
                self._last_error = str(exc)
            raise

        with self._lock:
            self._last_run_at = result.run_at
            self._last_success_at = result.run_at
            self._last_error = result.errors[-1] if result.errors else None
            self._latest_signal_count = result.signal_count
            self._latest_ai_signal_count = result.ai_signal_count
            self._refresh_seconds = max(1, int(result.refresh_seconds))

        if result.errors:
            LOGGER.warning("Engine run completed with %s warning(s)", len(result.errors))

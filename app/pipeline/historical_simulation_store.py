"""In-memory store for the latest historical simulation result."""

from __future__ import annotations

from threading import RLock

from app.models.historical_simulation import HistoricalSimulationResult


class HistoricalSimulationStore:
    """Thread-safe holder for the most recent historical replay result."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._latest_result: HistoricalSimulationResult | None = None

    def get_latest(self) -> HistoricalSimulationResult | None:
        with self._lock:
            if self._latest_result is None:
                return None
            return HistoricalSimulationResult.model_validate(self._latest_result.model_dump())

    def set_latest(self, result: HistoricalSimulationResult) -> None:
        with self._lock:
            self._latest_result = HistoricalSimulationResult.model_validate(result.model_dump())

    def reset(self) -> None:
        with self._lock:
            self._latest_result = None


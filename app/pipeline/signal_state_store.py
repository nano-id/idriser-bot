"""In-memory signal state for dashboard API reads."""

from __future__ import annotations

from threading import RLock
from typing import Sequence

from app.models.ai_signal import AISignal
from app.models.hourly_signal import HourlySignal


class SignalStateStore:
    """Thread-safe in-memory holder for latest aggregate and AI signals."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._latest_signals: list[HourlySignal] = []
        self._latest_ai_signals: list[AISignal] = []

    def get_latest_signals(self) -> list[HourlySignal]:
        """Return latest aggregate signals."""
        with self._lock:
            return [HourlySignal.model_validate(item.model_dump()) for item in self._latest_signals]

    def set_latest_signals(self, signals: Sequence[HourlySignal]) -> None:
        """Replace latest aggregate signal set."""
        with self._lock:
            self._latest_signals = [HourlySignal.model_validate(item.model_dump()) for item in signals]

    def get_latest_ai_signals(self) -> list[AISignal]:
        """Return latest AI support signals."""
        with self._lock:
            return [AISignal.model_validate(item.model_dump()) for item in self._latest_ai_signals]

    def set_latest_ai_signals(self, signals: Sequence[AISignal]) -> None:
        """Replace latest AI support signal set."""
        with self._lock:
            self._latest_ai_signals = [AISignal.model_validate(item.model_dump()) for item in signals]

    def clear(self) -> None:
        """Clear all stored signal state."""
        with self._lock:
            self._latest_signals.clear()
            self._latest_ai_signals.clear()


"""Helpers for timeframe and horizon normalization."""

from __future__ import annotations

import re
from math import ceil


_TIMEFRAME_RE = re.compile(r"^\s*(\d+)\s*([mhdMHD])\s*$")


def timeframe_to_minutes(value: str) -> int:
    """Convert timeframe like `5m`, `1h`, `1d` to minutes."""
    match = _TIMEFRAME_RE.match(value or "")
    if match is None:
        msg = f"Unsupported timeframe format: {value}"
        raise ValueError(msg)

    amount = int(match.group(1))
    unit = match.group(2).lower()
    multiplier = {"m": 1, "h": 60, "d": 1440}[unit]
    return amount * multiplier


def normalize_timeframe(value: str) -> str:
    """Normalize timeframe into compact lowercase form."""
    minutes = timeframe_to_minutes(value)
    if minutes % 1440 == 0:
        return f"{minutes // 1440}d"
    if minutes % 60 == 0:
        return f"{minutes // 60}h"
    return f"{minutes}m"


def required_snapshots_for_horizon(*, decision_horizon: str, snapshot_interval_minutes: int) -> int:
    """Return required snapshot count to cover decision horizon."""
    if snapshot_interval_minutes <= 0:
        msg = "snapshot_interval_minutes must be positive"
        raise ValueError(msg)

    horizon_minutes = timeframe_to_minutes(decision_horizon)
    return max(1, ceil(horizon_minutes / snapshot_interval_minutes))

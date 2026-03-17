"""Runtime helper utilities."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


def build_run_id() -> str:
    """Create deterministic run-id string for file naming."""
    return utc_now().strftime("%Y%m%d_%H%M%S")

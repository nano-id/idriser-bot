"""Shared models for future Step 2 / Step 3 filters."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FilterDecision(BaseModel):
    """Generic filter decision payload."""

    status: Literal["pass", "fail", "unknown"] = "unknown"
    score: float | None = Field(default=None, ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)

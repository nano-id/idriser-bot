"""Models for optional AI support scoring outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RiskLabel = Literal["LOW", "MEDIUM", "HIGH"]


class AISignal(BaseModel):
    """Supportive AI output for shortlist symbols."""

    symbol: str
    decision_horizon: str
    provider: str | None = None
    support_score: float = Field(ge=0, le=100)
    narrative_strength: float = Field(ge=0, le=100)
    risk_label: RiskLabel
    summary: str
    warnings: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    raw_response_excerpt: str | None = None
    timestamp: datetime

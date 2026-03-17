"""Models for Step 3 market regime filter."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RegimeStatus = Literal["BULLISH", "NEUTRAL", "BEARISH", "DANGER"]


class Step3Result(BaseModel):
    """Step 3 regime/risk result for one asset."""

    symbol: str
    base_asset: str
    step3_pass: bool
    regime_status: RegimeStatus
    regime_score: float = Field(ge=0, le=100)
    regime_reasoning: list[str] = Field(default_factory=list)
    regime_snapshot: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    fallback_used: bool = False
    unavailable_risk_metrics: list[str] = Field(default_factory=list)
    generated_at: datetime

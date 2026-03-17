"""Models for Step 2 technical filter."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Step2Result(BaseModel):
    """Technical filter output for one asset."""

    symbol: str
    base_asset: str
    timeframe: str
    confirmation_timeframe: str | None = None
    step2_score: float = Field(ge=0, le=100)
    step2_pass: bool
    technical_reasoning: list[str] = Field(default_factory=list)
    technical_snapshot: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    technical_flags: dict[str, bool] = Field(default_factory=dict)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    missing_technical_data: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    generated_at: datetime

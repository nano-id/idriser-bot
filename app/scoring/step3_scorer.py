"""Step 3 regime scoring engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.config.settings import Settings
from app.utils.indicators import clamp


RegimeStatus = Literal["BULLISH", "NEUTRAL", "BEARISH", "DANGER"]


@dataclass(slots=True)
class Step3ScoreOutcome:
    """Score output for Step 3."""

    regime_score: float
    regime_status: RegimeStatus
    step3_pass: bool
    score_breakdown: dict[str, float]
    score_reasoning: list[str]


class Step3Scorer:
    """Compute regime score/status from trend, volatility, breadth and derivatives signals."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def calculate(
        self,
        *,
        sub_scores: dict[str, float],
        danger_flag: bool,
        fallback_used: bool,
    ) -> Step3ScoreOutcome:
        score_breakdown: dict[str, float] = {}
        score_reasoning: list[str] = []
        regime_score = 0.0

        for category, weight in self.settings.regime_weights.items():
            cat_score = clamp(sub_scores.get(category, 0.0), 0.0, 1.0)
            points = cat_score * weight * 100
            score_breakdown[category] = round(points, 2)
            regime_score += points
            score_reasoning.append(
                f"{category} katkisi: {points:.2f} puan (kategori skor {cat_score:.2f})"
            )

        if fallback_used:
            regime_score -= self.settings.regime_fallback_penalty_points
            score_reasoning.append(
                f"fallback cezasi: -{self.settings.regime_fallback_penalty_points:.2f}"
            )

        regime_score = round(clamp(regime_score, 0.0, 100.0), 2)

        if danger_flag:
            regime_status: RegimeStatus = "DANGER"
        elif regime_score >= self.settings.regime_score_bullish_threshold:
            regime_status = "BULLISH"
        elif regime_score >= self.settings.regime_score_neutral_threshold:
            regime_status = "NEUTRAL"
        else:
            regime_status = "BEARISH"

        step3_pass = self._pass_decision(regime_status)
        score_reasoning.append(f"rejim durumu: {regime_status}")
        if not step3_pass:
            score_reasoning.append("rejim veto kosulu nedeniyle NO_TRADE")

        return Step3ScoreOutcome(
            regime_score=regime_score,
            regime_status=regime_status,
            step3_pass=step3_pass,
            score_breakdown=score_breakdown,
            score_reasoning=score_reasoning,
        )

    def _pass_decision(self, regime_status: RegimeStatus) -> bool:
        if regime_status == "DANGER":
            return not self.settings.regime_veto_if_danger
        if regime_status == "BEARISH":
            return not self.settings.regime_veto_if_bearish
        if regime_status == "NEUTRAL":
            return self.settings.regime_allow_neutral
        return True

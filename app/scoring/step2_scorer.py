"""Step 2 technical scoring engine."""

from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import Settings
from app.utils.indicators import clamp


@dataclass(slots=True)
class Step2ScoreOutcome:
    """Score output for Step 2."""

    step2_score: float
    step2_pass: bool
    score_breakdown: dict[str, float]
    score_reasoning: list[str]


class Step2Scorer:
    """Score technical quality using weighted category outputs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def calculate(
        self,
        *,
        sub_scores: dict[str, float],
        technical_flags: dict[str, bool],
        missing_technical_data: list[str],
    ) -> Step2ScoreOutcome:
        score_breakdown: dict[str, float] = {}
        score_reasoning: list[str] = []
        total_score = 0.0

        for category, weight in self.settings.technical_weights.items():
            normalized_score = clamp(sub_scores.get(category, 0.0), 0.0, 1.0)
            points = normalized_score * weight * 100
            score_breakdown[category] = round(points, 2)
            total_score += points
            score_reasoning.append(
                f"{category} katkisi: {points:.2f} puan (kategori skor {normalized_score:.2f})"
            )

        penalty = 0.0
        if technical_flags.get("overextended", False):
            penalty += self.settings.technical_overextended_penalty
            score_reasoning.append(
                f"overextended cezasi: -{self.settings.technical_overextended_penalty:.2f}"
            )

        if technical_flags.get("noisy_structure", False):
            penalty += self.settings.technical_noisy_penalty
            score_reasoning.append(f"noisy_structure cezasi: -{self.settings.technical_noisy_penalty:.2f}")

        critical_missing = [
            item
            for item in missing_technical_data
            if item in set(self.settings.technical_critical_indicators)
        ]
        if critical_missing:
            critical_penalty = len(critical_missing) * self.settings.technical_missing_critical_penalty
            penalty += critical_penalty
            score_reasoning.append(
                f"kritik eksik veri cezasi: -{critical_penalty:.2f} ({len(critical_missing)} indikator)"
            )

        if self.settings.technical_use_secondary_confirmation:
            secondary_confirm = technical_flags.get("secondary_confirm")
            if secondary_confirm is False:
                penalty += self.settings.technical_secondary_confirmation_penalty
                score_reasoning.append(
                    "ikincil timeframe onayi yok: "
                    f"-{self.settings.technical_secondary_confirmation_penalty:.2f}"
                )

        total_score = clamp(total_score - penalty, 0.0, 100.0)

        hard_fail = technical_flags.get("hard_fail", False)
        entry_signal = technical_flags.get("entry_signal", False)
        step2_pass = (
            total_score >= self.settings.technical_pass_threshold
            and entry_signal
            and not hard_fail
        )

        if not entry_signal:
            score_reasoning.append("entry sinyali olusmadi")
        if hard_fail:
            score_reasoning.append("teknik risk veto kosulu tetiklendi")
        if total_score < self.settings.technical_pass_threshold:
            score_reasoning.append(
                f"step2 score esigin altinda ({total_score:.2f} < {self.settings.technical_pass_threshold:.2f})"
            )

        return Step2ScoreOutcome(
            step2_score=round(total_score, 2),
            step2_pass=step2_pass,
            score_breakdown=score_breakdown,
            score_reasoning=score_reasoning,
        )

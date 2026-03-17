"""Provider-agnostic optional AI support service for shortlist symbols."""

from __future__ import annotations

import logging
from typing import Mapping, Sequence

from app.clients.ai_client_factory import create_ai_support_client
from app.clients.ai_support_protocol import AISupportClientProtocol
from app.config.settings import Settings
from app.models.ai_signal import AISignal
from app.models.hourly_signal import HourlySignal
from app.models.step2 import Step2Result
from app.models.step3 import Step3Result
from app.utils.runtime import utc_now


LOGGER = logging.getLogger(__name__)


class AISupportService:
    """Generate optional AI support signals without replacing core decisions."""

    def __init__(
        self,
        *,
        settings: Settings,
        client: AISupportClientProtocol | None = None,
    ) -> None:
        self.settings = settings
        self.client = client or create_ai_support_client(settings=settings)

    def evaluate_shortlist(
        self,
        *,
        aggregate_signals: Sequence[HourlySignal],
        step2_results_by_symbol: Mapping[str, Step2Result] | None = None,
        step3_results_by_symbol: Mapping[str, Step3Result] | None = None,
        shortlist_symbols: Sequence[str] | None = None,
    ) -> list[AISignal]:
        """Return AI support outputs for shortlisted symbols."""
        selected = self._select_candidates(
            aggregate_signals=aggregate_signals,
            shortlist_symbols=shortlist_symbols,
        )
        if not selected:
            return []

        if not self._is_llm_enabled():
            LOGGER.info("AI support disabled; skipping %s symbols", len(selected))
            return []

        step2_results = step2_results_by_symbol or {}
        step3_results = step3_results_by_symbol or {}

        if not self.client.is_configured:
            return [
                self._fallback_signal(
                    signal=signal,
                    summary=f"{self.settings.llm_provider.title()} skipped: missing API key",
                    warning=f"{self.settings.llm_provider}_missing_api_key",
                    raw_excerpt=None,
                )
                for signal in selected
            ]

        outputs: list[AISignal] = []
        for signal in selected:
            context = self._build_context(
                signal=signal,
                step2_result=step2_results.get(signal.symbol),
                step3_result=step3_results.get(signal.symbol),
            )
            try:
                response = self.client.evaluate_context(context=context)
                outputs.append(
                    AISignal(
                        symbol=signal.symbol,
                        decision_horizon=signal.decision_horizon,
                        provider=self.settings.llm_provider,
                        support_score=float(response.get("support_score", 50.0)),
                        narrative_strength=float(response.get("narrative_strength", 50.0)),
                        risk_label=str(response.get("risk_label", "MEDIUM")),
                        summary=str(response.get("summary", "AI fallback")),
                        warnings=self._warnings_list(response.get("warnings")),
                        fallback_used=bool(response.get("fallback_used", False)),
                        raw_response_excerpt=self._raw_excerpt(response.get("raw_response_excerpt")),
                        timestamp=utc_now(),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("AI support signal fallback for %s: %s", signal.symbol, exc)
                outputs.append(
                    self._fallback_signal(
                        signal=signal,
                        summary="AI fallback: signal build failed",
                        warning="ai_signal_build_failed",
                        raw_excerpt=str(exc),
                    )
                )
        return outputs

    def _is_llm_enabled(self) -> bool:
        if self.settings.llm_provider == "disabled":
            return False
        if self.settings.llm_provider == "deepseek":
            return self.settings.deepseek_enabled
        return True

    def _select_candidates(
        self,
        *,
        aggregate_signals: Sequence[HourlySignal],
        shortlist_symbols: Sequence[str] | None,
    ) -> list[HourlySignal]:
        shortlist_set = {item.upper().strip() for item in shortlist_symbols or [] if item.strip()}
        candidates = []
        for signal in aggregate_signals:
            symbol = signal.symbol.upper().strip()
            if shortlist_set and symbol not in shortlist_set:
                continue
            if signal.mean_signal < self.settings.ai_min_aggregate_score:
                continue
            candidates.append(signal)

        candidates.sort(key=lambda item: item.mean_signal, reverse=True)
        return candidates[: self.settings.ai_shortlist_limit]

    @staticmethod
    def _build_context(
        *,
        signal: HourlySignal,
        step2_result: Step2Result | None,
        step3_result: Step3Result | None,
    ) -> dict[str, object]:
        breakout = bool(signal.feature_snapshot.get("latest_breakout", False))
        step2_summary = "not_available"
        if step2_result is not None:
            hard_fail = step2_result.technical_flags.get("hard_fail", False)
            step2_summary = (
                f"pass={step2_result.step2_pass};"
                f"score={step2_result.step2_score:.2f};"
                f"hard_fail={hard_fail};"
                f"fallback={step2_result.fallback_used}"
            )

        step3_summary = "not_available"
        if step3_result is not None:
            step3_summary = (
                f"pass={step3_result.step3_pass};"
                f"status={step3_result.regime_status};"
                f"score={step3_result.regime_score:.2f};"
                f"fallback={step3_result.fallback_used}"
            )

        return {
            "symbol": signal.symbol,
            "decision_horizon": signal.decision_horizon,
            "mean_signal": round(signal.mean_signal, 6),
            "bullish_ratio": round(signal.bullish_ratio, 6),
            "stability_score": round(signal.stability_score, 6),
            "breakout": breakout,
            "step2_summary": step2_summary,
            "step3_summary": step3_summary,
        }

    def _fallback_signal(
        self,
        *,
        signal: HourlySignal,
        summary: str,
        warning: str,
        raw_excerpt: str | None,
    ) -> AISignal:
        return AISignal(
            symbol=signal.symbol,
            decision_horizon=signal.decision_horizon,
            provider=self.settings.llm_provider,
            support_score=50.0,
            narrative_strength=50.0,
            risk_label="MEDIUM",
            summary=summary,
            warnings=[warning],
            fallback_used=True,
            raw_response_excerpt=self._raw_excerpt(raw_excerpt),
            timestamp=utc_now(),
        )

    @staticmethod
    def _warnings_list(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            cleaned = value.strip()
            return [cleaned] if cleaned else []
        return []

    @staticmethod
    def _raw_excerpt(value: object, *, max_len: int = 280) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        if len(text) <= max_len:
            return text
        return f"{text[:max_len]}..."

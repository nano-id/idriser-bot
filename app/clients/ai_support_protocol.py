"""Protocol and helpers for provider-agnostic AI support clients."""

from __future__ import annotations

import json
import re
from typing import Any, Literal, Protocol, TypedDict


RiskLabel = Literal["LOW", "MEDIUM", "HIGH"]

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", flags=re.IGNORECASE | re.DOTALL)


class AISupportResult(TypedDict):
    """Normalized output contract shared by all AI providers."""

    support_score: float
    narrative_strength: float
    risk_label: RiskLabel
    summary: str
    warnings: list[str]
    fallback_used: bool
    raw_response_excerpt: str | None


class AISupportClientProtocol(Protocol):
    """Provider-agnostic client interface."""

    @property
    def is_configured(self) -> bool:
        """True when required provider credentials are available."""

    def evaluate_context(self, *, context: dict[str, Any]) -> AISupportResult:
        """Evaluate compact signal context and return normalized payload."""


def parse_json_text(content: str) -> dict[str, Any]:
    """Parse JSON payload from model output, including fenced blocks."""
    text = content.strip()
    if text.startswith("```"):
        match = _JSON_FENCE_RE.search(text)
        if match:
            text = match.group(1).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            msg = "content is not valid JSON"
            raise ValueError(msg) from None
        payload = json.loads(text[start : end + 1])

    if not isinstance(payload, dict):
        msg = "parsed JSON is not an object"
        raise ValueError(msg)
    return payload


def normalize_ai_payload(payload: dict[str, Any]) -> AISupportResult:
    """Normalize provider response payload to shared contract."""
    support_score = _coerce_score(payload.get("support_score"))
    narrative_strength = _coerce_score(payload.get("narrative_strength"))

    risk_label_raw = payload.get("risk_label")
    risk_label = str(risk_label_raw).strip().upper() if risk_label_raw is not None else ""
    if risk_label not in {"LOW", "MEDIUM", "HIGH"}:
        msg = f"invalid risk_label: {risk_label_raw}"
        raise ValueError(msg)

    summary_raw = payload.get("summary")
    summary = str(summary_raw).strip() if summary_raw is not None else ""
    if not summary:
        msg = "summary is missing"
        raise ValueError(msg)

    warnings_raw = payload.get("warnings", [])
    warnings: list[str]
    if isinstance(warnings_raw, list):
        warnings = [str(item).strip() for item in warnings_raw if str(item).strip()]
    elif isinstance(warnings_raw, str):
        cleaned = warnings_raw.strip()
        warnings = [cleaned] if cleaned else []
    else:
        warnings = []

    return AISupportResult(
        support_score=support_score,
        narrative_strength=narrative_strength,
        risk_label=risk_label,
        summary=summary,
        warnings=warnings,
        fallback_used=False,
        raw_response_excerpt=None,
    )


def build_fallback_result(
    *,
    summary: str,
    warnings: list[str],
    raw_response_excerpt: str | None,
) -> AISupportResult:
    """Build safe fallback payload when provider request/parse fails."""
    return AISupportResult(
        support_score=50.0,
        narrative_strength=50.0,
        risk_label="MEDIUM",
        summary=summary,
        warnings=warnings,
        fallback_used=True,
        raw_response_excerpt=excerpt_text(raw_response_excerpt) if raw_response_excerpt else None,
    )


def excerpt_text(value: str | None, *, max_len: int = 280) -> str | None:
    """Trim long raw text for safe API/model transport."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}..."


def _coerce_score(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        msg = "score field is missing"
        raise ValueError(msg)
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        msg = f"invalid score value: {value}"
        raise ValueError(msg) from exc
    bounded = max(0.0, min(100.0, numeric))
    return round(bounded, 2)


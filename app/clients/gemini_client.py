"""Gemini REST client for supportive scoring."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.clients.ai_support_protocol import (
    AISupportResult,
    build_fallback_result,
    excerpt_text,
    normalize_ai_payload,
    parse_json_text,
)
from app.clients.base_http import BaseHTTPClient, HTTPClientError
from app.config.settings import Settings


LOGGER = logging.getLogger(__name__)


class GeminiClient:
    """Call Gemini generateContent endpoint and normalize outputs."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings
        api_key = settings.gemini_api_key.strip()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-goog-api-key"] = api_key

        self.http_client = BaseHTTPClient(
            base_url=settings.gemini_base_url,
            timeout_seconds=settings.gemini_timeout_seconds,
            max_retries=settings.gemini_max_retries,
            backoff_seconds=settings.request_backoff_seconds,
            default_headers=headers,
        )
        self._api_key_present = bool(api_key)

    @property
    def is_configured(self) -> bool:
        """Return True when API key is available for Gemini requests."""
        return self._api_key_present

    def evaluate_context(self, *, context: dict[str, Any]) -> AISupportResult:
        """Request supportive scoring for one compact coin context."""
        if not self.is_configured:
            return build_fallback_result(
                summary="Gemini skipped: missing API key",
                warnings=["gemini_missing_api_key"],
                raw_response_excerpt=None,
            )

        path = f"/v1beta/models/{self.settings.gemini_model}:generateContent"
        prompt = json.dumps(
            {
                "task": "supportive_assessment_only",
                "requirements": {
                    "support_score_range": "0-100",
                    "narrative_strength_range": "0-100",
                    "risk_label_values": ["LOW", "MEDIUM", "HIGH"],
                    "no_assumptions": True,
                    "json_only": True,
                },
                "context": context,
            },
            separators=(",", ":"),
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                "Use only provided numeric context. "
                                "Do not invent unknown data. "
                                "Return valid JSON with keys: "
                                "support_score, narrative_strength, risk_label, summary, warnings.\n"
                                f"{prompt}"
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": self.settings.gemini_temperature,
                "responseMimeType": "application/json",
            },
        }

        try:
            raw_response = self.http_client.request_json(
                "POST",
                path,
                json_payload=payload,
            )
        except HTTPClientError as exc:
            LOGGER.warning("Gemini request failed: %s", exc)
            return build_fallback_result(
                summary="Gemini fallback: request failed",
                warnings=["gemini_request_failed"],
                raw_response_excerpt=str(exc),
            )

        return self._normalize_response(raw_response)

    def _normalize_response(self, raw_response: Any) -> AISupportResult:
        try:
            content = self._extract_text(raw_response)
            parsed = parse_json_text(content)
            normalized = normalize_ai_payload(parsed)
            normalized["raw_response_excerpt"] = excerpt_text(content)
            return normalized
        except ValueError as exc:
            LOGGER.warning("Gemini response parse failed: %s", exc)
            return build_fallback_result(
                summary="Gemini fallback: response parse failed",
                warnings=["gemini_parse_failed"],
                raw_response_excerpt=excerpt_text(str(raw_response)),
            )

    @staticmethod
    def _extract_text(raw_response: Any) -> str:
        if not isinstance(raw_response, dict):
            msg = "response payload is not an object"
            raise ValueError(msg)

        candidates = raw_response.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            msg = "response candidates are missing"
            raise ValueError(msg)

        first = candidates[0]
        if not isinstance(first, dict):
            msg = "response candidate is invalid"
            raise ValueError(msg)

        content = first.get("content")
        if not isinstance(content, dict):
            msg = "response content is invalid"
            raise ValueError(msg)

        parts = content.get("parts")
        if not isinstance(parts, list) or not parts:
            msg = "response parts are missing"
            raise ValueError(msg)

        first_part = parts[0]
        if not isinstance(first_part, dict):
            msg = "response part is invalid"
            raise ValueError(msg)

        text = first_part.get("text")
        if not isinstance(text, str) or not text.strip():
            msg = "response text is empty"
            raise ValueError(msg)
        return text

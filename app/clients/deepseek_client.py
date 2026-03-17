"""DeepSeek chat-completions client for supportive scoring."""

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


class DeepSeekClient:
    """Call DeepSeek and normalize responses into strict support payloads."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings
        api_key = settings.deepseek_api_key.strip()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.http_client = BaseHTTPClient(
            base_url=settings.deepseek_base_url,
            timeout_seconds=settings.deepseek_timeout_seconds,
            max_retries=settings.deepseek_max_retries,
            backoff_seconds=settings.request_backoff_seconds,
            default_headers=headers,
        )
        self._api_key_present = bool(api_key)

    @property
    def is_configured(self) -> bool:
        """Return True when API key is available for live requests."""
        return self._api_key_present

    def evaluate_context(self, *, context: dict[str, Any]) -> AISupportResult:
        """Request supportive scoring for one compact coin context."""
        if not self.is_configured:
            return build_fallback_result(
                summary="DeepSeek skipped: missing API key",
                warnings=["deepseek_missing_api_key"],
                raw_response_excerpt=None,
            )

        payload = {
            "model": self.settings.deepseek_model,
            "temperature": self.settings.deepseek_temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a supportive crypto signal assistant. "
                        "Use only the provided context. "
                        "Do not assume unknown data. "
                        "Return strictly valid JSON with keys: "
                        "support_score, narrative_strength, risk_label, summary, warnings."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": "supportive_assessment_only",
                            "requirements": {
                                "support_score_range": "0-100",
                                "narrative_strength_range": "0-100",
                                "risk_label_values": ["LOW", "MEDIUM", "HIGH"],
                            },
                            "context": context,
                        },
                        separators=(",", ":"),
                    ),
                },
            ],
        }

        try:
            raw_response = self.http_client.request_json(
                "POST",
                "/chat/completions",
                json_payload=payload,
            )
        except HTTPClientError as exc:
            LOGGER.warning("DeepSeek request failed: %s", exc)
            return build_fallback_result(
                summary="DeepSeek fallback: request failed",
                warnings=["deepseek_request_failed"],
                raw_response_excerpt=str(exc),
            )

        return self._normalize_response(raw_response)

    def _normalize_response(self, raw_response: Any) -> AISupportResult:
        try:
            content = self._extract_message_content(raw_response)
            parsed = parse_json_text(content)
            normalized = normalize_ai_payload(parsed)
            normalized["raw_response_excerpt"] = excerpt_text(content)
            return normalized
        except ValueError as exc:
            LOGGER.warning("DeepSeek response parse failed: %s", exc)
            return build_fallback_result(
                summary="DeepSeek fallback: response parse failed",
                warnings=["deepseek_parse_failed"],
                raw_response_excerpt=excerpt_text(str(raw_response)),
            )

    @staticmethod
    def _extract_message_content(raw_response: Any) -> str:
        if not isinstance(raw_response, dict):
            msg = "response payload is not an object"
            raise ValueError(msg)

        choices = raw_response.get("choices")
        if not isinstance(choices, list) or not choices:
            msg = "response choices are missing"
            raise ValueError(msg)

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            msg = "response choice is invalid"
            raise ValueError(msg)

        message = first_choice.get("message")
        if not isinstance(message, dict):
            msg = "response message is invalid"
            raise ValueError(msg)

        content = message.get("content")
        if isinstance(content, str):
            if content.strip():
                return content
            msg = "response content is empty"
            raise ValueError(msg)

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            if parts:
                return "\n".join(parts)

        msg = "response content format is unsupported"
        raise ValueError(msg)


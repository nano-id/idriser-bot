"""Gemini client tests with mocked HTTP responses."""

from __future__ import annotations

import json

from app.clients.base_http import HTTPClientError
from app.clients.gemini_client import GeminiClient
from app.config.settings import Settings


def _build_settings(*, api_key: str = "gemini-test-key") -> Settings:
    return Settings(
        _env_file=None,
        llm_provider="gemini",
        gemini_api_key=api_key,
        gemini_base_url="https://generativelanguage.googleapis.com",
        gemini_model="gemini-2.0-flash",
        gemini_timeout_seconds=10,
        gemini_max_retries=1,
        gemini_temperature=0.1,
    )


def test_gemini_client_parses_successful_json(monkeypatch) -> None:
    settings = _build_settings()
    client = GeminiClient(settings=settings)

    payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "support_score": 81,
                                    "narrative_strength": 76,
                                    "risk_label": "LOW",
                                    "summary": "Momentum and stability are supportive.",
                                    "warnings": ["No external/news context provided."],
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }
    monkeypatch.setattr(client.http_client, "request_json", lambda *args, **kwargs: payload)

    result = client.evaluate_context(context={"symbol": "BTC/USDT"})
    assert result["fallback_used"] is False
    assert result["support_score"] == 81.0
    assert result["narrative_strength"] == 76.0
    assert result["risk_label"] == "LOW"


def test_gemini_client_fallback_on_parse_failure(monkeypatch) -> None:
    settings = _build_settings()
    client = GeminiClient(settings=settings)

    payload = {"candidates": [{"content": {"parts": [{"text": "{bad-json"}]}}]}
    monkeypatch.setattr(client.http_client, "request_json", lambda *args, **kwargs: payload)

    result = client.evaluate_context(context={"symbol": "ETH/USDT"})
    assert result["fallback_used"] is True
    assert "gemini_parse_failed" in result["warnings"]


def test_gemini_client_fallback_on_request_failure(monkeypatch) -> None:
    settings = _build_settings()
    client = GeminiClient(settings=settings)

    def _raise_http_error(*args, **kwargs):
        raise HTTPClientError("timeout")

    monkeypatch.setattr(client.http_client, "request_json", _raise_http_error)
    result = client.evaluate_context(context={"symbol": "BNB/USDT"})
    assert result["fallback_used"] is True
    assert "gemini_request_failed" in result["warnings"]

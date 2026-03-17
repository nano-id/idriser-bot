"""DeepSeek client tests with mocked HTTP responses."""

from __future__ import annotations

import json

from app.clients.base_http import HTTPClientError
from app.clients.deepseek_client import DeepSeekClient
from app.config.settings import Settings


def _build_settings(*, api_key: str = "test-key") -> Settings:
    return Settings(
        _env_file=None,
        deepseek_enabled=True,
        deepseek_api_key=api_key,
        deepseek_base_url="https://api.deepseek.com",
        deepseek_model="deepseek-chat",
        deepseek_timeout_seconds=10,
        deepseek_max_retries=1,
        deepseek_temperature=0.1,
    )


def test_deepseek_client_parses_successful_json(monkeypatch) -> None:
    settings = _build_settings()
    client = DeepSeekClient(settings=settings)

    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "support_score": 78,
                            "narrative_strength": 71,
                            "risk_label": "LOW",
                            "summary": "Trend alignment and stability look supportive.",
                            "warnings": ["No external/news context provided."],
                        }
                    )
                }
            }
        ]
    }

    monkeypatch.setattr(client.http_client, "request_json", lambda *args, **kwargs: payload)

    result = client.evaluate_context(context={"symbol": "BTC/USDT"})
    assert result["fallback_used"] is False
    assert result["support_score"] == 78.0
    assert result["narrative_strength"] == 71.0
    assert result["risk_label"] == "LOW"
    assert "supportive" in result["summary"].lower()


def test_deepseek_client_fallback_on_malformed_json(monkeypatch) -> None:
    settings = _build_settings()
    client = DeepSeekClient(settings=settings)

    payload = {"choices": [{"message": {"content": "{bad-json"}}]}
    monkeypatch.setattr(client.http_client, "request_json", lambda *args, **kwargs: payload)

    result = client.evaluate_context(context={"symbol": "ETH/USDT"})
    assert result["fallback_used"] is True
    assert "deepseek_parse_failed" in result["warnings"]


def test_deepseek_client_fallback_on_request_failure(monkeypatch) -> None:
    settings = _build_settings()
    client = DeepSeekClient(settings=settings)

    def _raise_http_error(*args, **kwargs):
        raise HTTPClientError("timeout")

    monkeypatch.setattr(client.http_client, "request_json", _raise_http_error)

    result = client.evaluate_context(context={"symbol": "BNB/USDT"})
    assert result["fallback_used"] is True
    assert "deepseek_request_failed" in result["warnings"]


"""Factory for provider-agnostic AI support clients."""

from __future__ import annotations

from typing import Any

from app.clients.ai_support_protocol import AISupportClientProtocol, AISupportResult, build_fallback_result
from app.clients.deepseek_client import DeepSeekClient
from app.clients.gemini_client import GeminiClient
from app.config.settings import Settings


class DisabledAIClient:
    """No-op client used when LLM provider is disabled."""

    @property
    def is_configured(self) -> bool:
        return False

    def evaluate_context(self, *, context: dict[str, Any]) -> AISupportResult:
        return build_fallback_result(
            summary="AI provider disabled",
            warnings=["llm_provider_disabled"],
            raw_response_excerpt=None,
        )


def create_ai_support_client(*, settings: Settings) -> AISupportClientProtocol:
    """Create provider-specific AI support client from settings."""
    provider = settings.llm_provider
    if provider == "deepseek":
        return DeepSeekClient(settings=settings)
    if provider == "gemini":
        return GeminiClient(settings=settings)
    return DisabledAIClient()


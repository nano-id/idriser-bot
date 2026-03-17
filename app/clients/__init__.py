"""Client exports."""

from app.clients.ai_client_factory import create_ai_support_client
from app.clients.ai_support_protocol import AISupportClientProtocol, AISupportResult
from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.clients.ccxt_client import CCXTUniverseClient
from app.clients.deepseek_client import DeepSeekClient
from app.clients.gemini_client import GeminiClient

__all__ = [
    "CCXTUniverseClient",
    "CCXTMarketDataClient",
    "AISupportClientProtocol",
    "AISupportResult",
    "DeepSeekClient",
    "GeminiClient",
    "create_ai_support_client",
]

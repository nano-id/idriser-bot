"""CCXT integration used by the universe builder."""

from __future__ import annotations

import logging
from typing import Any

import ccxt


LOGGER = logging.getLogger(__name__)


class CCXTUniverseClient:
    """Fetch tradable markets from a configured exchange."""

    def __init__(self, exchange_id: str) -> None:
        self.exchange_id = exchange_id

    def fetch_markets(self) -> list[dict[str, Any]]:
        """Load markets and return as a list of market dicts."""
        if not hasattr(ccxt, self.exchange_id):
            msg = f"Exchange '{self.exchange_id}' is not supported by ccxt"
            raise ValueError(msg)

        exchange_class = getattr(ccxt, self.exchange_id)
        exchange = exchange_class({"enableRateLimit": True})
        try:
            markets = exchange.load_markets()
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Failed loading markets from %s", self.exchange_id)
            raise RuntimeError(f"Failed to load markets from {self.exchange_id}: {exc}") from exc
        finally:
            try:
                exchange.close()
            except Exception:  # noqa: BLE001
                pass

        return list(markets.values())

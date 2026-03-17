"""Coin universe builder for Step 1 scan input."""

from __future__ import annotations

import logging

from pydantic import ValidationError

from app.clients.ccxt_client import CCXTUniverseClient
from app.config.settings import Settings
from app.models.universe import UniverseAsset
from app.normalization.symbols import split_base_quote
from app.universe.filters import should_exclude_market


LOGGER = logging.getLogger(__name__)


class UniverseBuilder:
    """Build a normalized coin universe from CCXT markets."""

    def __init__(self, settings: Settings, ccxt_client: CCXTUniverseClient) -> None:
        self.settings = settings
        self.ccxt_client = ccxt_client

    def build(self, size: int | None = None) -> list[UniverseAsset]:
        """Build universe with exchange markets and safe fallback."""
        target_size = size or self.settings.universe_size
        try:
            assets = self._build_from_exchange(target_size=target_size)
            if assets:
                return assets
            LOGGER.warning("Exchange universe returned no assets; using fallback symbols")
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Failed to build exchange universe (%s). Falling back to static symbols.", exc)

        return self._build_from_fallback(target_size=target_size)

    def _build_from_exchange(self, target_size: int) -> list[UniverseAsset]:
        markets = self.ccxt_client.fetch_markets()
        allowed_quotes = {quote.upper() for quote in self.settings.universe_quote_assets}
        quote_priority = {quote.upper(): idx for idx, quote in enumerate(self.settings.universe_quote_assets)}
        preferred_bases: list[str] = []
        for raw_symbol in self.settings.fallback_symbols:
            base, _ = split_base_quote(raw_symbol)
            if base:
                preferred_bases.append(base.upper())
        preferred_base_priority = {base: idx for idx, base in enumerate(preferred_bases)}

        candidates: list[UniverseAsset] = []
        for market in markets:
            if not market.get("active", True):
                continue
            if not market.get("spot", True):
                continue

            symbol = str(market.get("symbol", "")).upper()
            base_asset = str(market.get("base", "")).upper()
            quote_asset = str(market.get("quote", "")).upper()

            if should_exclude_market(
                symbol=symbol,
                base_asset=base_asset,
                quote_asset=quote_asset,
                allowed_quotes=allowed_quotes,
                excluded_base_suffixes=self.settings.excluded_base_suffixes,
                excluded_base_prefixes=self.settings.excluded_base_prefixes,
                excluded_symbol_keywords=self.settings.excluded_symbol_keywords,
            ):
                continue

            try:
                candidates.append(
                    UniverseAsset(
                        exchange_symbol=symbol,
                        base_asset=base_asset,
                        quote_asset=quote_asset,
                    )
                )
            except ValidationError:
                LOGGER.debug("Skipping invalid market symbol=%s base=%s quote=%s", symbol, base_asset, quote_asset)
                continue

        # Deduplicate by base asset while prioritizing configured quote order.
        candidates.sort(
            key=lambda item: (
                preferred_base_priority.get(item.base_asset, 10_000),
                quote_priority.get(item.quote_asset, 10_000),
                item.base_asset,
                item.exchange_symbol,
            )
        )
        deduped: dict[str, UniverseAsset] = {}
        for asset in candidates:
            if asset.base_asset not in deduped:
                deduped[asset.base_asset] = asset
            if len(deduped) >= target_size:
                break

        selected = list(deduped.values())
        LOGGER.info("Built exchange universe with %s assets", len(selected))
        return selected

    def _build_from_fallback(self, target_size: int) -> list[UniverseAsset]:
        assets: list[UniverseAsset] = []
        for raw_symbol in self.settings.fallback_symbols:
            base, quote = split_base_quote(raw_symbol)
            if quote is None:
                continue
            assets.append(
                UniverseAsset(
                    exchange_symbol=f"{base}/{quote}",
                    base_asset=base,
                    quote_asset=quote,
                )
            )
            if len(assets) >= target_size:
                break
        LOGGER.info("Built fallback universe with %s assets", len(assets))
        return assets

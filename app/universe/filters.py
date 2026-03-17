"""Filtering helpers for universe construction."""

from __future__ import annotations

from app.normalization.symbols import is_likely_leveraged_token


def should_exclude_market(
    *,
    symbol: str,
    base_asset: str,
    quote_asset: str,
    allowed_quotes: set[str],
    excluded_base_suffixes: list[str],
    excluded_base_prefixes: list[str],
    excluded_symbol_keywords: list[str],
) -> bool:
    """Return True if a market should be excluded from the coin universe."""
    if not symbol or not base_asset or not quote_asset:
        return True

    if quote_asset.upper() not in allowed_quotes:
        return True

    if ":" in symbol:
        # Common derivatives notation in CCXT symbols.
        return True

    if is_likely_leveraged_token(base_asset, excluded_suffixes=excluded_base_suffixes):
        return True

    upper_base = base_asset.upper()
    for prefix in excluded_base_prefixes:
        if upper_base.startswith(prefix.upper()):
            return True

    upper_symbol = symbol.upper()
    for keyword in excluded_symbol_keywords:
        if keyword.upper() in upper_symbol:
            return True

    return False

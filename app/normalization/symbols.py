"""Symbol normalization and provider mapping utilities."""

from __future__ import annotations

import re


LEVERAGED_SUFFIX_RE = re.compile(r"(UP|DOWN|BULL|BEAR|[0-9]+L|[0-9]+S)$")


def normalize_exchange_symbol(symbol: str) -> str:
    """Normalize exchange symbols into BASE/QUOTE format where possible."""
    cleaned = symbol.strip().upper()
    if "/" in cleaned:
        base, quote = cleaned.split("/", 1)
        return f"{base.strip()}/{quote.strip()}"
    return cleaned


def split_base_quote(symbol: str) -> tuple[str, str | None]:
    """Split `BASE/QUOTE` symbol and return uppercase parts."""
    normalized = normalize_exchange_symbol(symbol)
    if "/" not in normalized:
        return normalized, None
    base, quote = normalized.split("/", 1)
    return base, quote


def is_likely_leveraged_token(base_asset: str, excluded_suffixes: list[str] | None = None) -> bool:
    """Identify common leveraged token naming patterns."""
    base = base_asset.upper().strip()
    if excluded_suffixes:
        for suffix in excluded_suffixes:
            if base.endswith(suffix.upper()):
                return True
    return bool(LEVERAGED_SUFFIX_RE.search(base))


def normalize_provider_asset(base_asset: str) -> str:
    """Normalize base asset ticker for providers that use uppercase tickers."""
    return base_asset.upper().strip()

"""Models for coin universe entries."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UniverseAsset(BaseModel):
    """Represents a normalized tradable asset from the universe builder."""

    exchange_symbol: str
    base_asset: str = Field(min_length=2)
    quote_asset: str = Field(min_length=2)

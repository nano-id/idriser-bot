"""Symbol normalization tests."""

from __future__ import annotations

from app.normalization.symbols import (
    is_likely_leveraged_token,
    normalize_exchange_symbol,
    split_base_quote,
)


def test_normalize_exchange_symbol() -> None:
    assert normalize_exchange_symbol(" btc/usdt ") == "BTC/USDT"
    assert normalize_exchange_symbol("ethusdt") == "ETHUSDT"


def test_split_base_quote() -> None:
    base, quote = split_base_quote("SOL/USDT")
    assert base == "SOL"
    assert quote == "USDT"


def test_leveraged_detection() -> None:
    assert is_likely_leveraged_token("ETHUP")
    assert is_likely_leveraged_token("BTC3L")
    assert not is_likely_leveraged_token("BTC")


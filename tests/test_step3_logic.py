"""Step 3 market regime filter tests with mocked market data."""

from __future__ import annotations

from app.config.settings import Settings
from app.filters.market_regime_filter import CCXTMarketRegimeFilter


class FakeMarketDataClient:
    """Market data stub for Step3 tests."""

    def __init__(
        self,
        *,
        ohlcv_map: dict[tuple[str, str], list[list[float]]],
        funding_map: dict[str, float] | None = None,
        oi_map: dict[str, float] | None = None,
    ) -> None:
        self.ohlcv_map = ohlcv_map
        self.funding_map = funding_map or {}
        self.oi_map = oi_map or {}

    def fetch_ohlcv(self, *, symbol: str, timeframe: str, limit: int) -> list[list[float]]:
        rows = self.ohlcv_map.get((symbol, timeframe))
        if rows is None:
            raise RuntimeError(f"No OHLCV data for {symbol}:{timeframe}")
        return rows[:limit]

    def fetch_funding_rate(self, *, symbol: str) -> float | None:
        return self.funding_map.get(symbol)

    def fetch_open_interest(self, *, symbol: str) -> float | None:
        return self.oi_map.get(symbol)


def _build_ohlcv(
    *,
    length: int,
    start_price: float,
    drift: float,
    final_multiplier: float = 1.0,
) -> list[list[float]]:
    rows: list[list[float]] = []
    close = start_price
    for idx in range(length):
        close = close + drift
        if idx == length - 1:
            close *= final_multiplier
        open_price = close * 0.999
        high = close * 1.008
        low = close * 0.992
        volume = 2_000 + idx * 3
        rows.append([1_700_000_000_000 + idx * 14_400_000, open_price, high, low, close, volume])
    return rows


def test_step3_bullish_regime_pass() -> None:
    settings = Settings(
        _env_file=None,
        regime_ohlcv_limit=220,
        regime_min_ohlcv_rows=120,
        regime_score_bullish_threshold=60,
        regime_score_neutral_threshold=40,
        regime_breadth_symbol_count=3,
        regime_breadth_min_samples=2,
    )
    tf = settings.regime_timeframe
    ohlcv_map = {
        (settings.regime_btc_symbol, tf): _build_ohlcv(length=200, start_price=30_000, drift=95),
        ("ETH/USDT", tf): _build_ohlcv(length=200, start_price=1_800, drift=7),
        ("SOL/USDT", tf): _build_ohlcv(length=200, start_price=40, drift=0.25),
        ("BNB/USDT", tf): _build_ohlcv(length=200, start_price=240, drift=0.9),
    }
    client = FakeMarketDataClient(
        ohlcv_map=ohlcv_map,
        funding_map={settings.regime_btc_symbol: 0.0002},
        oi_map={settings.regime_btc_symbol: 50_000_000},
    )
    regime_filter = CCXTMarketRegimeFilter(settings=settings, market_data_client=client)

    result = regime_filter.evaluate(
        symbol="ETH/USDT",
        market_symbols=[settings.regime_btc_symbol, "ETH/USDT", "SOL/USDT", "BNB/USDT"],
    )
    assert result.regime_status == "BULLISH"
    assert result.step3_pass is True


def test_step3_detects_danger_regime() -> None:
    settings = Settings(
        _env_file=None,
        regime_ohlcv_limit=220,
        regime_min_ohlcv_rows=120,
        regime_drawdown_danger_pct=0.05,
        regime_atr_danger_pct=0.08,
        regime_breadth_enabled=False,
        regime_derivatives_enabled=False,
    )
    tf = settings.regime_timeframe
    btc_rows = _build_ohlcv(length=200, start_price=30_000, drift=40, final_multiplier=0.72)
    client = FakeMarketDataClient(ohlcv_map={(settings.regime_btc_symbol, tf): btc_rows})
    regime_filter = CCXTMarketRegimeFilter(settings=settings, market_data_client=client)

    result = regime_filter.evaluate(symbol="ETH/USDT", market_symbols=[settings.regime_btc_symbol])
    assert result.regime_status == "DANGER"
    assert result.step3_pass is False


def test_step3_bearish_veto_behavior() -> None:
    settings = Settings(
        _env_file=None,
        regime_ohlcv_limit=220,
        regime_min_ohlcv_rows=120,
        regime_score_bullish_threshold=75,
        regime_score_neutral_threshold=55,
        regime_breadth_symbol_count=3,
        regime_breadth_min_samples=2,
        regime_atr_danger_pct=0.50,
        regime_drawdown_danger_pct=0.50,
        regime_allow_neutral=False,
        regime_veto_if_bearish=True,
    )
    tf = settings.regime_timeframe
    ohlcv_map = {
        (settings.regime_btc_symbol, tf): _build_ohlcv(length=200, start_price=30_000, drift=-25),
        ("ETH/USDT", tf): _build_ohlcv(length=200, start_price=1_800, drift=-1.2),
        ("SOL/USDT", tf): _build_ohlcv(length=200, start_price=40, drift=-0.03),
        ("BNB/USDT", tf): _build_ohlcv(length=200, start_price=240, drift=-0.15),
    }
    client = FakeMarketDataClient(
        ohlcv_map=ohlcv_map,
        funding_map={settings.regime_btc_symbol: 0.0},
        oi_map={settings.regime_btc_symbol: 10_000_000},
    )
    regime_filter = CCXTMarketRegimeFilter(settings=settings, market_data_client=client)

    result = regime_filter.evaluate(
        symbol="ETH/USDT",
        market_symbols=[settings.regime_btc_symbol, "ETH/USDT", "SOL/USDT", "BNB/USDT"],
    )
    assert result.regime_status == "BEARISH"
    assert result.step3_pass is False


def test_step3_fallback_when_derivatives_unavailable() -> None:
    settings = Settings(
        _env_file=None,
        regime_ohlcv_limit=220,
        regime_min_ohlcv_rows=120,
        regime_breadth_enabled=False,
        regime_derivatives_enabled=True,
    )
    tf = settings.regime_timeframe
    client = FakeMarketDataClient(
        ohlcv_map={(settings.regime_btc_symbol, tf): _build_ohlcv(length=200, start_price=30_000, drift=35)},
        funding_map={},
        oi_map={},
    )
    regime_filter = CCXTMarketRegimeFilter(settings=settings, market_data_client=client)

    result = regime_filter.evaluate(symbol="ETH/USDT", market_symbols=[settings.regime_btc_symbol])
    assert result.fallback_used is True
    assert "funding_rate" in result.unavailable_risk_metrics
    assert "open_interest" in result.unavailable_risk_metrics

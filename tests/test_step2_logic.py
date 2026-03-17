"""Step 2 technical filter tests with mocked OHLCV."""

from __future__ import annotations

from app.config.settings import Settings
from app.filters.technical_filter import CCXTTechnicalFilter


class FakeMarketDataClient:
    """Simple market data stub for Step2 tests."""

    def __init__(self, data_map: dict[tuple[str, str], list[list[float]]]) -> None:
        self.data_map = data_map

    def fetch_ohlcv(self, *, symbol: str, timeframe: str, limit: int) -> list[list[float]]:
        return self.data_map.get((symbol, timeframe), [])[:limit]


def _build_ohlcv(
    *,
    length: int,
    start_price: float,
    drift: float,
    final_spike_pct: float = 0.0,
    final_volume_multiplier: float = 1.0,
) -> list[list[float]]:
    rows: list[list[float]] = []
    close = start_price
    base_volume = 1_000.0
    for idx in range(length):
        close = close + drift
        if idx == length - 1 and final_spike_pct:
            close = close * (1 + final_spike_pct)
        open_price = close * 0.998
        high = close * 1.005
        low = close * 0.995
        volume = base_volume + idx * 5
        if idx == length - 1:
            volume *= final_volume_multiplier
        rows.append([1_700_000_000_000 + idx * 14_400_000, open_price, high, low, close, volume])
    return rows


def test_step2_passes_for_bullish_breakout_with_volume() -> None:
    settings = Settings(
        _env_file=None,
        technical_use_secondary_confirmation=False,
        technical_pass_threshold=55,
        technical_min_ohlcv_rows=80,
        technical_ohlcv_limit=200,
        technical_pullback_tolerance_pct=0.06,
    )
    rows = _build_ohlcv(
        length=180,
        start_price=100,
        drift=0.9,
        final_spike_pct=0.005,
        final_volume_multiplier=3.0,
    )
    client = FakeMarketDataClient({("ETH/USDT", settings.technical_main_timeframe): rows})
    technical_filter = CCXTTechnicalFilter(settings=settings, market_data_client=client)

    result = technical_filter.evaluate(symbol="ETH/USDT", base_asset="ETH")
    assert result.step2_pass is True
    assert result.step2_score >= settings.technical_pass_threshold
    assert result.technical_flags.get("trend_ok") is True
    assert result.technical_flags.get("entry_signal") is True


def test_step2_rejects_overextended_noisy_setup() -> None:
    settings = Settings(
        _env_file=None,
        technical_use_secondary_confirmation=False,
        technical_pass_threshold=65,
        technical_min_ohlcv_rows=80,
        technical_ohlcv_limit=200,
        technical_volume_ratio_min=1.3,
    )
    rows = _build_ohlcv(
        length=180,
        start_price=100,
        drift=0.4,
        final_spike_pct=0.35,
        final_volume_multiplier=0.15,
    )
    client = FakeMarketDataClient({("ETH/USDT", settings.technical_main_timeframe): rows})
    technical_filter = CCXTTechnicalFilter(settings=settings, market_data_client=client)

    result = technical_filter.evaluate(symbol="ETH/USDT", base_asset="ETH")
    assert result.step2_pass is False
    assert result.technical_flags.get("overextended") is True
    assert result.technical_flags.get("hard_fail") is True


def test_step2_handles_missing_ohlcv_data() -> None:
    settings = Settings(
        _env_file=None,
        technical_use_secondary_confirmation=False,
        technical_min_ohlcv_rows=120,
        technical_ohlcv_limit=200,
    )
    short_rows = _build_ohlcv(length=30, start_price=100, drift=0.2)
    client = FakeMarketDataClient({("ETH/USDT", settings.technical_main_timeframe): short_rows})
    technical_filter = CCXTTechnicalFilter(settings=settings, market_data_client=client)

    result = technical_filter.evaluate(symbol="ETH/USDT", base_asset="ETH")
    assert result.step2_pass is False
    assert "ohlcv_main_timeframe" in result.missing_technical_data


def test_step2_requires_volume_and_adx_support_for_trend_continuation() -> None:
    settings = Settings(
        _env_file=None,
        technical_use_secondary_confirmation=False,
        technical_pullback_tolerance_pct=0.03,
    )
    client = FakeMarketDataClient({})
    technical_filter = CCXTTechnicalFilter(settings=settings, market_data_client=client)
    snapshot = {
        "close": 102.0,
        "recent_high": 104.0,
        "ema_fast": 101.5,
        "ema_slow": 100.0,
        "rsi": 58.0,
        "rsi_prev": 54.0,
        "macd_hist": 0.2,
    }

    entry_score, flags, _ = technical_filter._evaluate_entry_pattern(
        technical_snapshot=snapshot,
        trend_flags={"trend_ok": True, "adx_ok": False},
        volume_flags={"volume_ok": False},
    )
    assert entry_score == 0.0
    assert flags["continuation_supported"] is False
    assert flags["entry_signal"] is False

    entry_score_supported, flags_supported, _ = technical_filter._evaluate_entry_pattern(
        technical_snapshot=snapshot,
        trend_flags={"trend_ok": True, "adx_ok": True},
        volume_flags={"volume_ok": False},
    )
    assert entry_score_supported == 0.0
    assert flags_supported["continuation_supported"] is False
    assert flags_supported["entry_signal"] is False

    snapshot["secondary_confirm"] = True
    entry_score_supported, flags_supported, _ = technical_filter._evaluate_entry_pattern(
        technical_snapshot=snapshot,
        trend_flags={"trend_ok": True, "adx_ok": True},
        volume_flags={"volume_ok": True},
    )
    assert entry_score_supported == 0.7
    assert flags_supported["continuation_supported"] is True
    assert flags_supported["entry_signal"] is True


def test_step2_continuation_requires_secondary_confirmation() -> None:
    settings = Settings(
        _env_file=None,
        technical_use_secondary_confirmation=True,
        technical_pullback_tolerance_pct=0.03,
    )
    client = FakeMarketDataClient({})
    technical_filter = CCXTTechnicalFilter(settings=settings, market_data_client=client)
    snapshot = {
        "close": 102.0,
        "recent_high": 104.0,
        "ema_fast": 101.5,
        "ema_slow": 100.0,
        "rsi": 58.0,
        "rsi_prev": 54.0,
        "macd_hist": 0.2,
        "secondary_confirm": False,
    }

    entry_score, flags, _ = technical_filter._evaluate_entry_pattern(
        technical_snapshot=snapshot,
        trend_flags={"trend_ok": True, "adx_ok": True},
        volume_flags={"volume_ok": True},
    )

    assert entry_score == 0.0
    assert flags["trend_continuation"] is False
    assert flags["entry_signal"] is False


def test_step2_breakout_requires_adx_and_rejects_overheated_chase() -> None:
    settings = Settings(
        _env_file=None,
        technical_use_secondary_confirmation=False,
        technical_pullback_tolerance_pct=0.02,
        technical_rsi_extreme=82,
        technical_stoch_overbought=85,
    )
    client = FakeMarketDataClient({})
    technical_filter = CCXTTechnicalFilter(settings=settings, market_data_client=client)

    weak_trend_snapshot = {
        "close": 105.0,
        "recent_high": 104.0,
        "ema_fast": 104.0,
        "ema_slow": 102.0,
        "rsi": 62.0,
        "stoch_k": 78.0,
        "macd_hist": 0.3,
        "secondary_confirm": True,
    }
    entry_score, flags, _ = technical_filter._evaluate_entry_pattern(
        technical_snapshot=weak_trend_snapshot,
        trend_flags={"trend_ok": True, "adx_ok": False},
        volume_flags={"volume_ok": True},
    )
    assert entry_score == 0.0
    assert flags["breakout"] is True
    assert flags["breakout_with_volume"] is False
    assert flags["entry_signal"] is False

    overheated_snapshot = {
        "close": 105.8,
        "recent_high": 104.0,
        "ema_fast": 102.5,
        "ema_slow": 100.5,
        "rsi": 84.0,
        "stoch_k": 96.0,
        "macd_hist": 0.4,
        "secondary_confirm": True,
    }
    entry_score_hot, flags_hot, _ = technical_filter._evaluate_entry_pattern(
        technical_snapshot=overheated_snapshot,
        trend_flags={"trend_ok": True, "adx_ok": True},
        volume_flags={"volume_ok": True},
    )
    assert entry_score_hot == 0.0
    assert flags_hot["breakout"] is True
    assert flags_hot["breakout_overheated"] is True
    assert flags_hot["breakout_with_volume"] is False
    assert flags_hot["entry_signal"] is False

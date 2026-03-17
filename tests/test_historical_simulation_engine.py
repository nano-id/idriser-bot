from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config.settings import Settings
from app.models.runtime_config import RuntimeConfig
from app.pipeline.historical_simulation_engine import HistoricalSimulationEngine


class FakeRuntimeConfigStore:
    def __init__(self, cfg: RuntimeConfig) -> None:
        self.cfg = cfg

    def load(self) -> RuntimeConfig:
        return self.cfg


class StubHistoricalMarketDataClient:
    def __init__(self, rows_by_key: dict[tuple[str, str], list[list[float]]]) -> None:
        self.rows_by_key = rows_by_key

    def fetch_ohlcv_range(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: datetime | int,
        end: datetime | int,
        limit_per_call: int = 1000,
    ) -> list[list[float]]:
        return list(self.rows_by_key.get((symbol, timeframe), []))


def _build_rows(
    *,
    start_at: datetime,
    count: int,
    start_price: float,
    price_step: float,
    base_volume: float,
    boosted_volume_after: int = 0,
) -> list[list[float]]:
    rows: list[list[float]] = []
    for idx in range(count):
        ts = int((start_at + timedelta(minutes=idx)).timestamp() * 1000)
        open_price = start_price + (idx * price_step)
        close_price = open_price + price_step
        high_price = close_price + (price_step * 0.75)
        low_price = open_price - (price_step * 0.25)
        volume = base_volume if idx < boosted_volume_after else base_volume * 3
        rows.append([ts, open_price, high_price, low_price, close_price, volume])
    return rows


def test_historical_simulation_replays_symbol_and_returns_final_equity() -> None:
    history_start = datetime(2026, 1, 1, tzinfo=UTC)
    symbol = "ETH/USDT"
    timeframe = "1m"
    rows_by_key = {
        (symbol, timeframe): _build_rows(
            start_at=history_start,
            count=220,
            start_price=100.0,
            price_step=0.35,
            base_volume=100.0,
            boosted_volume_after=120,
        ),
        ("BTC/USDT", timeframe): _build_rows(
            start_at=history_start,
            count=220,
            start_price=40_000.0,
            price_step=8.0,
            base_volume=500.0,
            boosted_volume_after=120,
        ),
    }
    settings = Settings(
        _env_file=None,
        snapshot_timeframe="1m",
        snapshot_interval_minutes=1,
        decision_horizon="5m",
        supported_decision_horizons=["5m", "15m", "1h"],
        engine_include_step2=True,
        engine_include_step3=True,
        technical_main_timeframe="1m",
        technical_confirmation_timeframe="1m",
        technical_use_secondary_confirmation=False,
        technical_ohlcv_limit=120,
        technical_min_ohlcv_rows=50,
        technical_breakout_lookback=10,
        technical_volume_ratio_min=1.0,
        technical_volume_ratio_strong=1.4,
        regime_timeframe="1m",
        regime_ohlcv_limit=120,
        regime_min_ohlcv_rows=50,
        regime_breadth_enabled=False,
        regime_derivatives_enabled=False,
        regime_allow_neutral=True,
        paper_bot_enabled=True,
        paper_initial_capital=10_000,
        paper_min_signal_score=0.35,
        paper_risk_reward_ratio=0.6,
        paper_atr_stop_multiplier=0.8,
        paper_max_hold_minutes=25,
    )
    engine = HistoricalSimulationEngine(
        settings=settings,
        runtime_config_store=FakeRuntimeConfigStore(RuntimeConfig.from_settings(settings)),  # type: ignore[arg-type]
        market_data_client=StubHistoricalMarketDataClient(rows_by_key),  # type: ignore[arg-type]
    )

    result = engine.run(
        symbol=symbol,
        start_at=history_start + timedelta(minutes=150),
        end_at=history_start + timedelta(minutes=210),
        close_open_positions_at_end=True,
    )

    assert result.symbol == symbol
    assert result.evaluation_count > 0
    assert result.opened_trade_count >= 1
    assert result.closed_trade_count >= 1
    assert result.final_equity > 0
    assert result.metrics.total_closed_trades >= 1
    assert result.metrics.current_equity == result.final_equity
    assert result.total_return_pct == result.metrics.total_return_pct
    assert result.closed_trade_count == result.metrics.total_closed_trades
    assert result.force_closed_at_end in {True, False}
    assert len(result.evaluations) == result.evaluation_count

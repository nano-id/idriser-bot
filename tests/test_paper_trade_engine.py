"""Paper trade engine tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config.settings import Settings
from app.models.hourly_signal import HourlySignal
from app.models.runtime_config import RuntimeConfig
from app.pipeline.paper_portfolio_store import PaperPortfolioStore
from app.pipeline.paper_trade_engine import PaperTradeEngine
from app.pipeline.signal_state_store import SignalStateStore


class FakeRuntimeConfigStore:
    def __init__(self, cfg: RuntimeConfig) -> None:
        self.cfg = cfg

    def load(self) -> RuntimeConfig:
        return self.cfg


def _signal(
    *,
    symbol: str = "BTC/USDT",
    mean_signal: float = 0.8,
    latest_close: float = 100.0,
    step2_pass: bool | None = True,
    step3_pass: bool | None = True,
    final_selected: bool | None = True,
    window_complete: bool = True,
    latest_atr_pct: float = 0.02,
) -> HourlySignal:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return HourlySignal(
        symbol=symbol,
        decision_horizon="1h",
        base_snapshot_timeframe="5m",
        required_snapshots=12,
        window_size=12,
        snapshot_count=12,
        window_start=now,
        window_end=now,
        expected_duration_minutes=60,
        actual_duration_minutes=60,
        mean_signal=mean_signal,
        median_signal=mean_signal,
        signal_stddev=0.02,
        bullish_ratio=0.8,
        last_3_slope=0.01,
        stability_score=0.92,
        fallback_used=False,
        latest_breakout=True,
        step2_score=78.0,
        step2_pass=step2_pass,
        regime_status="BULLISH",
        step3_pass=step3_pass,
        regime_score=82.0,
        final_selected=final_selected,
        aggregate_flags={"window_complete": window_complete},
        feature_snapshot={"latest_close": latest_close, "latest_atr_pct": latest_atr_pct},
    )


def _build_engine(*, settings: Settings) -> tuple[PaperTradeEngine, SignalStateStore, PaperPortfolioStore]:
    runtime_cfg = RuntimeConfig.from_settings(settings)
    runtime_store = FakeRuntimeConfigStore(runtime_cfg)
    signal_store = SignalStateStore()
    portfolio_store = PaperPortfolioStore(initial_capital=settings.paper_initial_capital)
    engine = PaperTradeEngine(
        settings=settings,
        runtime_config_store=runtime_store,  # type: ignore[arg-type]
        signal_state_store=signal_store,
        portfolio_store=portfolio_store,
    )
    return engine, signal_store, portfolio_store


def test_paper_trade_engine_opens_trade_for_valid_signal() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_initial_capital=10_000,
        paper_max_open_positions=3,
        paper_risk_per_trade_pct=0.01,
        paper_min_signal_score=0.6,
        paper_require_window_complete=True,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.84, latest_close=100.0)])

    result = engine.run_once()

    assert result.opened_count == 1
    assert result.closed_count == 0
    assert result.status.open_trade_count == 1
    assert portfolio_store.get_portfolio().cash_balance < settings.paper_initial_capital


def test_paper_trade_engine_respects_step2_step3_requirements() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_require_step2_pass=True,
        paper_require_step3_pass=True,
        paper_min_signal_score=0.6,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals(
        [
            _signal(mean_signal=0.9, step2_pass=False, step3_pass=True),
            _signal(symbol="ETH/USDT", mean_signal=0.92, step2_pass=True, step3_pass=False),
        ]
    )

    result = engine.run_once()

    assert result.opened_count == 0
    assert result.status.open_trade_count == 0
    assert portfolio_store.get_open_trades() == []


def test_paper_trade_engine_requires_final_selected_by_default() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_min_signal_score=0.6,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.9, final_selected=False)])

    result = engine.run_once()

    assert result.opened_count == 0
    assert result.status.open_trade_count == 0
    assert portfolio_store.get_open_trades() == []


def test_paper_trade_engine_closes_trade_on_stop_loss() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_min_signal_score=0.6,
        paper_atr_stop_multiplier=1.0,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.85, latest_close=100.0, latest_atr_pct=0.02)])
    first = engine.run_once()
    assert first.opened_count == 1

    signal_store.set_latest_signals([_signal(mean_signal=0.2, latest_close=97.0, latest_atr_pct=0.02)])
    second = engine.run_once()

    assert second.closed_count >= 1
    closed = portfolio_store.get_closed_trades()
    assert closed[-1].reason_closed == "stop_loss"


def test_paper_trade_engine_closes_trade_on_take_profit() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_min_signal_score=0.6,
        paper_atr_stop_multiplier=1.0,
        paper_risk_reward_ratio=1.5,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.85, latest_close=100.0, latest_atr_pct=0.02)])
    first = engine.run_once()
    assert first.opened_count == 1

    signal_store.set_latest_signals([_signal(mean_signal=0.2, latest_close=104.0, latest_atr_pct=0.02)])
    second = engine.run_once()

    assert second.closed_count >= 1
    closed = portfolio_store.get_closed_trades()
    assert closed[-1].reason_closed == "take_profit"


def test_paper_trade_engine_applies_fee_and_slippage() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_min_signal_score=0.6,
        paper_fee_bps=10,
        paper_slippage_bps=5,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.85, latest_close=100.0, latest_atr_pct=0.02)])

    result = engine.run_once()

    assert result.opened_count == 1
    open_trade = portfolio_store.get_open_trades()[0]
    assert open_trade.entry_fee_paid > 0
    assert open_trade.total_fees_paid > 0
    assert open_trade.entry_price > 100.0
    assert portfolio_store.get_portfolio().total_fees_paid > 0


def test_paper_trade_engine_closes_trade_on_time_stop() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_min_signal_score=0.6,
        paper_max_hold_minutes=120,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.85, latest_close=100.0)])
    first = engine.run_once()
    assert first.opened_count == 1

    portfolio = portfolio_store.get_portfolio()
    open_trades = portfolio_store.get_open_trades()
    open_trades[0].time_stop_at = datetime.now(tz=UTC) - timedelta(minutes=1)
    portfolio_store.replace_portfolio(
        portfolio=portfolio,
        open_trades=open_trades,
        closed_trades=portfolio_store.get_closed_trades(),
    )

    signal_store.set_latest_signals([_signal(mean_signal=0.2, latest_close=100.0)])
    second = engine.run_once()

    assert second.closed_count >= 1
    closed = portfolio_store.get_closed_trades()
    assert closed[-1].reason_closed == "time_stop"


def test_paper_trade_engine_uses_fixed_stop_and_take_profit_percentages() -> None:
    settings = Settings(
        _env_file=None,
        paper_bot_enabled=True,
        paper_min_signal_score=0.0,
        paper_slippage_bps=0,
        paper_fee_bps=0,
        paper_fixed_stop_loss_pct=0.01,
        paper_fixed_take_profit_pct=0.02,
    )
    engine, signal_store, portfolio_store = _build_engine(settings=settings)
    signal_store.set_latest_signals([_signal(mean_signal=0.85, latest_close=100.0, latest_atr_pct=0.05)])

    first = engine.run_once()

    assert first.opened_count == 1
    open_trade = portfolio_store.get_open_trades()[0]
    assert open_trade.stop_loss == 99.0
    assert open_trade.take_profit == 102.0

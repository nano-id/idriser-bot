"""Paper trading engine consuming dashboard signal state."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Sequence
from uuid import uuid4

from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.models.paper_event import PaperEvent
from app.models.paper_snapshot import PaperSnapshot
from app.models.hourly_signal import HourlySignal
from app.models.runtime_config import RuntimeConfig
from app.pipeline.paper_broker import PaperBroker
from app.pipeline.paper_journal_store import PaperJournalStore
from app.pipeline.paper_portfolio_store import PaperPortfolioStore
from app.pipeline.signal_state_store import SignalStateStore
from app.utils.runtime import utc_now


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PaperEngineStatus:
    """Latest paper engine runtime state for API exposure."""

    enabled: bool
    last_run_at: datetime | None
    last_error: str | None
    open_trade_count: int
    closed_trade_count: int
    cash_balance: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float


@dataclass(slots=True)
class PaperCycleResult:
    """Summary result returned by one paper bot cycle."""

    run_at: datetime
    opened_count: int
    closed_count: int
    status: PaperEngineStatus


class PaperTradeEngine:
    """Simulate paper positions from latest aggregate signal snapshots."""

    def __init__(
        self,
        *,
        settings: Settings,
        runtime_config_store: RuntimeConfigStore,
        signal_state_store: SignalStateStore,
        portfolio_store: PaperPortfolioStore,
        journal_store: PaperJournalStore | None = None,
        paper_broker: PaperBroker | None = None,
    ) -> None:
        self.settings = settings
        self.runtime_config_store = runtime_config_store
        self.signal_state_store = signal_state_store
        self.portfolio_store = portfolio_store
        self.journal_store = journal_store
        self.paper_broker = paper_broker or PaperBroker()

        self._lock = RLock()
        self._last_run_at: datetime | None = None
        self._last_error: str | None = None
        self._last_enabled = settings.paper_bot_enabled

    def run_once(self, *, now: datetime | None = None) -> PaperCycleResult:
        """Run one paper-trading cycle using current signal state."""
        return self._run_once(candle_map=None, now=now)

    def run_once_with_candles(
        self,
        *,
        candle_map: dict[str, dict[str, float]] | None = None,
        now: datetime | None = None,
    ) -> PaperCycleResult:
        """Run one paper cycle with explicit candle high/low/close data."""
        return self._run_once(candle_map=candle_map, now=now)

    def force_close_all(self, *, now: datetime | None = None, reason: str = "end_of_backtest") -> PaperEngineStatus:
        """Force-close all currently open trades using latest known prices."""
        with self._lock:
            run_at = now or utc_now()
            errors: list[str] = []
            runtime_config = self._load_runtime_config(errors=errors)
            effective_settings = self._build_effective_settings(runtime_config=runtime_config, errors=errors)

            portfolio = self.portfolio_store.get_portfolio()
            open_trades = self.portfolio_store.get_open_trades()
            closed_trades = self.portfolio_store.get_closed_trades()
            if not open_trades:
                return self._build_status(
                    enabled=effective_settings.paper_bot_enabled,
                    last_run_at=self._last_run_at,
                    last_error=self._last_error,
                )

            aggregate_signals = self.signal_state_store.get_latest_signals()
            prices_by_symbol = self._build_price_map(signals=aggregate_signals, open_trades=open_trades)
            open_trades, closed_trades, closed_count, newly_closed = self.paper_broker.force_close_all(
                settings=effective_settings,
                portfolio=portfolio,
                open_trades=open_trades,
                closed_trades=closed_trades,
                prices_by_symbol=prices_by_symbol,
                now=run_at,
                reason=reason,
            )
            self.paper_broker.refresh_portfolio(
                portfolio=portfolio,
                open_trades=open_trades,
                closed_trades=closed_trades,
                prices_by_symbol=prices_by_symbol,
            )
            self.portfolio_store.replace_portfolio(
                portfolio=portfolio,
                open_trades=open_trades,
                closed_trades=closed_trades,
            )
            self._record_journal(
                now=run_at,
                portfolio=portfolio,
                opened_trades=[],
                closed_trades=newly_closed,
                opened_count=0,
                closed_count=closed_count,
                errors=errors,
            )
            return self._build_status(
                enabled=effective_settings.paper_bot_enabled,
                last_run_at=self._last_run_at,
                last_error=self._last_error,
            )

    def advance_mark_to_market(
        self,
        *,
        candle_map: dict[str, dict[str, float]],
        now: datetime | None = None,
    ) -> PaperEngineStatus:
        """Advance open paper trades without evaluating new entry signals."""
        with self._lock:
            run_at = now or utc_now()
            errors: list[str] = []
            runtime_config = self._load_runtime_config(errors=errors)
            effective_settings = self._build_effective_settings(runtime_config=runtime_config, errors=errors)

            portfolio = self.portfolio_store.get_portfolio()
            open_trades = self.portfolio_store.get_open_trades()
            closed_trades = self.portfolio_store.get_closed_trades()

            prices_by_symbol = {
                symbol: float(payload["close"])
                for symbol, payload in candle_map.items()
                if isinstance(payload.get("close"), (int, float)) and float(payload["close"]) > 0
            }
            open_trades, closed_trades, closed_count, newly_closed = self.paper_broker.mark_to_market(
                settings=effective_settings,
                portfolio=portfolio,
                open_trades=open_trades,
                closed_trades=closed_trades,
                prices_by_symbol=prices_by_symbol,
                now=run_at,
                candle_map=candle_map,
            )
            self.paper_broker.refresh_portfolio(
                portfolio=portfolio,
                open_trades=open_trades,
                closed_trades=closed_trades,
                prices_by_symbol=prices_by_symbol,
            )
            self.portfolio_store.replace_portfolio(
                portfolio=portfolio,
                open_trades=open_trades,
                closed_trades=closed_trades,
            )
            if self.journal_store is not None:
                if newly_closed:
                    self._record_journal(
                        now=run_at,
                        portfolio=portfolio,
                        opened_trades=[],
                        closed_trades=newly_closed,
                        opened_count=0,
                        closed_count=closed_count,
                        errors=errors,
                    )
                else:
                    self.journal_store.add_snapshot(self._build_snapshot(now=run_at, portfolio=portfolio))
            return self._build_status(
                enabled=effective_settings.paper_bot_enabled,
                last_run_at=self._last_run_at,
                last_error=self._last_error,
            )

    def _run_once(
        self,
        *,
        candle_map: dict[str, dict[str, float]] | None,
        now: datetime | None,
    ) -> PaperCycleResult:
        """Internal paper-trading cycle runner."""
        with self._lock:
            run_at = now or utc_now()
            errors: list[str] = []
            try:
                runtime_config = self._load_runtime_config(errors=errors)
                effective_settings = self._build_effective_settings(runtime_config=runtime_config, errors=errors)

                portfolio = self.portfolio_store.get_portfolio()
                open_trades = self.portfolio_store.get_open_trades()
                closed_trades = self.portfolio_store.get_closed_trades()

                aggregate_signals = self.signal_state_store.get_latest_signals()
                ai_signals = self.signal_state_store.get_latest_ai_signals()
                ai_scores_by_symbol = {
                    item.symbol: item.support_score
                    for item in ai_signals
                    if isinstance(item.support_score, (int, float))
                }

                prices_by_symbol = self._build_price_map(signals=aggregate_signals, open_trades=open_trades)
                open_trades, closed_trades, closed_count, newly_closed = self.paper_broker.mark_to_market(
                    settings=effective_settings,
                    portfolio=portfolio,
                    open_trades=open_trades,
                    closed_trades=closed_trades,
                    prices_by_symbol=prices_by_symbol,
                    now=run_at,
                    candle_map=candle_map,
                )

                opened_count = 0
                opened_trades = []
                if effective_settings.paper_bot_enabled:
                    candidates = self._select_candidates(
                        signals=aggregate_signals,
                        settings=effective_settings,
                    )
                    open_symbols = {item.symbol for item in open_trades}
                    slots = max(0, effective_settings.paper_max_open_positions - len(open_trades))
                    for signal in candidates:
                        if slots <= 0:
                            break
                        if signal.symbol in open_symbols:
                            continue

                        trade = self.paper_broker.open_long(
                            portfolio=portfolio,
                            signal=signal,
                            settings=effective_settings,
                            now=run_at,
                            ai_support_score=ai_scores_by_symbol.get(signal.symbol),
                        )
                        if trade is None:
                            continue

                        open_trades.append(trade)
                        opened_trades.append(trade)
                        open_symbols.add(trade.symbol)
                        opened_count += 1
                        slots -= 1

                self.paper_broker.refresh_portfolio(
                    portfolio=portfolio,
                    open_trades=open_trades,
                    closed_trades=closed_trades,
                    prices_by_symbol=prices_by_symbol,
                )

                self.portfolio_store.replace_portfolio(
                    portfolio=portfolio,
                    open_trades=open_trades,
                    closed_trades=closed_trades,
                )

                self._last_run_at = run_at
                self._last_enabled = effective_settings.paper_bot_enabled
                self._last_error = errors[-1] if errors else None
                self._record_journal(
                    now=run_at,
                    portfolio=portfolio,
                    opened_trades=opened_trades,
                    closed_trades=newly_closed,
                    opened_count=opened_count,
                    closed_count=closed_count,
                    errors=errors,
                )
                status_payload = self._build_status(
                    enabled=effective_settings.paper_bot_enabled,
                    last_run_at=self._last_run_at,
                    last_error=self._last_error,
                )
                return PaperCycleResult(
                    run_at=run_at,
                    opened_count=opened_count,
                    closed_count=closed_count,
                    status=status_payload,
                )
            except Exception as exc:  # noqa: BLE001
                self._last_run_at = run_at
                self._last_error = str(exc)
                LOGGER.warning("Paper cycle failed: %s", exc)
                raise

    def status(self) -> PaperEngineStatus:
        """Return current paper engine status snapshot."""
        with self._lock:
            return self._build_status(
                enabled=self._last_enabled,
                last_run_at=self._last_run_at,
                last_error=self._last_error,
            )

    def reset(self) -> PaperEngineStatus:
        """Reset paper portfolio and trade state to configured defaults."""
        with self._lock:
            errors: list[str] = []
            runtime_config = self._load_runtime_config(errors=errors)
            effective_settings = self._build_effective_settings(runtime_config=runtime_config, errors=errors)
            self.portfolio_store.reset(initial_capital=effective_settings.paper_initial_capital)
            if self.journal_store is not None:
                self.journal_store.reset()
                portfolio = self.portfolio_store.get_portfolio()
                self.journal_store.add_snapshot(self._build_snapshot(now=utc_now(), portfolio=portfolio))
                self.journal_store.add_event(
                    PaperEvent(
                        event_id=f"pev-{uuid4().hex[:12]}",
                        timestamp=utc_now(),
                        event_type="RESET",
                        summary="Paper portfolio reset to initial capital",
                        payload={"initial_capital": effective_settings.paper_initial_capital},
                    )
                )
            self._last_enabled = effective_settings.paper_bot_enabled
            self._last_error = errors[-1] if errors else None
            return self._build_status(
                enabled=self._last_enabled,
                last_run_at=self._last_run_at,
                last_error=self._last_error,
            )

    def _build_status(
        self,
        *,
        enabled: bool,
        last_run_at: datetime | None,
        last_error: str | None,
    ) -> PaperEngineStatus:
        portfolio = self.portfolio_store.get_portfolio()
        open_trades = self.portfolio_store.get_open_trades()
        closed_trades = self.portfolio_store.get_closed_trades()
        return PaperEngineStatus(
            enabled=enabled,
            last_run_at=last_run_at,
            last_error=last_error,
            open_trade_count=len(open_trades),
            closed_trade_count=len(closed_trades),
            cash_balance=portfolio.cash_balance,
            equity=portfolio.equity,
            realized_pnl=portfolio.realized_pnl,
            unrealized_pnl=portfolio.unrealized_pnl,
        )

    def _select_candidates(self, *, signals: Sequence[HourlySignal], settings: Settings) -> list[HourlySignal]:
        candidates: list[HourlySignal] = []
        for signal in signals:
            if signal.mean_signal < settings.paper_min_signal_score:
                continue
            if settings.paper_require_final_selected and signal.final_selected is not True:
                continue
            if settings.paper_require_step2_pass and signal.step2_pass is not True:
                continue
            if settings.paper_require_step3_pass and signal.step3_pass is not True:
                continue
            if settings.paper_require_window_complete and not bool(signal.aggregate_flags.get("window_complete", False)):
                continue
            if self.paper_broker.extract_signal_price(signal=signal) is None:
                continue
            candidates.append(signal)

        candidates.sort(
            key=lambda item: (
                item.mean_signal,
                item.stability_score,
                item.bullish_ratio,
            ),
            reverse=True,
        )
        return candidates

    def _build_price_map(self, *, signals: Sequence[HourlySignal], open_trades) -> dict[str, float]:
        prices: dict[str, float] = {}
        for signal in signals:
            price = self.paper_broker.extract_signal_price(signal=signal)
            if price is not None and price > 0:
                prices[signal.symbol] = price

        for trade in open_trades:
            if trade.symbol not in prices and trade.current_price is not None and trade.current_price > 0:
                prices[trade.symbol] = trade.current_price
        return prices

    def _load_runtime_config(self, *, errors: list[str]) -> RuntimeConfig:
        try:
            return self.runtime_config_store.load()
        except ValueError as exc:
            LOGGER.warning("Runtime config load failed for paper engine, using defaults: %s", exc)
            errors.append(f"runtime_config_load_failed:{exc}")
            return RuntimeConfig.from_settings(self.settings)

    def _build_effective_settings(self, *, runtime_config: RuntimeConfig, errors: list[str]) -> Settings:
        payload = self.settings.model_dump()
        payload.update(runtime_config.to_settings_overrides())
        try:
            return Settings(_env_file=None, **payload)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Runtime config merge failed for paper engine, using base settings: %s", exc)
            errors.append(f"runtime_config_merge_failed:{exc}")
            return Settings(_env_file=None, **self.settings.model_dump())

    def _record_journal(
        self,
        *,
        now: datetime,
        portfolio,
        opened_trades,
        closed_trades,
        opened_count: int,
        closed_count: int,
        errors: list[str],
    ) -> None:
        if self.journal_store is None:
            return

        self.journal_store.add_snapshot(self._build_snapshot(now=now, portfolio=portfolio))

        events: list[PaperEvent] = []
        for trade in opened_trades:
            events.append(
                PaperEvent(
                    event_id=f"pev-{uuid4().hex[:12]}",
                    timestamp=now,
                    event_type="OPEN",
                    summary=f"Opened {trade.symbol} LONG paper trade",
                    symbol=trade.symbol,
                    trade_id=trade.trade_id,
                    payload={
                        "entry_price": trade.entry_price,
                        "quantity": trade.quantity,
                        "decision_horizon": trade.decision_horizon,
                    },
                )
            )
        for trade in closed_trades:
            events.append(
                PaperEvent(
                    event_id=f"pev-{uuid4().hex[:12]}",
                    timestamp=now,
                    event_type="CLOSE",
                    summary=f"Closed {trade.symbol} paper trade via {trade.reason_closed}",
                    symbol=trade.symbol,
                    trade_id=trade.trade_id,
                    pnl_value=trade.pnl_value,
                    payload={
                        "exit_price": trade.exit_price,
                        "pnl_pct": trade.pnl_pct,
                        "reason_closed": trade.reason_closed,
                    },
                )
            )
        events.append(
            PaperEvent(
                event_id=f"pev-{uuid4().hex[:12]}",
                timestamp=now,
                event_type="RUN",
                summary="Paper cycle completed",
                payload={
                    "opened_count": opened_count,
                    "closed_count": closed_count,
                    "warnings": list(errors),
                    "equity": portfolio.equity,
                },
            )
        )
        for error in errors:
            events.append(
                PaperEvent(
                    event_id=f"pev-{uuid4().hex[:12]}",
                    timestamp=now,
                    event_type="ERROR",
                    summary=f"Paper warning: {error}",
                    payload={"error": error},
                )
            )
        self.journal_store.add_events(events)

    def _build_snapshot(self, *, now: datetime, portfolio) -> PaperSnapshot:
        return PaperSnapshot(
            timestamp=now,
            equity=portfolio.equity,
            cash_balance=portfolio.cash_balance,
            open_positions=portfolio.open_positions,
            closed_positions=portfolio.closed_positions,
            realized_pnl=portfolio.realized_pnl,
            unrealized_pnl=portfolio.unrealized_pnl,
        )

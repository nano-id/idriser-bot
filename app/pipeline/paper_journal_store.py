"""Thread-safe in-memory journal for paper simulation events and equity snapshots."""

from __future__ import annotations

from collections import deque
from threading import RLock
from typing import Iterable

from app.models.paper_event import PaperEvent
from app.models.paper_metrics import PaperMetrics
from app.models.paper_portfolio import PaperPortfolio
from app.models.paper_snapshot import PaperSnapshot
from app.models.paper_trade import PaperTrade


class PaperJournalStore:
    """Hold recent paper simulation events and portfolio snapshots."""

    def __init__(self, *, max_events: int = 500, max_snapshots: int = 5000) -> None:
        self._lock = RLock()
        self._events: deque[PaperEvent] = deque(maxlen=max_events)
        self._snapshots: deque[PaperSnapshot] = deque(maxlen=max_snapshots)

    def add_event(self, event: PaperEvent) -> None:
        with self._lock:
            self._events.append(PaperEvent.model_validate(event.model_dump()))

    def add_events(self, events: Iterable[PaperEvent]) -> None:
        with self._lock:
            for event in events:
                self._events.append(PaperEvent.model_validate(event.model_dump()))

    def get_events(self, *, limit: int | None = None) -> list[PaperEvent]:
        with self._lock:
            items = list(self._events)
        if limit is not None and limit >= 0:
            items = items[-limit:]
        return [PaperEvent.model_validate(item.model_dump()) for item in reversed(items)]

    def add_snapshot(self, snapshot: PaperSnapshot) -> None:
        with self._lock:
            self._snapshots.append(PaperSnapshot.model_validate(snapshot.model_dump()))

    def get_snapshots(self, *, limit: int | None = None) -> list[PaperSnapshot]:
        with self._lock:
            items = list(self._snapshots)
        if limit is not None and limit >= 0:
            items = items[-limit:]
        return [PaperSnapshot.model_validate(item.model_dump()) for item in items]

    def reset(self) -> None:
        with self._lock:
            self._events.clear()
            self._snapshots.clear()

    def build_metrics(
        self,
        *,
        portfolio: PaperPortfolio,
        closed_trades: list[PaperTrade],
    ) -> PaperMetrics:
        closed = [trade for trade in closed_trades if trade.status == "CLOSED"]
        wins = [trade for trade in closed if trade.pnl_value > 0]
        losses = [trade for trade in closed if trade.pnl_value < 0]

        total_closed = len(closed)
        total_profit = sum(trade.pnl_value for trade in wins)
        total_loss_abs = abs(sum(trade.pnl_value for trade in losses))
        avg_win = total_profit / len(wins) if wins else 0.0
        avg_loss = sum(trade.pnl_value for trade in losses) / len(losses) if losses else 0.0
        expectancy = sum(trade.pnl_value for trade in closed) / total_closed if total_closed else 0.0
        profit_factor = (total_profit / total_loss_abs) if total_loss_abs > 0 else None
        best_trade_pct = max((trade.pnl_pct for trade in closed), default=0.0)
        worst_trade_pct = min((trade.pnl_pct for trade in closed), default=0.0)
        hold_minutes: list[float] = []
        for trade in closed:
            if trade.opened_at and trade.closed_at:
                hold_minutes.append((trade.closed_at - trade.opened_at).total_seconds() / 60.0)

        max_drawdown = 0.0
        peak = None
        snapshots = self.get_snapshots()
        for snapshot in snapshots:
            peak = snapshot.equity if peak is None else max(peak, snapshot.equity)
            if peak and peak > 0:
                drawdown = ((peak - snapshot.equity) / peak) * 100.0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        starting_equity = snapshots[0].equity if snapshots else portfolio.equity

        return PaperMetrics(
            total_closed_trades=total_closed,
            win_count=len(wins),
            loss_count=len(losses),
            win_rate_pct=((len(wins) / total_closed) * 100.0) if total_closed else 0.0,
            avg_win_value=round(avg_win, 8),
            avg_loss_value=round(avg_loss, 8),
            expectancy_value=round(expectancy, 8),
            profit_factor=round(profit_factor, 8) if profit_factor is not None else None,
            best_trade_pct=round(best_trade_pct, 6),
            worst_trade_pct=round(worst_trade_pct, 6),
            max_drawdown_pct=round(max_drawdown, 6),
            total_fees_paid=round(portfolio.total_fees_paid, 8),
            net_profit_value=round(portfolio.realized_pnl + portfolio.unrealized_pnl, 8),
            total_return_pct=round((((portfolio.equity / starting_equity) - 1.0) * 100.0), 6) if starting_equity > 0 else 0.0,
            avg_hold_minutes=round((sum(hold_minutes) / len(hold_minutes)), 4) if hold_minutes else 0.0,
            current_equity=portfolio.equity,
            current_cash_balance=portfolio.cash_balance,
            open_positions=portfolio.open_positions,
        )

"""In-memory store for paper portfolio and trades."""

from __future__ import annotations

from threading import RLock
from typing import Sequence

from app.models.paper_portfolio import PaperPortfolio
from app.models.paper_trade import PaperTrade


class PaperPortfolioStore:
    """Thread-safe in-memory holder used by paper bot API and engine."""

    def __init__(self, *, initial_capital: float) -> None:
        self._lock = RLock()
        self._initial_capital = float(initial_capital)
        self._portfolio = PaperPortfolio(
            cash_balance=self._initial_capital,
            equity=self._initial_capital,
            open_positions=0,
            closed_positions=0,
            win_count=0,
            loss_count=0,
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            total_fees_paid=0.0,
        )
        self._open_trades: list[PaperTrade] = []
        self._closed_trades: list[PaperTrade] = []

    def get_portfolio(self) -> PaperPortfolio:
        """Return defensive copy of portfolio state."""
        with self._lock:
            return PaperPortfolio.model_validate(self._portfolio.model_dump())

    def get_open_trades(self) -> list[PaperTrade]:
        """Return defensive copy of open trades."""
        with self._lock:
            return [PaperTrade.model_validate(item.model_dump()) for item in self._open_trades]

    def get_closed_trades(self) -> list[PaperTrade]:
        """Return defensive copy of closed trades."""
        with self._lock:
            return [PaperTrade.model_validate(item.model_dump()) for item in self._closed_trades]

    def replace_portfolio(
        self,
        *,
        portfolio: PaperPortfolio,
        open_trades: Sequence[PaperTrade] | None = None,
        closed_trades: Sequence[PaperTrade] | None = None,
    ) -> None:
        """Replace stored portfolio and optionally open/closed trade lists."""
        with self._lock:
            self._portfolio = PaperPortfolio.model_validate(portfolio.model_dump())
            if open_trades is not None:
                self._open_trades = [PaperTrade.model_validate(item.model_dump()) for item in open_trades]
            if closed_trades is not None:
                self._closed_trades = [PaperTrade.model_validate(item.model_dump()) for item in closed_trades]

    def reset(self, *, initial_capital: float | None = None) -> PaperPortfolio:
        """Reset all paper state to pristine balances and empty trades."""
        with self._lock:
            if initial_capital is not None:
                self._initial_capital = float(initial_capital)
            self._portfolio = PaperPortfolio(
                cash_balance=self._initial_capital,
                equity=self._initial_capital,
                open_positions=0,
                closed_positions=0,
                win_count=0,
                loss_count=0,
                realized_pnl=0.0,
                unrealized_pnl=0.0,
                total_fees_paid=0.0,
            )
            self._open_trades.clear()
            self._closed_trades.clear()
            return PaperPortfolio.model_validate(self._portfolio.model_dump())

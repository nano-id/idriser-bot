"""Execution simulator for paper long-only trades."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from app.config.settings import Settings
from app.models.hourly_signal import HourlySignal
from app.models.paper_portfolio import PaperPortfolio
from app.models.paper_trade import PaperTrade


class PaperBroker:
    """Simulated broker that opens/closes and marks paper positions."""

    def __init__(self, *, min_stop_pct: float = 0.003) -> None:
        self.min_stop_pct = min_stop_pct

    def extract_signal_price(self, *, signal: HourlySignal) -> float | None:
        """Extract latest price from aggregate signal payload."""
        value = signal.feature_snapshot.get("latest_close")
        if isinstance(value, (int, float)) and float(value) > 0:
            return float(value)
        return None

    def open_long(
        self,
        *,
        portfolio: PaperPortfolio,
        signal: HourlySignal,
        settings: Settings,
        now: datetime,
        ai_support_score: float | None,
    ) -> PaperTrade | None:
        """Open one LONG paper trade when sufficient data and cash exist."""
        market_price = self.extract_signal_price(signal=signal)
        if market_price is None or portfolio.cash_balance <= 0:
            return None

        entry_price = market_price * (1 + (settings.paper_slippage_bps / 10_000))

        risk_budget = portfolio.cash_balance * settings.paper_risk_per_trade_pct
        if risk_budget <= 0:
            return None

        fixed_stop_pct = settings.paper_fixed_stop_loss_pct
        if fixed_stop_pct is not None:
            stop_distance_pct = float(fixed_stop_pct)
        else:
            atr_pct_raw = signal.feature_snapshot.get("latest_atr_pct")
            atr_pct = float(atr_pct_raw) if isinstance(atr_pct_raw, (int, float)) and float(atr_pct_raw) > 0 else 0.01
            stop_distance_pct = max(atr_pct * settings.paper_atr_stop_multiplier, self.min_stop_pct)
        stop_loss = entry_price * (1 - stop_distance_pct)
        stop_distance_value = entry_price - stop_loss
        if stop_distance_value <= 0:
            return None

        qty_by_risk = risk_budget / stop_distance_value
        qty_by_cash = portfolio.cash_balance / entry_price
        quantity = min(qty_by_risk, qty_by_cash)
        if quantity <= 0:
            return None

        notional = quantity * entry_price
        if notional <= 0:
            return None

        entry_fee_paid = notional * (settings.paper_fee_bps / 10_000)
        total_cash_required = notional + entry_fee_paid
        if total_cash_required > portfolio.cash_balance:
            quantity = portfolio.cash_balance / (entry_price * (1 + (settings.paper_fee_bps / 10_000)))
            if quantity <= 0:
                return None
            notional = quantity * entry_price
            entry_fee_paid = notional * (settings.paper_fee_bps / 10_000)
            total_cash_required = notional + entry_fee_paid
            if total_cash_required > portfolio.cash_balance:
                return None

        fixed_take_profit_pct = settings.paper_fixed_take_profit_pct
        if fixed_take_profit_pct is not None:
            take_profit = entry_price * (1 + float(fixed_take_profit_pct))
        else:
            take_profit = entry_price + (stop_distance_value * settings.paper_risk_reward_ratio)
        time_stop_at = None
        if settings.paper_max_hold_minutes is not None:
            time_stop_at = now + timedelta(minutes=settings.paper_max_hold_minutes)

        portfolio.cash_balance = round(max(0.0, portfolio.cash_balance - total_cash_required), 8)
        portfolio.total_fees_paid = round(portfolio.total_fees_paid + entry_fee_paid, 8)

        return PaperTrade(
            trade_id=f"pt-{uuid4().hex[:12]}",
            symbol=signal.symbol,
            decision_horizon=signal.decision_horizon,
            status="OPEN",
            side="LONG",
            entry_price=round(entry_price, 8),
            current_price=round(entry_price, 8),
            exit_price=None,
            quantity=round(quantity, 8),
            notional=round(notional, 8),
            opened_at=now,
            closed_at=None,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            time_stop_at=time_stop_at,
            pnl_pct=0.0,
            pnl_value=0.0,
            reason_opened=f"mean_signal={signal.mean_signal:.4f}",
            reason_closed=None,
            entry_fee_paid=round(entry_fee_paid, 8),
            exit_fee_paid=0.0,
            total_fees_paid=round(entry_fee_paid, 8),
            step2_score=signal.step2_score,
            step3_pass=signal.step3_pass,
            ai_support_score=ai_support_score,
        )

    def mark_to_market(
        self,
        *,
        settings: Settings,
        portfolio: PaperPortfolio,
        open_trades: list[PaperTrade],
        closed_trades: list[PaperTrade],
        prices_by_symbol: dict[str, float],
        now: datetime,
        candle_map: dict[str, dict[str, float]] | None = None,
    ) -> tuple[list[PaperTrade], list[PaperTrade], int, list[PaperTrade]]:
        """Update open trades and close those hitting exit rules."""
        updated_open: list[PaperTrade] = []
        updated_closed = [PaperTrade.model_validate(item.model_dump()) for item in closed_trades]
        newly_closed: list[PaperTrade] = []
        closed_now = 0

        for trade in open_trades:
            current_price = prices_by_symbol.get(trade.symbol, trade.current_price or trade.entry_price)
            if current_price <= 0:
                updated_open.append(PaperTrade.model_validate(trade.model_dump()))
                continue

            working = PaperTrade.model_validate(trade.model_dump())
            working.current_price = round(current_price, 8)
            working.pnl_value = round((current_price - working.entry_price) * working.quantity - working.total_fees_paid, 8)
            working.pnl_pct = round(((current_price / working.entry_price) - 1.0) * 100.0, 6)

            close_reason: str | None = None
            forced_exit_price: float | None = None
            candle = (candle_map or {}).get(trade.symbol, {})
            candle_low = self._as_positive_float(candle.get("low"))
            candle_high = self._as_positive_float(candle.get("high"))
            candle_close = self._as_positive_float(candle.get("close")) or current_price

            if working.stop_loss is not None and (
                (candle_low is not None and candle_low <= working.stop_loss) or current_price <= working.stop_loss
            ):
                close_reason = "stop_loss"
                forced_exit_price = working.stop_loss
            elif working.take_profit is not None and (
                (candle_high is not None and candle_high >= working.take_profit) or current_price >= working.take_profit
            ):
                close_reason = "take_profit"
                forced_exit_price = working.take_profit
            elif working.time_stop_at is not None and now >= working.time_stop_at:
                close_reason = "time_stop"
                forced_exit_price = candle_close

            if close_reason is None:
                updated_open.append(working)
                continue

            self._close_trade(
                trade=working,
                settings=settings,
                portfolio=portfolio,
                now=now,
                close_reason=close_reason,
                market_price=forced_exit_price or current_price,
            )
            updated_closed.append(working)
            newly_closed.append(PaperTrade.model_validate(working.model_dump()))
            closed_now += 1

        return updated_open, updated_closed, closed_now, newly_closed

    def force_close_all(
        self,
        *,
        settings: Settings,
        portfolio: PaperPortfolio,
        open_trades: list[PaperTrade],
        closed_trades: list[PaperTrade],
        prices_by_symbol: dict[str, float],
        now: datetime,
        reason: str = "end_of_backtest",
    ) -> tuple[list[PaperTrade], list[PaperTrade], int, list[PaperTrade]]:
        """Force-close all remaining open trades at the supplied prices."""
        updated_closed = [PaperTrade.model_validate(item.model_dump()) for item in closed_trades]
        newly_closed: list[PaperTrade] = []
        closed_now = 0

        for trade in open_trades:
            working = PaperTrade.model_validate(trade.model_dump())
            market_price = prices_by_symbol.get(trade.symbol, trade.current_price or trade.entry_price)
            if market_price <= 0:
                market_price = working.entry_price
            self._close_trade(
                trade=working,
                settings=settings,
                portfolio=portfolio,
                now=now,
                close_reason=reason,
                market_price=market_price,
            )
            updated_closed.append(working)
            newly_closed.append(PaperTrade.model_validate(working.model_dump()))
            closed_now += 1

        return [], updated_closed, closed_now, newly_closed

    def refresh_portfolio(
        self,
        *,
        portfolio: PaperPortfolio,
        open_trades: list[PaperTrade],
        closed_trades: list[PaperTrade],
        prices_by_symbol: dict[str, float],
    ) -> None:
        """Recompute portfolio-level totals from trade state."""
        unrealized = 0.0
        open_exposure = 0.0
        for trade in open_trades:
            mark_price = prices_by_symbol.get(trade.symbol, trade.current_price or trade.entry_price)
            unrealized += ((mark_price - trade.entry_price) * trade.quantity) - trade.total_fees_paid
            open_exposure += mark_price * trade.quantity

        realized = sum(item.pnl_value for item in closed_trades if item.status == "CLOSED")
        wins = sum(1 for item in closed_trades if item.status == "CLOSED" and item.pnl_value > 0)
        losses = sum(1 for item in closed_trades if item.status == "CLOSED" and item.pnl_value < 0)

        portfolio.unrealized_pnl = round(unrealized, 8)
        portfolio.realized_pnl = round(realized, 8)
        portfolio.open_positions = len(open_trades)
        portfolio.closed_positions = len(closed_trades)
        portfolio.win_count = wins
        portfolio.loss_count = losses
        portfolio.equity = round(portfolio.cash_balance + open_exposure, 8)

    def _close_trade(
        self,
        *,
        trade: PaperTrade,
        settings: Settings,
        portfolio: PaperPortfolio,
        now: datetime,
        close_reason: str,
        market_price: float,
    ) -> None:
        trade.status = "CLOSED"
        trade.closed_at = now
        exit_price = market_price * (1 - (settings.paper_slippage_bps / 10_000))
        exit_notional = trade.quantity * exit_price
        exit_fee_paid = exit_notional * (settings.paper_fee_bps / 10_000)
        net_exit_value = exit_notional - exit_fee_paid
        trade.exit_price = round(exit_price, 8)
        trade.reason_closed = close_reason
        trade.exit_fee_paid = round(exit_fee_paid, 8)
        trade.total_fees_paid = round(trade.entry_fee_paid + trade.exit_fee_paid, 8)
        trade.pnl_value = round(net_exit_value - trade.notional - trade.entry_fee_paid, 8)
        trade.pnl_pct = round((trade.pnl_value / trade.notional) * 100.0, 6) if trade.notional > 0 else 0.0

        portfolio.cash_balance = round(portfolio.cash_balance + net_exit_value, 8)
        portfolio.total_fees_paid = round(portfolio.total_fees_paid + exit_fee_paid, 8)

    @staticmethod
    def _as_positive_float(value: object) -> float | None:
        if isinstance(value, (int, float)) and float(value) > 0:
            return float(value)
        return None

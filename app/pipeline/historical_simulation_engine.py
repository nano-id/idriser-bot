"""Historical replay simulation engine for symbol/date-range backtests."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Sequence

from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.clients.replay_market_data_client import ReplayMarketDataClient
from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.filters.market_regime_filter import CCXTMarketRegimeFilter
from app.filters.technical_filter import CCXTTechnicalFilter
from app.models.historical_simulation import HistoricalSignalEvaluation, HistoricalSimulationResult
from app.models.hourly_signal import HourlySignal
from app.models.runtime_config import RuntimeConfig
from app.models.step2 import Step2Result
from app.models.step3 import Step3Result
from app.pipeline.hourly_signal_aggregator import HourlySignalAggregator
from app.pipeline.market_snapshot_collector import MarketSnapshotCollector
from app.pipeline.paper_journal_store import PaperJournalStore
from app.pipeline.paper_portfolio_store import PaperPortfolioStore
from app.pipeline.paper_trade_engine import PaperTradeEngine
from app.pipeline.signal_state_store import SignalStateStore
from app.utils.timeframe import required_snapshots_for_horizon, timeframe_to_minutes


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class HistoricalSimulationRequest:
    """Internal request model for one historical replay run."""

    symbol: str
    start_at: datetime
    end_at: datetime
    close_open_positions_at_end: bool = True


class _StaticRuntimeConfigStore:
    """Minimal runtime store wrapper for one frozen effective config."""

    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self.runtime_config = runtime_config

    def load(self) -> RuntimeConfig:
        return self.runtime_config


class HistoricalSimulationEngine:
    """Replay one symbol from past to future using the active strategy settings."""

    def __init__(
        self,
        *,
        settings: Settings,
        runtime_config_store: RuntimeConfigStore,
        market_data_client: CCXTMarketDataClient | None = None,
    ) -> None:
        self.settings = settings
        self.runtime_config_store = runtime_config_store
        self.market_data_client = market_data_client or CCXTMarketDataClient(
            exchange_id=settings.exchange_id,
            timeout_seconds=settings.request_timeout_seconds,
            max_retries=settings.request_max_retries,
            backoff_seconds=settings.request_backoff_seconds,
        )

    def run(self, *, symbol: str, start_at: datetime, end_at: datetime, close_open_positions_at_end: bool = True) -> HistoricalSimulationResult:
        """Run a historical replay simulation using current runtime parameters."""
        warnings: list[str] = []
        request = HistoricalSimulationRequest(
            symbol=symbol.strip().upper(),
            start_at=self._to_utc(start_at),
            end_at=self._to_utc(end_at),
            close_open_positions_at_end=close_open_positions_at_end,
        )
        if request.end_at <= request.start_at:
            msg = "Bitis tarihi baslangic tarihinden sonra olmalidir."
            raise ValueError(msg)

        runtime_config = self._load_runtime_config(warnings=warnings)
        effective_settings = self._build_effective_settings(runtime_config=runtime_config, warnings=warnings)

        required_snapshots = required_snapshots_for_horizon(
            decision_horizon=effective_settings.decision_horizon,
            snapshot_interval_minutes=effective_settings.snapshot_interval_minutes,
        )
        breadth_symbols = self._build_breadth_symbols(symbol=request.symbol, settings=effective_settings)
        rows_by_key = self._preload_rows(
            request=request,
            settings=effective_settings,
            required_snapshots=required_snapshots,
            breadth_symbols=breadth_symbols,
            warnings=warnings,
        )

        replay_client = ReplayMarketDataClient(rows_by_key=rows_by_key)
        collector = MarketSnapshotCollector(settings=effective_settings, market_data_client=replay_client)
        aggregator = HourlySignalAggregator(settings=effective_settings)
        technical_filter = CCXTTechnicalFilter(settings=effective_settings, market_data_client=replay_client)
        regime_filter = CCXTMarketRegimeFilter(settings=effective_settings, market_data_client=replay_client)

        signal_state_store = SignalStateStore()
        portfolio_store = PaperPortfolioStore(initial_capital=effective_settings.paper_initial_capital)
        journal_store = PaperJournalStore(max_events=20_000, max_snapshots=50_000)
        paper_engine = PaperTradeEngine(
            settings=effective_settings,
            runtime_config_store=_StaticRuntimeConfigStore(RuntimeConfig.from_settings(effective_settings)),  # type: ignore[arg-type]
            signal_state_store=signal_state_store,
            portfolio_store=portfolio_store,
            journal_store=journal_store,
        )

        base_rows = rows_by_key.get((request.symbol, effective_settings.snapshot_timeframe), [])
        replay_rows = [row for row in base_rows if self._row_in_range(row=row, start_at=request.start_at, end_at=request.end_at)]
        if not replay_rows:
            msg = f"Secilen tarih araliginda veri bulunamadi: {request.symbol}"
            raise ValueError(msg)

        evaluations: list[HistoricalSignalEvaluation] = []
        selected_signal_count = 0
        opened_trade_count = 0
        closed_trade_count = 0
        decision_interval_minutes = timeframe_to_minutes(effective_settings.decision_horizon)
        next_decision_at = request.start_at

        for row in replay_rows:
            candle_time = self._row_timestamp(row)
            replay_client.set_current_time(candle_time)
            candle_map = {
                request.symbol: {
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                }
            }

            if candle_time >= next_decision_at:
                signal = self._build_signal(
                    symbol=request.symbol,
                    settings=effective_settings,
                    required_snapshots=required_snapshots,
                    breadth_symbols=breadth_symbols,
                    collector=collector,
                    aggregator=aggregator,
                    technical_filter=technical_filter,
                    regime_filter=regime_filter,
                )
                signal_state_store.set_latest_signals([signal])
                cycle = paper_engine.run_once_with_candles(candle_map=candle_map, now=candle_time)
                selected_signal_count += 1 if signal.final_selected is True else 0
                opened_trade_count += cycle.opened_count
                closed_trade_count += cycle.closed_count
                evaluations.append(
                    HistoricalSignalEvaluation(
                        timestamp=candle_time,
                        symbol=signal.symbol,
                        decision_horizon=signal.decision_horizon,
                        price=self._signal_price(signal),
                        mean_signal=signal.mean_signal,
                        bullish_ratio=signal.bullish_ratio,
                        stability_score=signal.stability_score,
                        latest_breakout=signal.latest_breakout,
                        window_complete=bool(signal.aggregate_flags.get("window_complete", False)),
                        fallback_used=signal.fallback_used,
                        step2_score=signal.step2_score,
                        step2_pass=signal.step2_pass,
                        regime_status=signal.regime_status,
                        step3_pass=signal.step3_pass,
                        final_selected=signal.final_selected,
                        reject_stage=signal.reject_stage,
                        reject_reason_summary=signal.reject_reason_summary,
                        opened_trades=cycle.opened_count,
                        closed_trades=cycle.closed_count,
                    )
                )
                next_decision_at = candle_time + timedelta(minutes=decision_interval_minutes)
            else:
                paper_engine.advance_mark_to_market(candle_map=candle_map, now=candle_time)

        force_closed_at_end = False
        if request.close_open_positions_at_end and portfolio_store.get_open_trades():
            last_close = float(replay_rows[-1][4])
            signal_state_store.set_latest_signals(
                [
                    HourlySignal(
                        symbol=request.symbol,
                        decision_horizon=effective_settings.decision_horizon,
                        base_snapshot_timeframe=effective_settings.snapshot_timeframe,
                        required_snapshots=required_snapshots,
                        window_size=required_snapshots,
                        snapshot_count=required_snapshots,
                        window_start=request.end_at,
                        window_end=request.end_at,
                        expected_duration_minutes=required_snapshots * effective_settings.snapshot_interval_minutes,
                        actual_duration_minutes=required_snapshots * effective_settings.snapshot_interval_minutes,
                        mean_signal=0.0,
                        median_signal=0.0,
                        signal_stddev=0.0,
                        bullish_ratio=0.0,
                        last_3_slope=0.0,
                        stability_score=0.0,
                        fallback_used=False,
                        latest_breakout=False,
                        aggregate_flags={"window_complete": True},
                        feature_snapshot={"latest_close": last_close},
                    )
                ]
            )
            status = paper_engine.force_close_all(now=request.end_at, reason="end_of_backtest")
            closed_trade_count = status.closed_trade_count
            force_closed_at_end = True

        portfolio = portfolio_store.get_portfolio()
        closed_trades = portfolio_store.get_closed_trades()
        metrics = journal_store.build_metrics(portfolio=portfolio, closed_trades=closed_trades)

        return HistoricalSimulationResult(
            symbol=request.symbol,
            start_at=request.start_at,
            end_at=request.end_at,
            decision_horizon=effective_settings.decision_horizon,
            snapshot_timeframe=effective_settings.snapshot_timeframe,
            initial_capital=effective_settings.paper_initial_capital,
            final_equity=portfolio.equity,
            final_cash_balance=portfolio.cash_balance,
            total_return_pct=metrics.total_return_pct,
            candles_processed=len(replay_rows),
            evaluation_count=len(evaluations),
            selected_signal_count=selected_signal_count,
            opened_trade_count=opened_trade_count,
            closed_trade_count=len(closed_trades),
            force_closed_at_end=force_closed_at_end,
            runtime_summary={
                "decision_horizon": effective_settings.decision_horizon,
                "snapshot_timeframe": effective_settings.snapshot_timeframe,
                "snapshot_interval_minutes": effective_settings.snapshot_interval_minutes,
                "engine_include_step2": effective_settings.engine_include_step2,
                "engine_include_step3": effective_settings.engine_include_step3,
                "paper_min_signal_score": effective_settings.paper_min_signal_score,
                "paper_fixed_stop_loss_pct": effective_settings.paper_fixed_stop_loss_pct,
                "paper_fixed_take_profit_pct": effective_settings.paper_fixed_take_profit_pct,
                "paper_atr_stop_multiplier": effective_settings.paper_atr_stop_multiplier,
                "paper_risk_reward_ratio": effective_settings.paper_risk_reward_ratio,
            },
            metrics=metrics,
            open_trades=portfolio_store.get_open_trades(),
            closed_trades=closed_trades,
            events=journal_store.get_events(limit=2000),
            snapshots=journal_store.get_snapshots(limit=5000),
            evaluations=evaluations,
            warnings=warnings,
        )

    def _preload_rows(
        self,
        *,
        request: HistoricalSimulationRequest,
        settings: Settings,
        required_snapshots: int,
        breadth_symbols: Sequence[str],
        warnings: list[str],
    ) -> dict[tuple[str, str], list[list[float]]]:
        rows_by_key: dict[tuple[str, str], list[list[float]]] = {}

        def load(symbol: str, timeframe: str, warmup_rows: int) -> None:
            key = (symbol, timeframe)
            if key in rows_by_key:
                return
            warmup_start = request.start_at - timedelta(minutes=timeframe_to_minutes(timeframe) * warmup_rows)
            try:
                rows_by_key[key] = self.market_data_client.fetch_ohlcv_range(
                    symbol=symbol,
                    timeframe=timeframe,
                    start=warmup_start,
                    end=request.end_at,
                )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"historical_load_failed:{symbol}:{timeframe}:{exc}")
                rows_by_key[key] = []

        snapshot_warmup = self._required_snapshot_history_rows(settings=settings, required_snapshots=required_snapshots)
        load(request.symbol, settings.snapshot_timeframe, snapshot_warmup)
        load(request.symbol, settings.technical_main_timeframe, settings.technical_ohlcv_limit)
        if settings.technical_use_secondary_confirmation:
            load(request.symbol, settings.technical_confirmation_timeframe, settings.technical_ohlcv_limit)
        load(settings.regime_btc_symbol, settings.regime_timeframe, settings.regime_ohlcv_limit)
        if settings.regime_breadth_enabled:
            for breadth_symbol in breadth_symbols:
                load(breadth_symbol, settings.regime_breadth_timeframe, settings.regime_ohlcv_limit)

        return rows_by_key

    def _build_signal(
        self,
        *,
        symbol: str,
        settings: Settings,
        required_snapshots: int,
        breadth_symbols: Sequence[str],
        collector: MarketSnapshotCollector,
        aggregator: HourlySignalAggregator,
        technical_filter: CCXTTechnicalFilter,
        regime_filter: CCXTMarketRegimeFilter,
    ) -> HourlySignal:
        snapshots = collector.collect_recent(symbol=symbol, snapshot_count=required_snapshots)
        signal = aggregator.aggregate(
            symbol=symbol,
            snapshots=snapshots,
            decision_horizon=settings.decision_horizon,
        )

        step2_result: Step2Result | None = None
        step3_result: Step3Result | None = None
        if settings.engine_include_step2:
            step2_result = technical_filter.evaluate(symbol=symbol)
        if settings.engine_include_step3:
            step3_result = regime_filter.evaluate(symbol=symbol, market_symbols=list(breadth_symbols))

        enriched = HourlySignal.model_validate(signal.model_dump())
        if step2_result is not None:
            enriched.step2_score = step2_result.step2_score
            enriched.step2_pass = step2_result.step2_pass
            enriched.step2_entry_signal = step2_result.technical_flags.get("entry_signal")
            enriched.step2_hard_fail = step2_result.technical_flags.get("hard_fail")
            enriched.step2_summary = step2_result.technical_reasoning[0] if step2_result.technical_reasoning else None

        if step3_result is not None:
            enriched.regime_status = step3_result.regime_status
            enriched.step3_pass = step3_result.step3_pass
            enriched.regime_score = step3_result.regime_score
            enriched.step3_fallback_used = step3_result.fallback_used
            enriched.step3_unavailable_risk_metrics = list(step3_result.unavailable_risk_metrics)
            enriched.step3_summary = step3_result.regime_reasoning[0] if step3_result.regime_reasoning else None

        enriched.final_selected = True
        enriched.reject_stage = "NONE"
        enriched.reject_reason_summary = None
        if settings.engine_include_step2 and enriched.step2_pass is not True:
            enriched.final_selected = False
            enriched.reject_stage = "STEP2"
            enriched.reject_reason_summary = enriched.step2_summary or "Adim 2 teknik filtresi gecilemedi."
        elif settings.engine_include_step3 and enriched.step3_pass is not True:
            enriched.final_selected = False
            enriched.reject_stage = "STEP3"
            enriched.reject_reason_summary = enriched.step3_summary or "Adim 3 rejim filtresi veto verdi."

        return enriched

    def _build_breadth_symbols(self, *, symbol: str, settings: Settings) -> list[str]:
        raw_symbols = [symbol, *settings.fallback_symbols]
        unique_symbols: list[str] = []
        for item in raw_symbols:
            normalized = item.strip().upper()
            if normalized == settings.regime_btc_symbol.upper():
                continue
            if normalized not in unique_symbols:
                unique_symbols.append(normalized)
        return unique_symbols[: settings.regime_breadth_symbol_count]

    def _load_runtime_config(self, *, warnings: list[str]) -> RuntimeConfig:
        try:
            return self.runtime_config_store.load()
        except ValueError as exc:
            warnings.append(f"runtime_config_load_failed:{exc}")
            return RuntimeConfig.from_settings(self.settings)

    def _build_effective_settings(self, *, runtime_config: RuntimeConfig, warnings: list[str]) -> Settings:
        payload = self.settings.model_dump()
        payload.update(runtime_config.to_settings_overrides())
        try:
            return Settings(_env_file=None, **payload)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"runtime_config_merge_failed:{exc}")
            return Settings(_env_file=None, **self.settings.model_dump())

    @staticmethod
    def _required_snapshot_history_rows(*, settings: Settings, required_snapshots: int) -> int:
        indicator_warmup = max(
            settings.technical_ma_slow_period + settings.technical_ma_slope_lookback,
            settings.technical_macd_slow + settings.technical_macd_signal,
            settings.technical_bbands_period,
            settings.technical_rsi_period,
            settings.technical_adx_period,
            settings.technical_atr_period,
            settings.technical_volume_ma_period,
            settings.technical_breakout_lookback,
        )
        minimum = max(settings.technical_min_ohlcv_rows, required_snapshots)
        return max(minimum, indicator_warmup + required_snapshots + 1)

    @staticmethod
    def _to_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _row_timestamp(row: list[float]) -> datetime:
        return datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC)

    @staticmethod
    def _row_in_range(*, row: list[float], start_at: datetime, end_at: datetime) -> bool:
        timestamp = datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC)
        return start_at <= timestamp <= end_at

    @staticmethod
    def _signal_price(signal: HourlySignal) -> float | None:
        value = signal.feature_snapshot.get("latest_close")
        if isinstance(value, (int, float)) and float(value) > 0:
            return float(value)
        return None

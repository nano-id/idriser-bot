"""Orchestrator that feeds dashboard signal state from real scan components."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from app.clients.ccxt_client import CCXTUniverseClient
from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.filters.market_regime_filter import CCXTMarketRegimeFilter, MarketRegimeFilter
from app.filters.technical_filter import CCXTTechnicalFilter, TechnicalFilter
from app.models.ai_signal import AISignal
from app.models.hourly_signal import HourlySignal
from app.models.runtime_config import RuntimeConfig
from app.models.step2 import Step2Result
from app.models.step3 import Step3Result
from app.pipeline.ai_support_service import AISupportService
from app.pipeline.hourly_signal_aggregator import HourlySignalAggregator
from app.pipeline.market_snapshot_collector import MarketSnapshotCollector
from app.pipeline.signal_state_store import SignalStateStore
from app.universe.builder import UniverseBuilder
from app.utils.runtime import utc_now
from app.utils.timeframe import required_snapshots_for_horizon


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class EngineRunResult:
    """Summary payload returned by one engine run."""

    run_at: datetime
    signal_count: int
    ai_signal_count: int
    processed_symbols: int
    refresh_seconds: int
    errors: list[str]


class DashboardSignalEngine:
    """Run universe scan and update dashboard-facing in-memory signal state."""

    def __init__(
        self,
        *,
        settings: Settings,
        runtime_config_store: RuntimeConfigStore,
        signal_state_store: SignalStateStore,
        universe_builder: UniverseBuilder | None = None,
        snapshot_collector: MarketSnapshotCollector | None = None,
        aggregator: HourlySignalAggregator | None = None,
        technical_filter: TechnicalFilter | None = None,
        regime_filter: MarketRegimeFilter | None = None,
        ai_support_service: AISupportService | None = None,
    ) -> None:
        self.settings = settings
        self.runtime_config_store = runtime_config_store
        self.signal_state_store = signal_state_store

        self._universe_builder_override = universe_builder
        self._snapshot_collector_override = snapshot_collector
        self._aggregator_override = aggregator
        self._technical_filter_override = technical_filter
        self._regime_filter_override = regime_filter
        self._ai_support_service_override = ai_support_service

        self._universe_client: CCXTUniverseClient | None = None
        self._market_data_client: CCXTMarketDataClient | None = None

    def run_once(self) -> EngineRunResult:
        """Run one scan cycle and write latest state for dashboard consumers."""
        errors: list[str] = []
        run_at = utc_now()
        runtime_config = self._load_runtime_config(errors=errors)
        effective_settings = self._build_effective_settings(runtime_config=runtime_config, errors=errors)

        symbols = self._build_universe_symbols(settings=effective_settings)
        if not symbols:
            msg = "Engine produced no symbols"
            raise RuntimeError(msg)

        decision_horizon = effective_settings.decision_horizon
        required_snapshots = required_snapshots_for_horizon(
            decision_horizon=decision_horizon,
            snapshot_interval_minutes=effective_settings.snapshot_interval_minutes,
        )
        snapshots_by_symbol = self._collect_snapshots(
            settings=effective_settings,
            symbols=symbols,
            required_snapshots=required_snapshots,
            errors=errors,
        )
        aggregate_signals = self._aggregate_signals(
            settings=effective_settings,
            symbols=symbols,
            snapshots_by_symbol=snapshots_by_symbol,
            decision_horizon=decision_horizon,
            errors=errors,
        )

        step2_results_by_symbol: dict[str, Step2Result] = {}
        if effective_settings.engine_include_step2:
            step2_results_by_symbol = self._run_step2(
                settings=effective_settings,
                symbols=symbols,
                errors=errors,
            )

        step3_results_by_symbol: dict[str, Step3Result] = {}
        if effective_settings.engine_include_step3:
            step3_results_by_symbol = self._run_step3(
                settings=effective_settings,
                symbols=symbols,
                errors=errors,
            )

        enriched_signals = self._enrich_signals(
            signals=aggregate_signals,
            step2_results_by_symbol=step2_results_by_symbol,
            step3_results_by_symbol=step3_results_by_symbol,
        )
        annotated_signals = self._annotate_pipeline_state(
            signals=enriched_signals,
            require_step2=effective_settings.engine_include_step2,
            require_step3=effective_settings.engine_include_step3,
        )
        display_signals = self._select_top_signals(
            signals=annotated_signals,
            max_signals=effective_settings.engine_max_signals,
            prefer_step2=effective_settings.engine_include_step2,
            prefer_step3=effective_settings.engine_include_step3,
        )
        pipeline_signals = self._apply_pipeline_filters(
            signals=annotated_signals,
            require_step2=effective_settings.engine_include_step2,
            require_step3=effective_settings.engine_include_step3,
        )
        selected_signals = self._select_top_signals(
            signals=pipeline_signals,
            max_signals=effective_settings.engine_max_signals,
            prefer_step2=effective_settings.engine_include_step2,
            prefer_step3=effective_settings.engine_include_step3,
        )

        self.signal_state_store.set_latest_signals(display_signals)

        ai_signals: list[AISignal] = []
        if effective_settings.engine_include_ai_support and selected_signals:
            ai_signals = self._run_ai_support(
                settings=effective_settings,
                selected_signals=selected_signals,
                step2_results_by_symbol=step2_results_by_symbol,
                step3_results_by_symbol=step3_results_by_symbol,
                errors=errors,
            )
            self.signal_state_store.set_latest_ai_signals(ai_signals)
        else:
            self.signal_state_store.set_latest_ai_signals([])

        return EngineRunResult(
            run_at=run_at,
            signal_count=len(selected_signals),
            ai_signal_count=len(ai_signals),
            processed_symbols=len(symbols),
            refresh_seconds=effective_settings.engine_refresh_seconds,
            errors=errors,
        )

    def _load_runtime_config(self, *, errors: list[str]) -> RuntimeConfig:
        try:
            return self.runtime_config_store.load()
        except ValueError as exc:
            LOGGER.warning("Runtime config load failed, using defaults: %s", exc)
            errors.append(f"runtime_config_load_failed:{exc}")
            return RuntimeConfig.from_settings(self.settings)

    def _build_effective_settings(self, *, runtime_config: RuntimeConfig, errors: list[str]) -> Settings:
        payload = self.settings.model_dump()
        payload.update(runtime_config.to_settings_overrides())
        try:
            return Settings(_env_file=None, **payload)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Runtime config merge failed, using base settings: %s", exc)
            errors.append(f"runtime_config_merge_failed:{exc}")
            return Settings(_env_file=None, **self.settings.model_dump())

    def _build_universe_symbols(self, *, settings: Settings) -> list[str]:
        builder = self._build_universe_builder(settings=settings)
        assets = builder.build(size=settings.engine_universe_size)
        return [asset.exchange_symbol for asset in assets][: settings.engine_universe_size]

    def _collect_snapshots(
        self,
        *,
        settings: Settings,
        symbols: Sequence[str],
        required_snapshots: int,
        errors: list[str],
    ) -> dict[str, list]:
        collector = self._build_snapshot_collector(settings=settings)
        snapshots_by_symbol: dict[str, list] = {}
        for symbol in symbols:
            try:
                snapshots_by_symbol[symbol] = collector.collect_recent(
                    symbol=symbol,
                    snapshot_count=required_snapshots,
                )
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Snapshot collect failed for %s: %s", symbol, exc)
                errors.append(f"snapshot:{symbol}:{exc}")
                snapshots_by_symbol[symbol] = []
        return snapshots_by_symbol

    def _aggregate_signals(
        self,
        *,
        settings: Settings,
        symbols: Sequence[str],
        snapshots_by_symbol: Mapping[str, Sequence],
        decision_horizon: str,
        errors: list[str],
    ) -> list[HourlySignal]:
        aggregator = self._build_aggregator(settings=settings)
        signals: list[HourlySignal] = []
        for symbol in symbols:
            snapshots = snapshots_by_symbol.get(symbol, [])
            try:
                signal = aggregator.aggregate(
                    symbol=symbol,
                    snapshots=snapshots,
                    decision_horizon=decision_horizon,
                )
                signals.append(signal)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Aggregate build failed for %s: %s", symbol, exc)
                errors.append(f"aggregate:{symbol}:{exc}")
        return signals

    def _run_step2(
        self,
        *,
        settings: Settings,
        symbols: Sequence[str],
        errors: list[str],
    ) -> dict[str, Step2Result]:
        technical_filter = self._build_technical_filter(settings=settings)
        outputs: dict[str, Step2Result] = {}
        for symbol in symbols:
            try:
                result = technical_filter.evaluate(symbol=symbol)
                outputs[symbol] = result
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Step2 evaluation failed for %s: %s", symbol, exc)
                errors.append(f"step2:{symbol}:{exc}")
        return outputs

    def _run_step3(
        self,
        *,
        settings: Settings,
        symbols: Sequence[str],
        errors: list[str],
    ) -> dict[str, Step3Result]:
        regime_filter = self._build_regime_filter(settings=settings)
        outputs: dict[str, Step3Result] = {}
        symbol_list = list(symbols)
        for symbol in symbol_list:
            try:
                result = regime_filter.evaluate(symbol=symbol, market_symbols=symbol_list)
                outputs[symbol] = result
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Step3 evaluation failed for %s: %s", symbol, exc)
                errors.append(f"step3:{symbol}:{exc}")
        return outputs

    def _enrich_signals(
        self,
        *,
        signals: Sequence[HourlySignal],
        step2_results_by_symbol: Mapping[str, Step2Result],
        step3_results_by_symbol: Mapping[str, Step3Result],
    ) -> list[HourlySignal]:
        enriched: list[HourlySignal] = []
        for signal in signals:
            item = HourlySignal.model_validate(signal.model_dump())
            item.fallback_used = bool(item.aggregate_flags.get("fallback_used", item.fallback_used))
            item.latest_breakout = bool(item.feature_snapshot.get("latest_breakout", item.latest_breakout))

            step2_result = step2_results_by_symbol.get(item.symbol)
            if step2_result is not None:
                item.step2_score = step2_result.step2_score
                item.step2_pass = step2_result.step2_pass
                item.step2_entry_signal = step2_result.technical_flags.get("entry_signal")
                item.step2_hard_fail = step2_result.technical_flags.get("hard_fail")
                if step2_result.technical_reasoning:
                    item.step2_summary = step2_result.technical_reasoning[0]

            step3_result = step3_results_by_symbol.get(item.symbol)
            if step3_result is not None:
                item.regime_status = step3_result.regime_status
                item.step3_pass = step3_result.step3_pass
                item.regime_score = step3_result.regime_score
                item.step3_fallback_used = step3_result.fallback_used
                item.step3_unavailable_risk_metrics = list(step3_result.unavailable_risk_metrics)
                if step3_result.regime_reasoning:
                    item.step3_summary = step3_result.regime_reasoning[0]

            enriched.append(item)
        return enriched

    def _annotate_pipeline_state(
        self,
        *,
        signals: Sequence[HourlySignal],
        require_step2: bool,
        require_step3: bool,
    ) -> list[HourlySignal]:
        annotated: list[HourlySignal] = []
        for signal in signals:
            item = HourlySignal.model_validate(signal.model_dump())
            item.final_selected = True
            item.reject_stage = "NONE"
            item.reject_reason_summary = None

            if require_step2 and item.step2_pass is not True:
                item.final_selected = False
                item.reject_stage = "STEP2"
                item.reject_reason_summary = item.step2_summary or "Adım 2 teknik filtresi geçilemedi."
            elif require_step3 and item.step3_pass is not True:
                item.final_selected = False
                item.reject_stage = "STEP3"
                item.reject_reason_summary = item.step3_summary or "Adım 3 rejim filtresi veto verdi."

            annotated.append(item)
        return annotated

    def _apply_pipeline_filters(
        self,
        *,
        signals: Sequence[HourlySignal],
        require_step2: bool,
        require_step3: bool,
    ) -> list[HourlySignal]:
        filtered = list(signals)
        if require_step2:
            filtered = [item for item in filtered if item.step2_pass is True]
        if require_step3:
            filtered = [item for item in filtered if item.step3_pass is True]
        return filtered

    def _select_top_signals(
        self,
        *,
        signals: Sequence[HourlySignal],
        max_signals: int,
        prefer_step2: bool = False,
        prefer_step3: bool = False,
    ) -> list[HourlySignal]:
        eligible = [item for item in signals if item.snapshot_count > 0]
        ranked = sorted(
            eligible,
            key=lambda item: (
                1 if prefer_step3 and item.step3_pass is True else 0,
                item.regime_score if prefer_step3 and item.regime_score is not None else -1.0,
                1 if prefer_step2 and item.step2_pass is True else 0,
                item.step2_score if prefer_step2 and item.step2_score is not None else -1.0,
                item.mean_signal,
                item.bullish_ratio,
                item.stability_score,
            ),
            reverse=True,
        )
        return ranked[:max_signals]

    def _run_ai_support(
        self,
        *,
        settings: Settings,
        selected_signals: Sequence[HourlySignal],
        step2_results_by_symbol: Mapping[str, Step2Result],
        step3_results_by_symbol: Mapping[str, Step3Result],
        errors: list[str],
    ) -> list[AISignal]:
        service = self._build_ai_support_service(settings=settings)
        try:
            return service.evaluate_shortlist(
                aggregate_signals=selected_signals,
                step2_results_by_symbol=step2_results_by_symbol,
                step3_results_by_symbol=step3_results_by_symbol,
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("AI support evaluation failed: %s", exc)
            errors.append(f"ai_support:{exc}")
            return []

    def _build_universe_builder(self, *, settings: Settings) -> UniverseBuilder:
        if self._universe_builder_override is not None:
            return self._universe_builder_override
        return UniverseBuilder(settings=settings, ccxt_client=self._get_universe_client())

    def _build_snapshot_collector(self, *, settings: Settings) -> MarketSnapshotCollector:
        if self._snapshot_collector_override is not None:
            return self._snapshot_collector_override
        return MarketSnapshotCollector(settings=settings, market_data_client=self._get_market_data_client(settings))

    def _build_aggregator(self, *, settings: Settings) -> HourlySignalAggregator:
        if self._aggregator_override is not None:
            return self._aggregator_override
        return HourlySignalAggregator(settings=settings)

    def _build_technical_filter(self, *, settings: Settings) -> TechnicalFilter:
        if self._technical_filter_override is not None:
            return self._technical_filter_override
        return CCXTTechnicalFilter(settings=settings, market_data_client=self._get_market_data_client(settings))

    def _build_regime_filter(self, *, settings: Settings) -> MarketRegimeFilter:
        if self._regime_filter_override is not None:
            return self._regime_filter_override
        return CCXTMarketRegimeFilter(settings=settings, market_data_client=self._get_market_data_client(settings))

    def _build_ai_support_service(self, *, settings: Settings) -> AISupportService:
        if self._ai_support_service_override is not None:
            return self._ai_support_service_override
        return AISupportService(settings=settings)

    def _get_universe_client(self) -> CCXTUniverseClient:
        if self._universe_client is None:
            self._universe_client = CCXTUniverseClient(exchange_id=self.settings.exchange_id)
        return self._universe_client

    def _get_market_data_client(self, settings: Settings) -> CCXTMarketDataClient:
        if self._market_data_client is None:
            self._market_data_client = CCXTMarketDataClient(
                exchange_id=settings.exchange_id,
                timeout_seconds=settings.request_timeout_seconds,
                max_retries=settings.request_max_retries,
                backoff_seconds=settings.request_backoff_seconds,
            )
        return self._market_data_client

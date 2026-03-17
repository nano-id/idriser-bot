"""Dashboard signal engine tests with deterministic fakes."""

from __future__ import annotations

from datetime import UTC, datetime

from app.config.settings import Settings
from app.models.ai_signal import AISignal
from app.models.hourly_signal import HourlySignal
from app.models.runtime_config import RuntimeConfig
from app.models.step2 import Step2Result
from app.models.step3 import Step3Result
from app.models.universe import UniverseAsset
from app.pipeline.dashboard_signal_engine import DashboardSignalEngine
from app.pipeline.signal_state_store import SignalStateStore


class FakeRuntimeConfigStore:
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self._runtime_config = runtime_config

    def load(self) -> RuntimeConfig:
        return self._runtime_config


class FakeUniverseBuilder:
    def __init__(self, symbols: list[str]) -> None:
        self._symbols = symbols

    def build(self, size: int | None = None) -> list[UniverseAsset]:
        target = size or len(self._symbols)
        assets: list[UniverseAsset] = []
        for symbol in self._symbols[:target]:
            base, quote = symbol.split("/")
            assets.append(
                UniverseAsset(
                    exchange_symbol=symbol,
                    base_asset=base,
                    quote_asset=quote,
                )
            )
        return assets


class FakeSnapshotCollector:
    def collect_recent(self, *, symbol: str, snapshot_count: int | None = None) -> list:
        return [symbol, snapshot_count]


class FakeAggregator:
    def __init__(self, signals_by_symbol: dict[str, HourlySignal]) -> None:
        self._signals_by_symbol = signals_by_symbol

    def aggregate(self, *, symbol: str, snapshots, decision_horizon: str | None = None) -> HourlySignal:
        source = self._signals_by_symbol[symbol]
        return HourlySignal.model_validate(source.model_dump())


class FakeTechnicalFilter:
    def evaluate(self, symbol: str, base_asset: str | None = None) -> Step2Result:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        return Step2Result(
            symbol=symbol,
            base_asset=(base_asset or symbol.split("/")[0]),
            timeframe="4h",
            confirmation_timeframe="1h",
            step2_score=78.5,
            step2_pass=True,
            technical_reasoning=["ok"],
            technical_snapshot={},
            technical_flags={"hard_fail": False, "entry_signal": True},
            score_breakdown={},
            missing_technical_data=[],
            fallback_used=False,
            generated_at=now,
        )


class MappedTechnicalFilter:
    def __init__(self, payloads: dict[str, tuple[float, bool]]) -> None:
        self.payloads = payloads

    def evaluate(self, symbol: str, base_asset: str | None = None) -> Step2Result:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        score, step2_pass = self.payloads[symbol]
        return Step2Result(
            symbol=symbol,
            base_asset=(base_asset or symbol.split("/")[0]),
            timeframe="4h",
            confirmation_timeframe="1h",
            step2_score=score,
            step2_pass=step2_pass,
            technical_reasoning=["mapped"],
            technical_snapshot={},
            technical_flags={"hard_fail": False, "entry_signal": step2_pass},
            score_breakdown={},
            missing_technical_data=[],
            fallback_used=False,
            generated_at=now,
        )


class FakeRegimeFilter:
    def evaluate(self, symbol: str, market_symbols: list[str] | None = None) -> Step3Result:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        return Step3Result(
            symbol=symbol,
            base_asset=symbol.split("/")[0],
            step3_pass=True,
            regime_status="BULLISH",
            regime_score=82.0,
            regime_reasoning=["ok"],
            regime_snapshot={},
            score_breakdown={},
            fallback_used=False,
            unavailable_risk_metrics=[],
            generated_at=now,
        )


class MappedRegimeFilter:
    def __init__(self, payloads: dict[str, tuple[bool, str, float]]) -> None:
        self.payloads = payloads

    def evaluate(self, symbol: str, market_symbols: list[str] | None = None) -> Step3Result:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        step3_pass, regime_status, regime_score = self.payloads[symbol]
        return Step3Result(
            symbol=symbol,
            base_asset=symbol.split("/")[0],
            step3_pass=step3_pass,
            regime_status=regime_status,
            regime_score=regime_score,
            regime_reasoning=[f"regime:{regime_status.lower()}"],
            regime_snapshot={},
            score_breakdown={},
            fallback_used=not step3_pass,
            unavailable_risk_metrics=["funding_rate"] if not step3_pass else [],
            generated_at=now,
        )


class FakeAISupportService:
    def __init__(self) -> None:
        self.called = False

    def evaluate_shortlist(self, *, aggregate_signals, step2_results_by_symbol=None, step3_results_by_symbol=None):
        self.called = True
        now = datetime(2026, 1, 1, tzinfo=UTC)
        return [
            AISignal(
                symbol=signal.symbol,
                decision_horizon=signal.decision_horizon,
                provider="gemini",
                support_score=71.0,
                narrative_strength=66.0,
                risk_label="MEDIUM",
                summary="support",
                warnings=[],
                fallback_used=False,
                raw_response_excerpt="{}",
                timestamp=now,
            )
            for signal in aggregate_signals
        ]


def _build_signal(symbol: str, mean_signal: float) -> HourlySignal:
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
        stability_score=0.9,
        fallback_used=False,
        latest_breakout=True,
        aggregate_flags={"window_complete": True, "fallback_used": False},
        feature_snapshot={"latest_breakout": True},
    )


def test_run_once_updates_state_with_step_and_ai_results() -> None:
    runtime_config = RuntimeConfig(
        decision_horizon="1h",
        engine_universe_size=3,
        engine_max_signals=2,
        engine_include_step2=True,
        engine_include_step3=True,
        engine_include_ai_support=True,
        paper_max_open_positions=3,
    )
    settings = Settings(_env_file=None, llm_provider="gemini", gemini_api_key="test-key")
    state_store = SignalStateStore()
    ai_service = FakeAISupportService()

    engine = DashboardSignalEngine(
        settings=settings,
        runtime_config_store=FakeRuntimeConfigStore(runtime_config),
        signal_state_store=state_store,
        universe_builder=FakeUniverseBuilder(["BTC/USDT", "ETH/USDT", "BNB/USDT"]),
        snapshot_collector=FakeSnapshotCollector(),
        aggregator=FakeAggregator(
            {
                "BTC/USDT": _build_signal("BTC/USDT", 0.88),
                "ETH/USDT": _build_signal("ETH/USDT", 0.74),
                "BNB/USDT": _build_signal("BNB/USDT", 0.41),
            }
        ),
        technical_filter=FakeTechnicalFilter(),
        regime_filter=FakeRegimeFilter(),
        ai_support_service=ai_service,
    )

    result = engine.run_once()

    latest = state_store.get_latest_signals()
    latest_ai = state_store.get_latest_ai_signals()

    assert result.signal_count == 2
    assert result.ai_signal_count == 2
    assert result.processed_symbols == 3
    assert [item.symbol for item in latest] == ["BTC/USDT", "ETH/USDT"]
    assert latest[0].step2_pass is True
    assert latest[0].step2_score == 78.5
    assert latest[0].regime_status == "BULLISH"
    assert latest[0].step3_pass is True
    assert latest[0].final_selected is True
    assert latest[0].reject_stage == "NONE"
    assert latest[0].step3_summary == "ok"
    assert latest[0].step3_fallback_used is False
    assert len(latest_ai) == 2
    assert ai_service.called is True


def test_run_once_keeps_ai_state_empty_when_ai_disabled() -> None:
    runtime_config = RuntimeConfig(
        decision_horizon="1h",
        engine_universe_size=2,
        engine_max_signals=2,
        engine_include_step2=False,
        engine_include_step3=False,
        engine_include_ai_support=False,
        paper_max_open_positions=2,
    )
    settings = Settings(_env_file=None, llm_provider="gemini", gemini_api_key="test-key")
    state_store = SignalStateStore()
    ai_service = FakeAISupportService()

    engine = DashboardSignalEngine(
        settings=settings,
        runtime_config_store=FakeRuntimeConfigStore(runtime_config),
        signal_state_store=state_store,
        universe_builder=FakeUniverseBuilder(["BTC/USDT", "ETH/USDT"]),
        snapshot_collector=FakeSnapshotCollector(),
        aggregator=FakeAggregator(
            {
                "BTC/USDT": _build_signal("BTC/USDT", 0.82),
                "ETH/USDT": _build_signal("ETH/USDT", 0.71),
            }
        ),
        ai_support_service=ai_service,
    )

    result = engine.run_once()

    assert result.signal_count == 2
    assert result.ai_signal_count == 0
    assert state_store.get_latest_ai_signals() == []
    assert ai_service.called is False


def test_run_once_prioritizes_step2_pass_when_step2_enabled() -> None:
    runtime_config = RuntimeConfig(
        decision_horizon="1h",
        engine_universe_size=3,
        engine_max_signals=2,
        engine_include_step2=True,
        engine_include_step3=False,
        engine_include_ai_support=False,
        paper_max_open_positions=2,
    )
    settings = Settings(_env_file=None)
    state_store = SignalStateStore()

    engine = DashboardSignalEngine(
        settings=settings,
        runtime_config_store=FakeRuntimeConfigStore(runtime_config),
        signal_state_store=state_store,
        universe_builder=FakeUniverseBuilder(["BTC/USDT", "ETH/USDT", "BNB/USDT"]),
        snapshot_collector=FakeSnapshotCollector(),
        aggregator=FakeAggregator(
            {
                "BTC/USDT": _build_signal("BTC/USDT", 0.90),
                "ETH/USDT": _build_signal("ETH/USDT", 0.82),
                "BNB/USDT": _build_signal("BNB/USDT", 0.75),
            }
        ),
        technical_filter=MappedTechnicalFilter(
            {
                "BTC/USDT": (52.0, False),
                "ETH/USDT": (84.0, True),
                "BNB/USDT": (78.0, True),
            }
        ),
    )

    result = engine.run_once()

    latest = state_store.get_latest_signals()
    assert result.signal_count == 2
    assert [item.symbol for item in latest] == ["ETH/USDT", "BNB/USDT"]
    assert latest[0].step2_pass is True
    assert latest[0].step2_summary == "mapped"


def test_run_once_filters_out_step3_failures_when_step3_enabled() -> None:
    runtime_config = RuntimeConfig(
        decision_horizon="1h",
        engine_universe_size=3,
        engine_max_signals=3,
        engine_include_step2=False,
        engine_include_step3=True,
        engine_include_ai_support=False,
        paper_max_open_positions=3,
    )
    settings = Settings(_env_file=None)
    state_store = SignalStateStore()

    engine = DashboardSignalEngine(
        settings=settings,
        runtime_config_store=FakeRuntimeConfigStore(runtime_config),
        signal_state_store=state_store,
        universe_builder=FakeUniverseBuilder(["BTC/USDT", "ETH/USDT", "BNB/USDT"]),
        snapshot_collector=FakeSnapshotCollector(),
        aggregator=FakeAggregator(
            {
                "BTC/USDT": _build_signal("BTC/USDT", 0.90),
                "ETH/USDT": _build_signal("ETH/USDT", 0.82),
                "BNB/USDT": _build_signal("BNB/USDT", 0.75),
            }
        ),
        regime_filter=MappedRegimeFilter(
            {
                "BTC/USDT": (False, "BEARISH", 32.0),
                "ETH/USDT": (True, "BULLISH", 81.0),
                "BNB/USDT": (False, "DANGER", 0.0),
            }
        ),
    )

    result = engine.run_once()

    latest = state_store.get_latest_signals()
    assert result.signal_count == 1
    assert [item.symbol for item in latest] == ["ETH/USDT", "BTC/USDT", "BNB/USDT"]
    assert latest[0].step3_pass is True
    assert latest[0].regime_status == "BULLISH"
    assert latest[0].final_selected is True
    assert latest[0].reject_stage == "NONE"
    assert latest[1].final_selected is False
    assert latest[1].reject_stage == "STEP3"
    assert latest[2].final_selected is False
    assert latest[2].reject_stage == "STEP3"


def test_run_once_keeps_rejected_candidates_visible_when_no_final_signal() -> None:
    runtime_config = RuntimeConfig(
        decision_horizon="1h",
        engine_universe_size=2,
        engine_max_signals=2,
        engine_include_step2=True,
        engine_include_step3=True,
        engine_include_ai_support=False,
        paper_max_open_positions=2,
    )
    settings = Settings(_env_file=None)
    state_store = SignalStateStore()

    engine = DashboardSignalEngine(
        settings=settings,
        runtime_config_store=FakeRuntimeConfigStore(runtime_config),
        signal_state_store=state_store,
        universe_builder=FakeUniverseBuilder(["BTC/USDT", "ETH/USDT"]),
        snapshot_collector=FakeSnapshotCollector(),
        aggregator=FakeAggregator(
            {
                "BTC/USDT": _build_signal("BTC/USDT", 0.81),
                "ETH/USDT": _build_signal("ETH/USDT", 0.76),
            }
        ),
        technical_filter=MappedTechnicalFilter(
            {
                "BTC/USDT": (84.0, True),
                "ETH/USDT": (77.0, True),
            }
        ),
        regime_filter=MappedRegimeFilter(
            {
                "BTC/USDT": (False, "NEUTRAL", 49.0),
                "ETH/USDT": (False, "BEARISH", 32.0),
            }
        ),
    )

    result = engine.run_once()

    latest = state_store.get_latest_signals()
    assert result.signal_count == 0
    assert [item.symbol for item in latest] == ["BTC/USDT", "ETH/USDT"]
    assert all(item.final_selected is False for item in latest)
    assert all(item.reject_stage == "STEP3" for item in latest)

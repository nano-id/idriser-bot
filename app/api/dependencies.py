"""Dependency wiring for dashboard API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, Request

from app.config.runtime_store import RuntimeConfigStore
from app.config.settings import Settings
from app.pipeline.dashboard_signal_engine import DashboardSignalEngine
from app.pipeline.engine_runner import EngineRunner
from app.pipeline.historical_simulation_engine import HistoricalSimulationEngine
from app.pipeline.historical_simulation_store import HistoricalSimulationStore
from app.pipeline.paper_journal_store import PaperJournalStore
from app.pipeline.paper_portfolio_store import PaperPortfolioStore
from app.pipeline.paper_runner import PaperRunner
from app.pipeline.paper_trade_engine import PaperTradeEngine
from app.pipeline.signal_state_store import SignalStateStore


DEFAULT_RUNTIME_CONFIG_PATH = Path("runtime/runtime_config.json")


@dataclass(slots=True)
class AppServices:
    """Container for API-level singleton services."""

    settings: Settings
    runtime_config_store: RuntimeConfigStore
    signal_state_store: SignalStateStore
    dashboard_signal_engine: DashboardSignalEngine
    engine_runner: EngineRunner
    paper_portfolio_store: PaperPortfolioStore
    paper_journal_store: PaperJournalStore
    paper_trade_engine: PaperTradeEngine
    paper_runner: PaperRunner
    historical_simulation_engine: HistoricalSimulationEngine
    historical_simulation_store: HistoricalSimulationStore


def create_app_services(
    *,
    settings: Settings | None = None,
    runtime_config_path: str | Path | None = None,
    signal_state_store: SignalStateStore | None = None,
) -> AppServices:
    """Build service container for one API app instance."""
    resolved_settings = settings or Settings()
    resolved_path = Path(runtime_config_path) if runtime_config_path else DEFAULT_RUNTIME_CONFIG_PATH
    resolved_signal_store = signal_state_store or SignalStateStore()
    runtime_store = RuntimeConfigStore(path=resolved_path, settings=resolved_settings)
    dashboard_engine = DashboardSignalEngine(
        settings=resolved_settings,
        runtime_config_store=runtime_store,
        signal_state_store=resolved_signal_store,
    )
    engine_runner = EngineRunner(
        engine=dashboard_engine,
        refresh_seconds=resolved_settings.engine_refresh_seconds,
    )
    if resolved_settings.engine_enabled:
        engine_runner.start()
    paper_portfolio_store = PaperPortfolioStore(initial_capital=resolved_settings.paper_initial_capital)
    paper_journal_store = PaperJournalStore()
    paper_trade_engine = PaperTradeEngine(
        settings=resolved_settings,
        runtime_config_store=runtime_store,
        signal_state_store=resolved_signal_store,
        portfolio_store=paper_portfolio_store,
        journal_store=paper_journal_store,
    )
    paper_runner = PaperRunner(
        settings=resolved_settings,
        runtime_config_store=runtime_store,
        paper_engine=paper_trade_engine,
        engine_runner=engine_runner,
    )
    historical_simulation_engine = HistoricalSimulationEngine(
        settings=resolved_settings,
        runtime_config_store=runtime_store,
    )
    historical_simulation_store = HistoricalSimulationStore()

    return AppServices(
        settings=resolved_settings,
        runtime_config_store=runtime_store,
        signal_state_store=resolved_signal_store,
        dashboard_signal_engine=dashboard_engine,
        engine_runner=engine_runner,
        paper_portfolio_store=paper_portfolio_store,
        paper_journal_store=paper_journal_store,
        paper_trade_engine=paper_trade_engine,
        paper_runner=paper_runner,
        historical_simulation_engine=historical_simulation_engine,
        historical_simulation_store=historical_simulation_store,
    )


def setup_app_services(
    app: FastAPI,
    *,
    settings: Settings | None = None,
    runtime_config_path: str | Path | None = None,
    signal_state_store: SignalStateStore | None = None,
) -> None:
    """Attach app-wide service container to FastAPI state."""
    app.state.services = create_app_services(
        settings=settings,
        runtime_config_path=runtime_config_path,
        signal_state_store=signal_state_store,
    )


def get_services(request: Request) -> AppServices:
    """Return app-level services from request context."""
    return request.app.state.services


def get_settings(request: Request) -> Settings:
    """API dependency for settings."""
    return get_services(request).settings


def get_runtime_config_store(request: Request) -> RuntimeConfigStore:
    """API dependency for runtime config storage."""
    return get_services(request).runtime_config_store


def get_signal_state_store(request: Request) -> SignalStateStore:
    """API dependency for in-memory latest signal state."""
    return get_services(request).signal_state_store


def get_engine_runner(request: Request) -> EngineRunner:
    """API dependency for dashboard engine runner."""
    return get_services(request).engine_runner


def get_paper_portfolio_store(request: Request) -> PaperPortfolioStore:
    """API dependency for paper portfolio store."""
    return get_services(request).paper_portfolio_store


def get_paper_trade_engine(request: Request) -> PaperTradeEngine:
    """API dependency for paper trade engine."""
    return get_services(request).paper_trade_engine


def get_paper_journal_store(request: Request) -> PaperJournalStore:
    """API dependency for paper simulation journal store."""
    return get_services(request).paper_journal_store


def get_paper_runner(request: Request) -> PaperRunner:
    """API dependency for paper runner."""
    return get_services(request).paper_runner


def get_historical_simulation_engine(request: Request) -> HistoricalSimulationEngine:
    """API dependency for historical replay simulation engine."""
    return get_services(request).historical_simulation_engine


def get_historical_simulation_store(request: Request) -> HistoricalSimulationStore:
    """API dependency for latest historical replay result store."""
    return get_services(request).historical_simulation_store

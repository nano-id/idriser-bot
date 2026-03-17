"""Paper trading routes for dashboard controls and state reads."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_historical_simulation_engine,
    get_historical_simulation_store,
    get_paper_journal_store,
    get_paper_portfolio_store,
    get_paper_runner,
    get_paper_trade_engine,
)
from app.api.schemas import (
    HistoricalSimulationResponse,
    HistoricalSimulationRunRequest,
    PaperActionResponse,
    PaperEventsResponse,
    PaperExportResponse,
    PaperMetricsResponse,
    PaperPortfolioResponse,
    PaperRunOnceResponse,
    PaperSnapshotsResponse,
    PaperStatusResponse,
    PaperTradesResponse,
)
from app.pipeline.historical_simulation_engine import HistoricalSimulationEngine
from app.pipeline.historical_simulation_store import HistoricalSimulationStore
from app.pipeline.paper_journal_store import PaperJournalStore
from app.pipeline.paper_portfolio_store import PaperPortfolioStore
from app.pipeline.paper_runner import PaperRunner
from app.pipeline.paper_trade_engine import PaperTradeEngine


router = APIRouter()


def _to_status_response(status_obj) -> PaperStatusResponse:
    return PaperStatusResponse(
        running=status_obj.running,
        enabled=status_obj.enabled,
        refresh_seconds=status_obj.refresh_seconds,
        sync_engine_before_run=status_obj.sync_engine_before_run,
        last_run_at=status_obj.last_run_at,
        last_success_at=status_obj.last_success_at,
        last_error=status_obj.last_error,
        last_opened_count=status_obj.last_opened_count,
        last_closed_count=status_obj.last_closed_count,
        open_trade_count=status_obj.open_trade_count,
        closed_trade_count=status_obj.closed_trade_count,
        cash_balance=status_obj.cash_balance,
        equity=status_obj.equity,
        realized_pnl=status_obj.realized_pnl,
        unrealized_pnl=status_obj.unrealized_pnl,
    )


@router.get("/paper/status", response_model=PaperStatusResponse)
def get_paper_status(
    paper_runner: PaperRunner = Depends(get_paper_runner),
) -> PaperStatusResponse:
    """Return paper bot runtime status."""
    return _to_status_response(paper_runner.status())


@router.post("/paper/run-once", response_model=PaperRunOnceResponse)
def run_paper_once(
    paper_runner: PaperRunner = Depends(get_paper_runner),
    sync_engine_before_run: bool | None = Query(default=None),
) -> PaperRunOnceResponse:
    """Execute one paper cycle against latest signal state."""
    try:
        status_obj = paper_runner.run_once(sync_engine_before_run=sync_engine_before_run)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Paper run_once failed: {exc}",
        ) from exc

    return PaperRunOnceResponse(
        opened_count=status_obj.last_opened_count,
        closed_count=status_obj.last_closed_count,
        status=_to_status_response(status_obj),
    )


@router.post("/paper/start", response_model=PaperActionResponse)
def start_paper_runner(
    paper_runner: PaperRunner = Depends(get_paper_runner),
) -> PaperActionResponse:
    """Start background paper simulation loop."""
    return PaperActionResponse(action="start", status=_to_status_response(paper_runner.start()))


@router.post("/paper/stop", response_model=PaperActionResponse)
def stop_paper_runner(
    paper_runner: PaperRunner = Depends(get_paper_runner),
) -> PaperActionResponse:
    """Stop background paper simulation loop."""
    return PaperActionResponse(action="stop", status=_to_status_response(paper_runner.stop()))


@router.post("/paper/reset", response_model=PaperStatusResponse)
def reset_paper_portfolio(
    paper_engine: PaperTradeEngine = Depends(get_paper_trade_engine),
    paper_runner: PaperRunner = Depends(get_paper_runner),
) -> PaperStatusResponse:
    """Reset paper portfolio/trades to initial capital state."""
    paper_engine.reset()
    return _to_status_response(paper_runner.status())


@router.get("/paper/portfolio", response_model=PaperPortfolioResponse)
def get_paper_portfolio(
    portfolio_store: PaperPortfolioStore = Depends(get_paper_portfolio_store),
) -> PaperPortfolioResponse:
    """Return current paper portfolio summary."""
    return PaperPortfolioResponse(portfolio=portfolio_store.get_portfolio())


@router.get("/paper/trades/open", response_model=PaperTradesResponse)
def get_open_paper_trades(
    portfolio_store: PaperPortfolioStore = Depends(get_paper_portfolio_store),
) -> PaperTradesResponse:
    """Return currently open paper trades."""
    trades = portfolio_store.get_open_trades()
    return PaperTradesResponse(count=len(trades), trades=trades)


@router.get("/paper/trades/closed", response_model=PaperTradesResponse)
def get_closed_paper_trades(
    portfolio_store: PaperPortfolioStore = Depends(get_paper_portfolio_store),
) -> PaperTradesResponse:
    """Return closed paper trades history."""
    trades = portfolio_store.get_closed_trades()
    return PaperTradesResponse(count=len(trades), trades=trades)


@router.get("/paper/metrics", response_model=PaperMetricsResponse)
def get_paper_metrics(
    portfolio_store: PaperPortfolioStore = Depends(get_paper_portfolio_store),
    journal_store: PaperJournalStore = Depends(get_paper_journal_store),
) -> PaperMetricsResponse:
    """Return aggregate paper simulation performance metrics."""
    metrics = journal_store.build_metrics(
        portfolio=portfolio_store.get_portfolio(),
        closed_trades=portfolio_store.get_closed_trades(),
    )
    return PaperMetricsResponse(metrics=metrics)


@router.get("/paper/events", response_model=PaperEventsResponse)
def get_paper_events(
    journal_store: PaperJournalStore = Depends(get_paper_journal_store),
    limit: int = Query(default=50, ge=1, le=500),
) -> PaperEventsResponse:
    """Return recent paper simulation journal events."""
    events = journal_store.get_events(limit=limit)
    return PaperEventsResponse(count=len(events), events=events)


@router.get("/paper/snapshots", response_model=PaperSnapshotsResponse)
def get_paper_snapshots(
    journal_store: PaperJournalStore = Depends(get_paper_journal_store),
    limit: int = Query(default=200, ge=1, le=5000),
) -> PaperSnapshotsResponse:
    """Return recent paper equity snapshots for curve analysis."""
    snapshots = journal_store.get_snapshots(limit=limit)
    return PaperSnapshotsResponse(count=len(snapshots), snapshots=snapshots)


@router.get("/paper/export", response_model=PaperExportResponse)
def export_paper_state(
    portfolio_store: PaperPortfolioStore = Depends(get_paper_portfolio_store),
    journal_store: PaperJournalStore = Depends(get_paper_journal_store),
    event_limit: int = Query(default=200, ge=1, le=500),
    snapshot_limit: int = Query(default=1000, ge=1, le=5000),
) -> PaperExportResponse:
    """Return one full paper simulation export payload for local analysis."""
    portfolio = portfolio_store.get_portfolio()
    closed_trades = portfolio_store.get_closed_trades()
    return PaperExportResponse(
        portfolio=portfolio,
        metrics=journal_store.build_metrics(
            portfolio=portfolio,
            closed_trades=closed_trades,
        ),
        open_trades=portfolio_store.get_open_trades(),
        closed_trades=closed_trades,
        events=journal_store.get_events(limit=event_limit),
        snapshots=journal_store.get_snapshots(limit=snapshot_limit),
    )


@router.post("/paper/historical/run", response_model=HistoricalSimulationResponse)
def run_historical_simulation(
    payload: HistoricalSimulationRunRequest,
    simulation_engine: HistoricalSimulationEngine = Depends(get_historical_simulation_engine),
    simulation_store: HistoricalSimulationStore = Depends(get_historical_simulation_store),
) -> HistoricalSimulationResponse:
    """Replay one symbol between two dates using the active runtime parameters."""
    try:
        result = simulation_engine.run(
            symbol=payload.symbol,
            start_at=payload.start_at,
            end_at=payload.end_at,
            close_open_positions_at_end=payload.close_open_positions_at_end,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Historical simulation failed: {exc}",
        ) from exc

    simulation_store.set_latest(result)
    return HistoricalSimulationResponse(result=result)


@router.get("/paper/historical/latest", response_model=HistoricalSimulationResponse)
def get_latest_historical_simulation(
    simulation_store: HistoricalSimulationStore = Depends(get_historical_simulation_store),
) -> HistoricalSimulationResponse:
    """Return the latest historical replay result if one exists."""
    return HistoricalSimulationResponse(result=simulation_store.get_latest())

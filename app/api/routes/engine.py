"""Engine control routes for dashboard scan loop."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_engine_runner
from app.api.schemas import EngineActionResponse, EngineStatusResponse
from app.pipeline.engine_runner import EngineRunner


router = APIRouter()


def _to_status_response(status_obj) -> EngineStatusResponse:
    return EngineStatusResponse(
        running=status_obj.running,
        last_run_at=status_obj.last_run_at,
        last_success_at=status_obj.last_success_at,
        last_error=status_obj.last_error,
        latest_signal_count=status_obj.latest_signal_count,
        latest_ai_signal_count=status_obj.latest_ai_signal_count,
    )


@router.get("/engine/status", response_model=EngineStatusResponse)
def get_engine_status(
    runner: EngineRunner = Depends(get_engine_runner),
) -> EngineStatusResponse:
    """Return current engine runner status."""
    return _to_status_response(runner.status())


@router.post("/engine/run-once", response_model=EngineActionResponse)
def run_engine_once(
    runner: EngineRunner = Depends(get_engine_runner),
) -> EngineActionResponse:
    """Trigger one synchronous scan cycle."""
    try:
        status_obj = runner.run_once()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Engine run_once failed: {exc}",
        ) from exc

    return EngineActionResponse(
        action="run_once",
        status=_to_status_response(status_obj),
    )


@router.post("/engine/start", response_model=EngineActionResponse)
def start_engine(
    runner: EngineRunner = Depends(get_engine_runner),
) -> EngineActionResponse:
    """Start periodic background scan loop."""
    status_obj = runner.start()
    return EngineActionResponse(
        action="start",
        status=_to_status_response(status_obj),
    )


@router.post("/engine/stop", response_model=EngineActionResponse)
def stop_engine(
    runner: EngineRunner = Depends(get_engine_runner),
) -> EngineActionResponse:
    """Stop periodic background scan loop."""
    status_obj = runner.stop()
    return EngineActionResponse(
        action="stop",
        status=_to_status_response(status_obj),
    )

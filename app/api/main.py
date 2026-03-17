"""FastAPI app entrypoint for dashboard backend surface."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.dependencies import setup_app_services
from app.api.routes import engine_router, health_router, paper_router, runtime_config_router, signals_router, system_router, web_router
from app.config.settings import Settings
from app.pipeline.signal_state_store import SignalStateStore


APP_VERSION = "0.1.0-dev"
WEB_STATIC_DIR = Path(__file__).resolve().parents[1] / "web" / "static"


def create_app(
    *,
    settings: Settings | None = None,
    runtime_config_path: str | Path | None = None,
    signal_state_store: SignalStateStore | None = None,
) -> FastAPI:
    """Create configured FastAPI app instance."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        setup_app_services(
            app,
            settings=settings,
            runtime_config_path=runtime_config_path,
            signal_state_store=signal_state_store,
        )
        app.state.app_version = APP_VERSION
        try:
            yield
        finally:
            services = getattr(app.state, "services", None)
            if services is not None and hasattr(services, "engine_runner"):
                services.engine_runner.stop()
            if services is not None and hasattr(services, "paper_runner"):
                services.paper_runner.stop()

    app = FastAPI(
        title="Signal Engine Dashboard API",
        version=APP_VERSION,
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory=str(WEB_STATIC_DIR)), name="static")
    app.include_router(web_router)
    app.include_router(health_router)
    app.include_router(system_router)
    app.include_router(runtime_config_router)
    app.include_router(signals_router)
    app.include_router(engine_router)
    app.include_router(paper_router)
    return app


app = create_app()

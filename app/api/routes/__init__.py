"""Route exports for dashboard API."""

from app.api.routes.engine import router as engine_router
from app.api.routes.health import router as health_router
from app.api.routes.paper import router as paper_router
from app.api.routes.runtime_config import router as runtime_config_router
from app.api.routes.signals import router as signals_router
from app.api.routes.system import router as system_router
from app.api.routes.web import router as web_router

__all__ = [
    "engine_router",
    "health_router",
    "paper_router",
    "runtime_config_router",
    "signals_router",
    "system_router",
    "web_router",
]

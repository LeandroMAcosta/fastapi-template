from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.telemetry import setup_telemetry
from app.database.base import check_db_health
from app.middleware import register_middleware
from app.routers import api_router

setup_logging()
setup_telemetry()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "application_started",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        debug_mode=settings.DEBUG_MODE,
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-ready FastAPI template with JWT auth, async PostgreSQL, and repository pattern.",
        debug=settings.DEBUG_MODE,
        docs_url="/docs" if settings.DEBUG_MODE else None,
        redoc_url="/redoc" if settings.DEBUG_MODE else None,
        lifespan=lifespan,
    )

    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT, traces_sample_rate=0.1)

    register_exception_handlers(app)
    register_middleware(app)

    app.include_router(api_router, prefix="/api/v1")
    add_pagination(app)

    @app.get("/health", tags=["Health"], summary="Health check")
    async def health():
        try:
            await check_db_health()
            return {"status": "ok", "database": "ok"}
        except Exception:
            return {"status": "degraded", "database": "unavailable"}

    return app


app = create_app()

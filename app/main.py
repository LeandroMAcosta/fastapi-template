from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.database.base import check_db_health
from app.middleware.access_logger import AccessLoggerMiddleware
from app.routers import api_router

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

    # Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT, traces_sample_rate=0.1)

    # Global exception handler for unhandled errors
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"type": "server_error", "message": "Internal server error"},
        )

    # Rate limiting
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Middleware (order matters: first added = outermost)
    app.add_middleware(AccessLoggerMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(api_router, prefix="/api/v1")

    # Pagination
    add_pagination(app)

    # Health check
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health():
        try:
            await check_db_health()
            return {"status": "ok", "database": "ok"}
        except Exception:
            return {"status": "degraded", "database": "unavailable"}

    return app


app = create_app()

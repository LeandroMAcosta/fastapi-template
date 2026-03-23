import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        first = errors[0] if errors else {}
        field = " → ".join(str(loc) for loc in first.get("loc", []) if loc != "body")
        message = f"{field}: {first.get('msg', 'Invalid input')}" if field else first.get("msg", "Invalid input")
        return JSONResponse(
            status_code=422,
            content={"type": "validation_error", "message": message, "errors": errors},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"type": "server_error", "message": "Internal server error"},
        )

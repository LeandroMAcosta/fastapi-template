from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base exception with structured detail: {"type": "...", "message": "..."}."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type: str = "server_error"
    default_message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        detail = {"type": self.error_type, "message": message or self.default_message}
        super().__init__(status_code=self.status_code, detail=detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_type = "not_found"
    default_message = "Resource not found"


class DuplicateError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_type = "duplicate"
    default_message = "Resource already exists"


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_type = "forbidden"
    default_message = "Forbidden"


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_type = "bad_request"
    default_message = "Bad request"

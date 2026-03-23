"""Unit tests for custom exceptions — no DB needed."""

from app.core.exceptions import BadRequestError, DuplicateError, ForbiddenError, NotFoundError


class TestAppError:
    def test_detail_format(self):
        error = NotFoundError("Item not found")
        assert error.detail == {"type": "not_found", "message": "Item not found"}

    def test_default_message(self):
        error = NotFoundError()
        assert error.detail == {"type": "not_found", "message": "Resource not found"}


class TestExceptions:
    def test_not_found(self):
        error = NotFoundError("Item not found")
        assert error.status_code == 404
        assert error.detail["type"] == "not_found"
        assert error.detail["message"] == "Item not found"

    def test_duplicate(self):
        error = DuplicateError()
        assert error.status_code == 409
        assert error.detail["type"] == "duplicate"

    def test_forbidden(self):
        error = ForbiddenError()
        assert error.status_code == 403
        assert error.detail["type"] == "forbidden"

    def test_bad_request(self):
        error = BadRequestError("Invalid input")
        assert error.status_code == 400
        assert error.detail["message"] == "Invalid input"

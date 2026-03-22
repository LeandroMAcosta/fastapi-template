"""Unit tests for custom exceptions — no DB needed."""

from app.core.exceptions import BadRequestError, DuplicateError, ForbiddenError, NotFoundError


class TestExceptions:
    def test_not_found_status(self):
        error = NotFoundError("Item not found")
        assert error.status_code == 404
        assert error.detail == "Item not found"

    def test_duplicate_status(self):
        error = DuplicateError("Already exists")
        assert error.status_code == 409

    def test_forbidden_status(self):
        error = ForbiddenError()
        assert error.status_code == 403

    def test_bad_request_status(self):
        error = BadRequestError("Invalid input")
        assert error.status_code == 400

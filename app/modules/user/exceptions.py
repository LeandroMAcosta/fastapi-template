from app.core.exceptions import DuplicateError, NotFoundError


class UserNotFoundError(NotFoundError):
    error_type = "user_not_found"
    default_message = "User not found"


class UserAlreadyExistsError(DuplicateError):
    error_type = "user_already_exists"
    default_message = "User with this email already exists"

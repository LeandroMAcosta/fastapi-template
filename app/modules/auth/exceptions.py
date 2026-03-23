from app.core.exceptions import AppError


class InvalidCredentialsError(AppError):
    status_code = 401
    error_type = "invalid_credentials"
    default_message = "Invalid email or password"


class UserDisabledError(AppError):
    status_code = 403
    error_type = "user_disabled"
    default_message = "User account is disabled"


class InvalidTokenError(AppError):
    status_code = 401
    error_type = "invalid_token"
    default_message = "Invalid token"


class TokenExpiredError(AppError):
    status_code = 401
    error_type = "token_expired"
    default_message = "Token has expired"


class InsufficientPermissionsError(AppError):
    status_code = 403
    error_type = "insufficient_permissions"
    default_message = "You do not have permission to perform this action"

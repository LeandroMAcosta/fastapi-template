from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "FastAPI Template"
    DEBUG_MODE: bool = False
    ENVIRONMENT: Environment = Environment.LOCAL

    # Database
    DB_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/app_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 50
    DB_POOL_PRE_PING: bool = True

    # Auth
    AUTH_JWT_SECRET: str = "change-me-in-production"
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRATION_MINUTES: int = 15
    AUTH_REFRESH_TOKEN_EXPIRATION_DAYS: int = 7

    # Cookies
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Sentry
    SENTRY_DSN: str = ""

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "fastapi-template"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    OTEL_TRACES_SAMPLE_RATE: float = 1.0


settings = Settings()

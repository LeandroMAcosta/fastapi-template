from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "FastAPI Template"
    DEBUG_MODE: bool = False
    ENVIRONMENT: str = "local"

    # Database
    DB_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/app_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 50
    DB_POOL_PRE_PING: bool = True

    # Auth
    AUTH_JWT_SECRET: str = "change-me-in-production"
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_JWT_EXPIRATION_MINUTES: int = 60

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Sentry
    SENTRY_DSN: str = ""


settings = Settings()

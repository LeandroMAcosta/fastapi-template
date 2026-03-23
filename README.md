# FastAPI Template

[![CI](https://github.com/LeandroMAcosta/fastapi-template/actions/workflows/ci.yml/badge.svg)](https://github.com/LeandroMAcosta/fastapi-template/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/LeandroMAcosta/fastapi-template/branch/main/graph/badge.svg)](https://codecov.io/gh/LeandroMAcosta/fastapi-template)

Production-ready FastAPI template with async PostgreSQL, JWT auth, repository pattern, and dependency injection.

## Features

- **Async PostgreSQL** — psycopg v3 + SQLAlchemy 2.0 async
- **JWT Auth** — Access + refresh tokens with PyJWT
- **Repository Pattern** — Generic CRUD with `SQLAlchemyRepository[T]`
- **Dependency Injection** — `Depends()` chain: DB → Repository → Service → Router
- **Rate Limiting** — slowapi on auth endpoints
- **Structured Logging** — structlog with request ID tracing
- **Filtering & Pagination** — fastapi-filter + fastapi-pagination
- **Alembic Migrations** — Date-prefixed, reversible
- **Structured Errors** — `{"type": "...", "message": "..."}` format
- **Sentry** — Optional error tracking

## Project Structure

```
app/
├── core/           # Config, auth, base exceptions
├── database/       # Engine, base repository, base service
├── middleware/      # Access logger with request ID
├── migrations/     # Alembic migrations
└── modules/
    ├── auth/       # Register, login, refresh (public)
    └── user/       # CRUD endpoints (protected)
```

## Setup

```bash
# Install dependencies
uv sync --dev

# Configure environment
cp .env.example .env

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up
```

Starts PostgreSQL, API (with migrations), and frontend.

## Testing

```bash
# Unit tests (no DB)
./scripts/test.sh unit

# E2E tests (testcontainers PostgreSQL)
./scripts/test.sh e2e

# All tests
./scripts/test.sh all
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```

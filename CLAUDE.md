# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install
uv sync --dev

# Run dev server
uv run uvicorn app.main:app --reload

# Lint
uv run ruff check --fix . && uv run ruff format .

# Tests (unit = no DB, e2e = testcontainers PostgreSQL, requires Docker)
./scripts/test.sh unit
./scripts/test.sh e2e
./scripts/test.sh all

# Run a single test
uv run pytest tests/unit/core/test_auth.py::TestCreateAccessToken::test_creates_valid_token -v

# Migrations
uv run alembic upgrade head
uv run alembic downgrade -1
./scripts/migrate.sh create "description"

# Docker (PostgreSQL + API + frontend)
docker compose up
```

## Architecture

**DI chain via `Depends()` in constructors** — FastAPI auto-resolves the full chain without factory functions:
```
get_db() → SQLAlchemyRepository(db=Depends(get_db)) → UserService(repository=Depends()) → route handler
```

**Module structure** — each module in `app/modules/` is self-contained:
- `models.py` → SQLAlchemy model
- `repository.py` → extends `SQLAlchemyRepository[T]` (async CRUD)
- `service.py` → extends `BaseService[T]`, business logic
- `routers.py` → FastAPI endpoints, uses `Service = Depends()`
- `schemas.py` → Pydantic request/response models
- `exceptions.py` → module-specific errors inheriting from `AppError`
- `filters.py` → fastapi-filter definitions

To add a new module: create the directory with the above files, then register its router in `app/routers.py`.

**RBAC** — permissions are embedded in the JWT at login (`permissions` claim). Routes check via `dependencies=[Depends(require_permissions("resource:action"))]`. No DB query per request.

**Exceptions** — all errors return `{"type": "error_type", "message": "Human-readable message"}`. Create module exceptions by subclassing `AppError` (or `NotFoundError`, `DuplicateError`, etc.) with `error_type` and `default_message` class attributes.

**Async DB** — psycopg v3 with `create_async_engine`. All repository/service methods are async. Alembic migrations use sync psycopg (same driver, sync mode).

## Testing

- **Unit tests** (`tests/unit/`) — no DB, services tested with `MagicMock`/`AsyncMock` repositories
- **E2E tests** (`tests/e2e/`) — real PostgreSQL via testcontainers, Alembic migrations run automatically, `httpx.AsyncClient` with `ASGITransport`
- **Factories** — `tests/factories/` uses polyfactory for generating test data
- **Coverage** — separate configs in `coverage/unit.ini` (excludes routers/middleware) and `coverage/e2e.ini` (measures everything). Minimum 70%
- **pytest-asyncio** — `asyncio_mode = "auto"`, async test methods detected automatically

## Migrations

**NEVER write migration files manually.** Always use Alembic CLI to generate them:
```bash
./scripts/migrate.sh create "description"   # autogenerate from model changes
uv run alembic upgrade head                  # apply
uv run alembic downgrade -1                  # rollback one
```

When adding models, import them in `app/migrations/env.py` so Alembic detects them for autogenerate.

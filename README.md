# FastAPI Template

[![CI](https://github.com/LeandroMAcosta/fastapi-template/actions/workflows/ci.yml/badge.svg)](https://github.com/LeandroMAcosta/fastapi-template/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/LeandroMAcosta/fastapi-template/branch/main/graph/badge.svg)](https://codecov.io/gh/LeandroMAcosta/fastapi-template)

Production-ready FastAPI template with async PostgreSQL, JWT auth, RBAC, repository pattern, dependency injection, and full observability stack.

## Features

- **Async PostgreSQL** — psycopg v3 + SQLAlchemy 2.0 async
- **JWT Auth** — Access + refresh tokens with PyJWT
- **RBAC** — Role-based access control with permissions embedded in JWT
- **Repository Pattern** — Generic CRUD with `SQLAlchemyRepository[T]`
- **Dependency Injection** — `Depends()` chain: DB → Repository → Service → Router
- **Rate Limiting** — slowapi on auth endpoints
- **Structured Logging** — structlog with request ID tracing, JSON output in production
- **OpenTelemetry** — Traces, metrics, and logs exported via OTLP
- **Observability Stack** — Grafana + Tempo (traces) + Loki (logs) + Prometheus (metrics)
- **Filtering & Pagination** — fastapi-filter + fastapi-pagination
- **Alembic Migrations** — Date-prefixed, reversible
- **Structured Errors** — Consistent `{"type": "...", "message": "..."}` format (including 422 validation errors)
- **Sentry** — Optional error tracking

## Project Structure

```
app/
├── core/           # Config, auth, exceptions, logging, telemetry
├── database/       # Engine, base repository, base service
├── middleware/      # Access logger with request ID
├── migrations/     # Alembic migrations
└── modules/
    ├── auth/       # Register, login, refresh (public)
    ├── user/       # CRUD endpoints (protected)
    └── role/       # RBAC models (roles + permissions)

observability/      # Grafana, Tempo, Loki, Prometheus, OTel Collector configs
```

## Setup

```bash
# Install dependencies
uv sync --extra dev

# Configure environment
cp .env.example .env

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run uvicorn app.main:app --reload
```

## Docker

```bash
# Core stack (PostgreSQL + API + frontend)
docker compose up

# With observability (adds Grafana, Tempo, Loki, Prometheus, OTel Collector)
docker compose -f docker-compose.yml -f docker-compose.observability.yml up
```

Grafana is available at `http://localhost:3001` with pre-provisioned datasources (no login required).

## Observability

When running with the observability stack, the API exports traces, metrics, and logs via OpenTelemetry:

```
FastAPI app → OTel Collector → Tempo (traces)
                             → Loki (logs)
                             → Prometheus (metrics)

Grafana queries all three and correlates logs ↔ traces.
```

Configuration is controlled via environment variables (all optional, disabled by default):

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_ENABLED` | `false` | Enable OpenTelemetry export |
| `OTEL_SERVICE_NAME` | `fastapi-template` | Service name in traces/logs |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318` | OTLP HTTP endpoint |
| `OTEL_TRACES_SAMPLE_RATE` | `1.0` | Trace sampling rate (0.0 to 1.0) |

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

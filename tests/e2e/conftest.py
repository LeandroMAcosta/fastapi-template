"""E2E conftest — spins up a real PostgreSQL via testcontainers and runs Alembic migrations."""

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.database.base import get_db
from app.main import create_app


def run_migrations(db_url: str) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_url(postgres_container):
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def async_db_url(db_url):
    return db_url.replace("psycopg2", "psycopg").replace("postgresql://", "postgresql+psycopg://")


@pytest.fixture(scope="session")
def _run_migrations(db_url):
    run_migrations(db_url)


@pytest.fixture(scope="session")
def async_engine(async_db_url, _run_migrations):
    engine = create_async_engine(async_db_url)
    yield engine


@pytest.fixture(scope="module")
async def db_session(async_engine):
    session_factory = async_sessionmaker(bind=async_engine, autocommit=False, autoflush=False, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="module")
async def client(db_session):
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

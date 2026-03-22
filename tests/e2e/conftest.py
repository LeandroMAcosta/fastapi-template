"""E2E conftest — spins up a real PostgreSQL via testcontainers and runs Alembic migrations."""

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
def db_engine(db_url):
    run_migrations(db_url)
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="module")
def client(db_session):
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

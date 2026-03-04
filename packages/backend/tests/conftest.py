"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import sqlite3

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.db.schema import init_db
from app.main import create_app
from app.services.jwt import issue_token


@pytest.fixture
def settings() -> Settings:
    """Test settings with in-memory DB and dummy secrets."""
    return Settings(
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        jwt_secret="test-jwt-secret",
        couchdb_url="http://localhost:5984",
        couchdb_admin_user="admin",
        couchdb_admin_password="admin-password",
        database_path=":memory:",
    )


@pytest.fixture
def db(settings: Settings) -> sqlite3.Connection:
    """In-memory SQLite connection with schema initialized."""
    conn = init_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def app(settings: Settings, db: sqlite3.Connection):
    """FastAPI app with test settings and in-memory DB injected."""
    test_app = create_app(settings)
    # Override the DB with the in-memory one from the fixture
    test_app.state.db = db
    return test_app


@pytest_asyncio.fixture
async def client(app):
    """Async HTTP client for testing the app without a real server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def valid_token(settings: Settings) -> str:
    """A valid JWT token with user_id=1."""
    return issue_token({"user_id": 1, "email": "test@example.com"}, settings.jwt_secret)

"""Tests for OAuth authentication routes."""

from unittest.mock import AsyncMock, patch

import pytest

from app.models.schemas import UserInfo


@pytest.mark.asyncio
async def test_auth_google_redirects(client):
    """GET /auth/google should return a 302 redirect."""
    response = await client.get("/auth/google", follow_redirects=False)
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_auth_google_redirect_url(client):
    """GET /auth/google should redirect to Google OAuth."""
    response = await client.get("/auth/google", follow_redirects=False)
    location = response.headers["location"]
    assert "accounts.google.com" in location
    assert "client_id=test-client-id" in location


@pytest.mark.asyncio
async def test_auth_google_redirect_has_scope(client):
    """Redirect URL should include openid email profile scopes."""
    response = await client.get("/auth/google", follow_redirects=False)
    location = response.headers["location"]
    assert "scope=" in location
    assert "openid" in location


@pytest.mark.asyncio
@patch("app.routes.auth.exchange_code")
@patch("app.routes.auth.provision_vault")
async def test_callback_returns_token(mock_provision, mock_exchange, client):
    """GET /auth/callback should return a JWT token."""
    mock_exchange.return_value = UserInfo(
        google_id="google-123", email="test@example.com", name="Test User"
    )
    mock_provision.return_value = {
        "url": "http://couchdb:5984/vault_1",
        "username": "vault_1",
        "password": "secret",
    }

    response = await client.get("/auth/callback?code=test-code&state=test-state")
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"]) > 0


@pytest.mark.asyncio
@patch("app.routes.auth.exchange_code")
@patch("app.routes.auth.provision_vault")
async def test_callback_upserts_user(mock_provision, mock_exchange, client, db):
    """Callback should create a user in the database."""
    mock_exchange.return_value = UserInfo(
        google_id="google-456", email="new@example.com", name="New User"
    )
    mock_provision.return_value = {
        "url": "http://couchdb:5984/vault_1",
        "username": "vault_1",
        "password": "secret",
    }

    await client.get("/auth/callback?code=test-code&state=test-state")

    row = db.execute(
        "SELECT email FROM users WHERE google_id = ?", ("google-456",)
    ).fetchone()
    assert row is not None
    assert row["email"] == "new@example.com"


@pytest.mark.asyncio
@patch("app.routes.auth.exchange_code")
async def test_callback_oauth_failure(mock_exchange, client):
    """Callback should return 400 if OAuth exchange fails."""
    mock_exchange.side_effect = Exception("OAuth error")

    response = await client.get("/auth/callback?code=bad-code&state=test-state")
    assert response.status_code == 400


@pytest.mark.asyncio
@patch("app.routes.auth.exchange_code")
@patch("app.routes.auth.provision_vault")
async def test_callback_saves_credentials(mock_provision, mock_exchange, client, db):
    """Callback should save vault credentials in the database."""
    mock_exchange.return_value = UserInfo(
        google_id="google-789", email="creds@example.com", name="Creds User"
    )
    mock_provision.return_value = {
        "url": "http://couchdb:5984/vault_1",
        "username": "vault_1",
        "password": "vault-pass",
    }

    await client.get("/auth/callback?code=test-code&state=test-state")

    user = db.execute(
        "SELECT id FROM users WHERE google_id = ?", ("google-789",)
    ).fetchone()
    creds = db.execute(
        "SELECT * FROM vault_credentials WHERE user_id = ?", (user["id"],)
    ).fetchone()
    assert creds is not None
    assert creds["couchdb_url"] == "http://couchdb:5984/vault_1"

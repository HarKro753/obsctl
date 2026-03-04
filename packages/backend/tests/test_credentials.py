"""Tests for the credentials endpoint."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.db.queries import save_credentials, upsert_user
from app.services.jwt import ALGORITHM, issue_token


@pytest.mark.asyncio
async def test_credentials_no_auth_returns_401(client):
    """GET /credentials without auth header should return 401/403."""
    response = await client.get("/credentials")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_credentials_bad_token_returns_401(client):
    """GET /credentials with invalid JWT should return 401."""
    response = await client.get(
        "/credentials",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_credentials_expired_token_returns_401(client, settings):
    """GET /credentials with expired JWT should return 401."""
    payload = {
        "user_id": 1,
        "email": "test@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    expired_token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)

    response = await client.get(
        "/credentials",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_credentials_valid_token_returns_200(client, settings, db):
    """GET /credentials with valid JWT and existing vault returns 200."""
    # Create user and credentials
    user = upsert_user(db, "google-test", "test@example.com")
    save_credentials(db, user["id"], "http://couch:5984/vault_1", "vault_1", "pass123")

    token = issue_token(
        {"user_id": user["id"], "email": "test@example.com"}, settings.jwt_secret
    )

    response = await client.get(
        "/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["couchdb_url"] == "http://couch:5984/vault_1"
    assert data["couchdb_username"] == "vault_1"
    assert data["couchdb_password"] == "pass123"


@pytest.mark.asyncio
async def test_credentials_no_vault_returns_404(client, settings, db):
    """GET /credentials with valid JWT but no vault returns 404."""
    user = upsert_user(db, "google-novault", "novault@example.com")
    token = issue_token(
        {"user_id": user["id"], "email": "novault@example.com"}, settings.jwt_secret
    )

    response = await client.get(
        "/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_credentials_wrong_secret_returns_401(client, settings, db):
    """GET /credentials with token signed by wrong secret returns 401."""
    token = issue_token({"user_id": 1, "email": "test@example.com"}, "wrong-secret")

    response = await client.get(
        "/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (401, 403)

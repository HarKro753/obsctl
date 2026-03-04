"""Tests for CouchDB provisioning service (mocked HTTP)."""

import pytest
import respx
from httpx import Response

from app.config import Settings
from app.services.couchdb import provision_vault


@pytest.fixture
def couchdb_settings() -> Settings:
    """Settings for CouchDB tests."""
    return Settings(
        couchdb_url="http://couchdb:5984",
        couchdb_admin_user="admin",
        couchdb_admin_password="secret",
        database_path=":memory:",
    )


@pytest.mark.asyncio
@respx.mock
async def test_provision_creates_database(couchdb_settings):
    """provision_vault should PUT the database."""
    respx.put("http://couchdb:5984/vault_1").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.get("http://couchdb:5984/_users/org.couchdb.user:vault_1").mock(
        return_value=Response(404)
    )
    respx.put("http://couchdb:5984/_users/org.couchdb.user:vault_1").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.put("http://couchdb:5984/vault_1/_security").mock(
        return_value=Response(200, json={"ok": True})
    )

    result = await provision_vault(couchdb_settings, 1)
    assert result["url"] == "http://couchdb:5984/vault_1"
    assert result["username"] == "vault_1"
    assert "password" in result


@pytest.mark.asyncio
@respx.mock
async def test_provision_creates_user(couchdb_settings):
    """provision_vault should create a CouchDB user document."""
    respx.put("http://couchdb:5984/vault_2").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.get("http://couchdb:5984/_users/org.couchdb.user:vault_2").mock(
        return_value=Response(404)
    )
    user_route = respx.put("http://couchdb:5984/_users/org.couchdb.user:vault_2").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.put("http://couchdb:5984/vault_2/_security").mock(
        return_value=Response(200, json={"ok": True})
    )

    await provision_vault(couchdb_settings, 2)
    assert user_route.called


@pytest.mark.asyncio
@respx.mock
async def test_provision_sets_security_doc(couchdb_settings):
    """provision_vault should set the security doc restricting access."""
    respx.put("http://couchdb:5984/vault_3").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.get("http://couchdb:5984/_users/org.couchdb.user:vault_3").mock(
        return_value=Response(404)
    )
    respx.put("http://couchdb:5984/_users/org.couchdb.user:vault_3").mock(
        return_value=Response(201, json={"ok": True})
    )
    sec_route = respx.put("http://couchdb:5984/vault_3/_security").mock(
        return_value=Response(200, json={"ok": True})
    )

    await provision_vault(couchdb_settings, 3)
    assert sec_route.called


@pytest.mark.asyncio
@respx.mock
async def test_provision_existing_database(couchdb_settings):
    """provision_vault should handle 412 (DB already exists) gracefully."""
    respx.put("http://couchdb:5984/vault_4").mock(
        return_value=Response(412, json={"error": "file_exists"})
    )
    respx.get("http://couchdb:5984/_users/org.couchdb.user:vault_4").mock(
        return_value=Response(404)
    )
    respx.put("http://couchdb:5984/_users/org.couchdb.user:vault_4").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.put("http://couchdb:5984/vault_4/_security").mock(
        return_value=Response(200, json={"ok": True})
    )

    result = await provision_vault(couchdb_settings, 4)
    assert result["username"] == "vault_4"


@pytest.mark.asyncio
@respx.mock
async def test_provision_existing_user_updates(couchdb_settings):
    """provision_vault should update existing CouchDB user with _rev."""
    respx.put("http://couchdb:5984/vault_5").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.get("http://couchdb:5984/_users/org.couchdb.user:vault_5").mock(
        return_value=Response(200, json={"_rev": "1-abc", "name": "vault_5"})
    )
    respx.put("http://couchdb:5984/_users/org.couchdb.user:vault_5").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.put("http://couchdb:5984/vault_5/_security").mock(
        return_value=Response(200, json={"ok": True})
    )

    result = await provision_vault(couchdb_settings, 5)
    assert result["username"] == "vault_5"


@pytest.mark.asyncio
@respx.mock
async def test_provision_db_create_error(couchdb_settings):
    """provision_vault should raise on unexpected DB creation errors."""
    respx.put("http://couchdb:5984/vault_6").mock(
        return_value=Response(500, json={"error": "internal"})
    )

    with pytest.raises(Exception):
        await provision_vault(couchdb_settings, 6)


@pytest.mark.asyncio
@respx.mock
async def test_provision_returns_credentials(couchdb_settings):
    """provision_vault should return url, username, and password."""
    respx.put("http://couchdb:5984/vault_7").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.get("http://couchdb:5984/_users/org.couchdb.user:vault_7").mock(
        return_value=Response(404)
    )
    respx.put("http://couchdb:5984/_users/org.couchdb.user:vault_7").mock(
        return_value=Response(201, json={"ok": True})
    )
    respx.put("http://couchdb:5984/vault_7/_security").mock(
        return_value=Response(200, json={"ok": True})
    )

    result = await provision_vault(couchdb_settings, 7)
    assert "url" in result
    assert "username" in result
    assert "password" in result
    assert len(result["password"]) > 16  # secrets.token_urlsafe(32) is ~43 chars

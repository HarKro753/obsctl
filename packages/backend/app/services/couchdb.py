"""CouchDB provisioning via HTTP API (httpx)."""

from __future__ import annotations

import secrets

import httpx

from app.config import Settings


def _admin_auth(settings: Settings) -> tuple[str, str]:
    """Return (username, password) tuple for CouchDB admin."""
    return (settings.couchdb_admin_user, settings.couchdb_admin_password)


async def provision_vault(settings: Settings, user_id: int) -> dict[str, str]:
    """Provision a CouchDB database and user for a vault.

    This operation is idempotent: if the database and user already exist,
    it updates the security doc and returns the existing credentials.

    Args:
        settings: Application settings with CouchDB connection info.
        user_id: Internal user ID used to derive DB and username.

    Returns:
        Dict with keys: url, username, password.
    """
    db_name = f"vault_{user_id}"
    username = f"vault_{user_id}"
    password = secrets.token_urlsafe(32)
    base_url = settings.couchdb_url.rstrip("/")
    auth = _admin_auth(settings)

    async with httpx.AsyncClient() as client:
        # Create database (ignore 412 = already exists)
        db_resp = await client.put(
            f"{base_url}/{db_name}",
            auth=auth,
        )
        if db_resp.status_code not in (201, 412):
            db_resp.raise_for_status()

        # Create or update CouchDB user
        user_doc_url = f"{base_url}/_users/org.couchdb.user:{username}"

        # Check if user already exists
        existing = await client.get(user_doc_url, auth=auth)

        user_doc = {
            "name": username,
            "password": password,
            "roles": [],
            "type": "user",
        }

        if existing.status_code == 200:
            # Update existing user — include _rev
            user_doc["_rev"] = existing.json()["_rev"]

        user_resp = await client.put(
            user_doc_url,
            json=user_doc,
            auth=auth,
        )
        user_resp.raise_for_status()

        # Set security doc — restrict access to this user only
        security_doc = {
            "admins": {"names": [], "roles": []},
            "members": {"names": [username], "roles": []},
        }
        sec_resp = await client.put(
            f"{base_url}/{db_name}/_security",
            json=security_doc,
            auth=auth,
        )
        sec_resp.raise_for_status()

    return {
        "url": f"{base_url}/{db_name}",
        "username": username,
        "password": password,
    }

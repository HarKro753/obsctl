"""Database query functions. All queries use parameterized statements."""

from __future__ import annotations

import sqlite3
from typing import Any


def upsert_user(conn: sqlite3.Connection, google_id: str, email: str) -> dict[str, Any]:
    """Insert a user or update email if google_id already exists.

    Returns the user row as a dict.
    """
    conn.execute(
        """
        INSERT INTO users (google_id, email)
        VALUES (?, ?)
        ON CONFLICT(google_id) DO UPDATE SET email = excluded.email
        """,
        (google_id, email),
    )
    conn.commit()

    row = conn.execute(
        "SELECT id, google_id, email, created_at FROM users WHERE google_id = ?",
        (google_id,),
    ).fetchone()

    return dict(row)


def save_credentials(
    conn: sqlite3.Connection,
    user_id: int,
    couchdb_url: str,
    couchdb_username: str,
    couchdb_password: str,
) -> None:
    """Insert or replace vault credentials for a user."""
    conn.execute(
        """
        INSERT INTO vault_credentials (user_id, couchdb_url, couchdb_username, couchdb_password)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            couchdb_url = excluded.couchdb_url,
            couchdb_username = excluded.couchdb_username,
            couchdb_password = excluded.couchdb_password
        """,
        (user_id, couchdb_url, couchdb_username, couchdb_password),
    )
    conn.commit()


def get_credentials(conn: sqlite3.Connection, user_id: int) -> dict[str, Any] | None:
    """Fetch vault credentials for a user. Returns None if not found."""
    row = conn.execute(
        """
        SELECT couchdb_url, couchdb_username, couchdb_password
        FROM vault_credentials
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    if row is None:
        return None

    return dict(row)

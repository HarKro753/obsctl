"""SQLite database schema initialization."""

import os
import sqlite3


def init_db(db_path: str) -> sqlite3.Connection:
    """Create tables if they don't exist and return a connection.

    Args:
        db_path: Path to the SQLite database file, or ":memory:" for tests.

    Returns:
        An open sqlite3.Connection with WAL mode enabled (for file DBs).
    """
    # Ensure parent directory exists for file-based databases
    if db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    if db_path != ":memory:":
        conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS vault_credentials (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            couchdb_url TEXT NOT NULL,
            couchdb_username TEXT NOT NULL,
            couchdb_password TEXT NOT NULL
        );
        """
    )
    conn.commit()
    return conn

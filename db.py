"""SQLite storage for Ten Prompts Ago.

One table, `entries`. Every function takes the database path and the owner
(the visitor the entry belongs to), opens a short-lived connection, and
returns plain dicts so templates and the export never touch SQL.
"""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

KINDS = ("decision", "bug")

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id         INTEGER PRIMARY KEY,
    owner      TEXT NOT NULL,
    kind       TEXT NOT NULL CHECK (kind IN ('decision', 'bug')),
    text       TEXT NOT NULL,
    reason     TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS entries_owner ON entries (owner);
"""


def _connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _now():
    return datetime.now(timezone.utc).isoformat()


def init_db(path):
    """Create the database file and table if they don't exist yet."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with closing(_connect(path)) as conn, conn:
        conn.executescript(SCHEMA)


def list_entries(path, owner):
    """All of one owner's entries, newest first."""
    with closing(_connect(path)) as conn:
        rows = conn.execute(
            "SELECT id, kind, text, reason, created_at, updated_at FROM entries"
            " WHERE owner = ? ORDER BY created_at DESC, id DESC",
            (owner,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_entry(path, owner, kind, text, reason):
    """Save a new entry and return its id."""
    now = _now()
    with closing(_connect(path)) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO entries (owner, kind, text, reason, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (owner, kind, text, reason, now, now),
        )
    return cursor.lastrowid


def get_entry(path, owner, entry_id):
    """One of this owner's entries, or None."""
    with closing(_connect(path)) as conn:
        row = conn.execute(
            "SELECT id, kind, text, reason, created_at, updated_at FROM entries"
            " WHERE owner = ? AND id = ?",
            (owner, entry_id),
        ).fetchone()
    return dict(row) if row else None


def update_entry(path, owner, entry_id, kind, text, reason):
    """Change one of this owner's entries. Returns False if it doesn't exist."""
    with closing(_connect(path)) as conn, conn:
        cursor = conn.execute(
            "UPDATE entries SET kind = ?, text = ?, reason = ?, updated_at = ?"
            " WHERE owner = ? AND id = ?",
            (kind, text, reason, _now(), owner, entry_id),
        )
    return cursor.rowcount == 1


def delete_entry(path, owner, entry_id):
    """Remove one of this owner's entries. Returns False if it doesn't exist."""
    with closing(_connect(path)) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM entries WHERE owner = ? AND id = ?", (owner, entry_id)
        )
    return cursor.rowcount == 1

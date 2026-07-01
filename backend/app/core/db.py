"""SQLite data access helpers for the NguonTin MVP."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import settings


USER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('journalist', 'expert', 'admin')),
    full_name TEXT,
    verification_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (verification_status IN ('not_started', 'pending', 'approved', 'rejected')),
    verification_method_label TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


PROFILE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('journalist', 'expert', 'admin')),
    headline TEXT,
    organization TEXT,
    beat TEXT,
    expertise_topics TEXT,
    bio TEXT,
    city TEXT,
    contact_note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


VERIFICATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS verification_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    method_label TEXT NOT NULL,
    evidence_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewer_id INTEGER,
    reviewer_note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(reviewer_id) REFERENCES users(id) ON DELETE SET NULL
);
"""


REQUESTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    topic TEXT NOT NULL,
    location TEXT,
    deadline_text TEXT,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('draft', 'open', 'closed', 'archived')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


PITCHES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pitches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    expert_user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    proposed_angle TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn', 'request_closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(request_id, expert_user_id),
    FOREIGN KEY(request_id) REFERENCES requests(id) ON DELETE CASCADE,
    FOREIGN KEY(expert_user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


MODERATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS moderation_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_user_id INTEGER NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('user', 'request', 'pitch', 'verification')),
    target_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('approve', 'reject', 'flag', 'suspend', 'hide', 'restore')),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(admin_user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


DATABASE_TABLES = [
    USER_TABLE_SQL,
    PROFILE_TABLE_SQL,
    VERIFICATION_TABLE_SQL,
    REQUESTS_TABLE_SQL,
    PITCHES_TABLE_SQL,
    MODERATION_TABLE_SQL,
]


def _database_path() -> Path:
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_database_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_cursor(commit: bool = False) -> Iterator[sqlite3.Cursor]:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        yield cursor
        if commit:
            connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        for statement in DATABASE_TABLES:
            cursor.execute(statement)
        connection.commit()
    finally:
        connection.close()

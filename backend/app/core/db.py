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
    password_hash TEXT,
    role TEXT NOT NULL CHECK (role IN ('journalist', 'expert', 'admin')),
    full_name TEXT,
    auth_preference TEXT NOT NULL DEFAULT 'email_login',
    email_verified_at TEXT,
    verification_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (verification_status IN ('not_started', 'pending', 'approved', 'rejected')),
    verification_method_label TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


EMAIL_LOGIN_CHALLENGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS email_login_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    intended_role TEXT CHECK (intended_role IN ('journalist', 'expert', 'admin')),
    intended_full_name TEXT,
    auth_flow TEXT NOT NULL CHECK (auth_flow IN ('login', 'register')),
    expires_at TEXT NOT NULL,
    consumed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    EMAIL_LOGIN_CHALLENGES_TABLE_SQL,
    PROFILE_TABLE_SQL,
    VERIFICATION_TABLE_SQL,
    REQUESTS_TABLE_SQL,
    PITCHES_TABLE_SQL,
    MODERATION_TABLE_SQL,
]


USER_MIGRATIONS = {
    "password_hash": "ALTER TABLE users ADD COLUMN password_hash TEXT",
    "auth_preference": "ALTER TABLE users ADD COLUMN auth_preference TEXT NOT NULL DEFAULT 'email_login'",
    "email_verified_at": "ALTER TABLE users ADD COLUMN email_verified_at TEXT",
}


def _rebuild_users_table_for_passwordless_auth(cursor: sqlite3.Cursor) -> None:
    cursor.executescript(
        """
        ALTER TABLE users RENAME TO users_legacy_password_hash;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            role TEXT NOT NULL CHECK (role IN ('journalist', 'expert', 'admin')),
            full_name TEXT,
            auth_preference TEXT NOT NULL DEFAULT 'email_login',
            email_verified_at TEXT,
            verification_status TEXT NOT NULL DEFAULT 'not_started'
                CHECK (verification_status IN ('not_started', 'pending', 'approved', 'rejected')),
            verification_method_label TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        INSERT INTO users (
            id,
            email,
            password_hash,
            role,
            full_name,
            auth_preference,
            email_verified_at,
            verification_status,
            verification_method_label,
            created_at,
            updated_at
        )
        SELECT
            id,
            email,
            password_hash,
            role,
            full_name,
            COALESCE(auth_preference, 'email_login'),
            email_verified_at,
            verification_status,
            verification_method_label,
            created_at,
            updated_at
        FROM users_legacy_password_hash;

        DROP TABLE users_legacy_password_hash;
        """
    )


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


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    row = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _existing_columns(cursor: sqlite3.Cursor, table_name: str) -> set[str]:
    rows = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _run_user_table_migrations(cursor: sqlite3.Cursor) -> None:
    if not _table_exists(cursor, "users"):
        return

    existing_columns = _existing_columns(cursor, "users")
    for column_name, statement in USER_MIGRATIONS.items():
        if column_name not in existing_columns:
            cursor.execute(statement)

    password_hash_info = cursor.execute("PRAGMA table_info(users)").fetchall()
    password_hash_column = next((row for row in password_hash_info if row[1] == "password_hash"), None)
    if password_hash_column is not None and password_hash_column[3] == 1:
        _rebuild_users_table_for_passwordless_auth(cursor)


def init_db() -> None:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        for statement in DATABASE_TABLES:
            cursor.execute(statement)
        _run_user_table_migrations(cursor)
        connection.commit()
    finally:
        connection.close()

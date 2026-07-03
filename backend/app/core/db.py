"""Database connection helpers for SQLite and PostgreSQL."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from app.core.config import settings

try:
    import psycopg
    from psycopg.rows import dict_row as _PG_DICT_ROW
    from psycopg import IntegrityError as _PSYCOPG_INTEGRITY_ERROR
    from psycopg import OperationalError as _PSYCOPG_OPERATIONAL_ERROR
except ImportError:  # pragma: no cover
    psycopg = None
    _PG_DICT_ROW = None
    _PSYCOPG_INTEGRITY_ERROR = None
    _PSYCOPG_OPERATIONAL_ERROR = None


class DatabaseError(Exception):
    pass


class DatabaseConnectionError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


def _database_path() -> Path:
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _create_postgres_connection() -> Any:
    if psycopg is None:
        raise RuntimeError("PostgreSQL support requires psycopg[binary].")
    try:
        return psycopg.connect(
            host=settings.pg_host,
            port=settings.pg_port,
            dbname=settings.pg_database,
            user=settings.pg_user,
            password=settings.pg_password,
            sslmode=settings.pg_sslmode,
            row_factory=_PG_DICT_ROW,
        )
    except Exception as exc:
        raise DatabaseConnectionError("Unable to connect to PostgreSQL") from exc


def _create_sqlite_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_database_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_connection() -> Any:
    if settings.postgres_enabled:
        return _create_postgres_connection()
    return _create_sqlite_connection()


class _PostgresCursor:
    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor

    def execute(self, query: str, params: Any = None) -> Any:
        query = query.replace("?", "%s")
        return self._cursor.execute(query, params)

    def executemany(self, query: str, params: Any) -> Any:
        query = query.replace("?", "%s")
        return self._cursor.executemany(query, params)

    def fetchone(self) -> Any:
        return self._cursor.fetchone()

    def fetchall(self) -> Any:
        return self._cursor.fetchall()

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._cursor, attr)


@contextmanager
def db_cursor(commit: bool = False) -> Iterator[Any]:
    connection = get_connection()
    try:
        if settings.postgres_enabled:
            cursor = _PostgresCursor(connection.cursor())
        else:
            cursor = connection.cursor()
        yield cursor
        if commit:
            connection.commit()
    except sqlite3.IntegrityError as exc:
        if settings.postgres_enabled:
            connection.rollback()
        raise IntegrityError from exc
    except _PSYCOPG_INTEGRITY_ERROR as exc:  # type: ignore
        connection.rollback()
        raise IntegrityError from exc
    except Exception:
        if settings.postgres_enabled:
            connection.rollback()
        raise
    finally:
        connection.close()


def _sqlite_table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    row = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _sqlite_existing_columns(cursor: sqlite3.Cursor, table_name: str) -> set[str]:
    rows = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _run_sqlite_user_table_migrations(cursor: sqlite3.Cursor) -> None:
    if not _sqlite_table_exists(cursor, "users"):
        return

    existing_columns = _sqlite_existing_columns(cursor, "users")
    for column_name, statement in USER_MIGRATIONS.items():
        if column_name not in existing_columns:
            cursor.execute(statement)

    password_hash_info = cursor.execute("PRAGMA table_info(users)").fetchall()
    password_hash_column = next((row for row in password_hash_info if row[1] == "password_hash"), None)
    if password_hash_column is not None and password_hash_column[3] == 1:
        _rebuild_users_table_for_passwordless_auth(cursor)


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
                CHECK (status IN ('not_started', 'pending', 'approved', 'rejected')),
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


def init_db() -> None:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        if settings.postgres_enabled:
            for statement in POSTGRES_DATABASE_TABLES:
                cursor.execute(statement)
        else:
            for statement in SQLITE_DATABASE_TABLES:
                cursor.execute(statement)
            _run_sqlite_user_table_migrations(cursor)
        connection.commit()
    finally:
        connection.close()


SQLITE_USER_TABLE_SQL = """
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

SQLITE_EMAIL_LOGIN_CHALLENGES_TABLE_SQL = """
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

SQLITE_PROFILE_TABLE_SQL = """
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

SQLITE_VERIFICATION_TABLE_SQL = """
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

SQLITE_REQUESTS_TABLE_SQL = """
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

SQLITE_PITCHES_TABLE_SQL = """
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

SQLITE_MODERATION_TABLE_SQL = """
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

SQLITE_DATABASE_TABLES = [
    SQLITE_USER_TABLE_SQL,
    SQLITE_EMAIL_LOGIN_CHALLENGES_TABLE_SQL,
    SQLITE_PROFILE_TABLE_SQL,
    SQLITE_VERIFICATION_TABLE_SQL,
    SQLITE_REQUESTS_TABLE_SQL,
    SQLITE_PITCHES_TABLE_SQL,
    SQLITE_MODERATION_TABLE_SQL,
]

POSTGRES_USER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    role TEXT NOT NULL CHECK (role IN ('journalist', 'expert', 'admin')),
    full_name TEXT,
    auth_preference TEXT NOT NULL DEFAULT 'email_login',
    email_verified_at TEXT,
    verification_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (verification_status IN ('not_started', 'pending', 'approved', 'rejected')),
    verification_method_label TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

POSTGRES_EMAIL_LOGIN_CHALLENGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS email_login_challenges (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    intended_role TEXT CHECK (intended_role IN ('journalist', 'expert', 'admin')),
    intended_full_name TEXT,
    auth_flow TEXT NOT NULL CHECK (auth_flow IN ('login', 'register')),
    expires_at TEXT NOT NULL,
    consumed_at TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

POSTGRES_PROFILE_TABLE_SQL = """
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

POSTGRES_VERIFICATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS verification_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    method_label TEXT NOT NULL,
    evidence_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewer_id INTEGER,
    reviewer_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(reviewer_id) REFERENCES users(id) ON DELETE SET NULL
);
"""

POSTGRES_REQUESTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    owner_user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    topic TEXT NOT NULL,
    location TEXT,
    deadline_text TEXT,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('draft', 'open', 'closed', 'archived')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

POSTGRES_PITCHES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pitches (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL,
    expert_user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    proposed_angle TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn', 'request_closed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(request_id, expert_user_id),
    FOREIGN KEY(request_id) REFERENCES requests(id) ON DELETE CASCADE,
    FOREIGN KEY(expert_user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

POSTGRES_MODERATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS moderation_actions (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('user', 'request', 'pitch', 'verification')),
    target_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('approve', 'reject', 'flag', 'suspend', 'hide', 'restore')),
    reason TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(admin_user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

POSTGRES_DATABASE_TABLES = [
    POSTGRES_USER_TABLE_SQL,
    POSTGRES_EMAIL_LOGIN_CHALLENGES_TABLE_SQL,
    POSTGRES_PROFILE_TABLE_SQL,
    POSTGRES_VERIFICATION_TABLE_SQL,
    POSTGRES_REQUESTS_TABLE_SQL,
    POSTGRES_PITCHES_TABLE_SQL,
    POSTGRES_MODERATION_TABLE_SQL,
]

USER_MIGRATIONS = {
    "password_hash": "ALTER TABLE users ADD COLUMN password_hash TEXT",
    "auth_preference": "ALTER TABLE users ADD COLUMN auth_preference TEXT NOT NULL DEFAULT 'email_login'",
    "email_verified_at": "ALTER TABLE users ADD COLUMN email_verified_at TEXT",
}

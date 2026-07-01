"""User data access helpers."""

from __future__ import annotations

import sqlite3
from typing import Any

from app.core.db import db_cursor
from app.models.enums import UserRole


ALLOWED_SELF_SERVICE_ROLES = {UserRole.JOURNALIST.value, UserRole.EXPERT.value}


def create_user(*, email: str, password_hash: str, role: str, full_name: str) -> dict[str, Any]:
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
            """,
            (email.lower().strip(), password_hash, role, full_name.strip()),
        )
        user_id = cursor.lastrowid
    if user_id is None:
        raise RuntimeError("Created user did not return an id")

    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("Created user could not be reloaded")
    return user


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),),
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


def ensure_email_available(email: str) -> None:
    if get_user_by_email(email) is not None:
        raise sqlite3.IntegrityError("email already exists")

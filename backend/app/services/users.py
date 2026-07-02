"""User data access helpers."""

from __future__ import annotations

import sqlite3
from typing import Any

from app.core.db import db_cursor
from app.models.enums import UserRole


ALLOWED_SELF_SERVICE_ROLES = {UserRole.JOURNALIST.value, UserRole.EXPERT.value}


def create_user(
    *,
    email: str,
    role: str,
    full_name: str,
    auth_preference: str = "email_login",
    email_verified_at: str | None = None,
) -> dict[str, Any]:
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO users (email, role, full_name, auth_preference, email_verified_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                email.lower().strip(),
                role,
                full_name.strip(),
                auth_preference,
                email_verified_at,
            ),
        )
        user_id = cursor.lastrowid
    if user_id is None:
        raise RuntimeError("Created user did not return an id")

    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("Created user could not be reloaded")
    return user


def update_user_email_verification(*, user_id: int, verified_at: str) -> dict[str, Any]:
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            UPDATE users
            SET email_verified_at = ?, auth_preference = 'email_login', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (verified_at, user_id),
        )
    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("Updated user could not be reloaded")
    return user


def update_user_auth(*, user_id: int, auth_preference: str, email_verified_at: str | None = None) -> dict[str, Any]:
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            UPDATE users
            SET auth_preference = ?, email_verified_at = COALESCE(?, email_verified_at), updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (auth_preference, email_verified_at, user_id),
        )
    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("Updated user could not be reloaded")
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

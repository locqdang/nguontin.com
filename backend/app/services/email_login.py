"""Email login challenge persistence and verification helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.db import db_cursor
from app.core.security import generate_email_login_code, hash_email_login_code, verify_email_login_code


def create_email_login_challenge(
    *,
    email: str,
    auth_flow: str,
    intended_role: str | None = None,
    intended_full_name: str | None = None,
) -> dict[str, Any]:
    code = generate_email_login_code()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.email_login_code_ttl_minutes)
    normalized_email = email.lower().strip()

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM email_login_challenges WHERE email = ? AND consumed_at IS NULL",
            (normalized_email,),
        )
        cursor.execute(
            """
            INSERT INTO email_login_challenges (
                email,
                code_hash,
                intended_role,
                intended_full_name,
                auth_flow,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                normalized_email,
                hash_email_login_code(code),
                intended_role,
                intended_full_name.strip() if intended_full_name else None,
                auth_flow,
                expires_at.isoformat(),
            ),
        )
        challenge_id = cursor.lastrowid

    return {
        "id": challenge_id,
        "email": normalized_email,
        "code": code,
        "auth_flow": auth_flow,
        "intended_role": intended_role,
        "intended_full_name": intended_full_name.strip() if intended_full_name else None,
        "expires_at": expires_at.isoformat(),
    }


def get_active_email_login_challenge(email: str) -> dict[str, Any] | None:
    normalized_email = email.lower().strip()
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM email_login_challenges
            WHERE email = ? AND consumed_at IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (normalized_email,),
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def consume_email_login_challenge(*, email: str, code: str) -> dict[str, Any] | None:
    challenge = get_active_email_login_challenge(email)
    if challenge is None:
        return None

    expires_at = datetime.fromisoformat(challenge["expires_at"])
    if expires_at < datetime.now(UTC):
        return None

    if not verify_email_login_code(code, challenge["code_hash"]):
        return None

    consumed_at = datetime.now(UTC).isoformat()
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE email_login_challenges SET consumed_at = ? WHERE id = ?",
            (consumed_at, challenge["id"]),
        )

    challenge["consumed_at"] = consumed_at
    return challenge

"""Security helpers for one-time email login codes and JWT access tokens."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets
from typing import Any

import jwt

from app.core.config import settings


_DIGITS = "0123456789"


def generate_email_login_code(length: int = 6) -> str:
    return "".join(secrets.choice(_DIGITS) for _ in range(length))


def hash_email_login_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_email_login_code(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_email_login_code(code), code_hash)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

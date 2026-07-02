"""Profile data access helpers."""

from __future__ import annotations

from typing import Any

from app.core.db import db_cursor
from app.models.enums import UserRole
from app.services.users import get_user_by_id


PROFILE_ALLOWED_ROLES = {UserRole.JOURNALIST.value, UserRole.EXPERT.value, UserRole.ADMIN.value}


def get_profile_by_user_id(*, user_id: int, role: str) -> dict[str, Any] | None:
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = ? AND role = ?",
            (user_id, role),
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def upsert_journalist_profile(
    *,
    user_id: int,
    full_name: str,
    outlet_name: str | None,
    beat: str | None,
    bio: str | None,
    region: str | None,
    contact_note: str | None,
) -> dict[str, Any]:
    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("Cannot create profile for a missing user")
    if user["role"] != UserRole.JOURNALIST.value:
        raise ValueError("Only journalist accounts can manage a journalist profile")

    normalized_outlet_name = outlet_name.strip() if outlet_name else None
    normalized_beat = beat.strip() if beat else None
    normalized_bio = bio.strip() if bio else None
    normalized_region = region.strip() if region else None
    normalized_contact_note = contact_note.strip() if contact_note else None

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO profiles (
                user_id,
                role,
                headline,
                organization,
                beat,
                expertise_topics,
                bio,
                city,
                contact_note
            ) VALUES (?, 'journalist', NULL, ?, ?, NULL, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                organization = excluded.organization,
                beat = excluded.beat,
                bio = excluded.bio,
                city = excluded.city,
                contact_note = excluded.contact_note,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                normalized_outlet_name,
                normalized_beat,
                normalized_bio,
                normalized_region,
                normalized_contact_note,
            ),
        )
        cursor.execute(
            """
            UPDATE users
            SET full_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (full_name.strip(), user_id),
        )

    profile = get_journalist_profile(user_id=user_id)
    if profile is None:
        raise RuntimeError("Created journalist profile could not be reloaded")
    return profile


def get_journalist_profile(*, user_id: int) -> dict[str, Any] | None:
    user = get_user_by_id(user_id)
    if user is None:
        return None

    profile = get_profile_by_user_id(user_id=user_id, role=UserRole.JOURNALIST.value)
    if profile is None:
        return None

    return {
        "user_id": user_id,
        "role": UserRole.JOURNALIST.value,
        "full_name": user.get("full_name") or "",
        "outlet_name": profile.get("organization"),
        "beat": profile.get("beat"),
        "bio": profile.get("bio"),
        "region": profile.get("city"),
        "contact_note": profile.get("contact_note"),
    }

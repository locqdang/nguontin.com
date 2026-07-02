from __future__ import annotations

from pathlib import Path
import os
import tempfile

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token
from app.services.users import create_user


def _make_client() -> tuple[TestClient, str]:
    temp_dir = tempfile.mkdtemp(prefix="nguontin-profiles-test-")
    database_path = str(Path(temp_dir) / "test.db")
    os.environ["DATABASE_PATH"] = database_path
    strong_test_secret = "test-secret-value-with-32-bytes-minimum"
    os.environ["JWT_SECRET"] = strong_test_secret
    settings.database_path = database_path
    settings.jwt_secret = strong_test_secret

    from app.main import app
    from app.core.db import init_db

    init_db()
    return TestClient(app), database_path


def test_journalist_can_create_and_read_own_profile() -> None:
    client, _database_path = _make_client()
    user = create_user(
        email="journalist@example.com",
        role="journalist",
        full_name="Phóng viên An",
    )
    token = create_access_token(str(user["id"]), {"role": user["role"]})

    update_response = client.patch(
        "/profiles/journalist",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Phóng viên An Nguyễn",
            "outlet_name": "Báo Nguồn Tin",
            "beat": "Công nghệ",
            "bio": "Theo dõi startup và chính sách công nghệ.",
            "region": "TP. Hồ Chí Minh",
            "contact_note": "Ưu tiên phản hồi trong giờ hành chính.",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Phóng viên An Nguyễn"
    assert update_response.json()["outlet_name"] == "Báo Nguồn Tin"

    get_response = client.get(
        "/profiles/journalist",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["user_id"] == user["id"]
    assert payload["beat"] == "Công nghệ"
    assert payload["region"] == "TP. Hồ Chí Minh"


def test_journalist_profile_returns_not_found_before_creation() -> None:
    client, _database_path = _make_client()
    user = create_user(
        email="journalist2@example.com",
        role="journalist",
        full_name="Phóng viên Chưa Có Hồ Sơ",
    )
    token = create_access_token(str(user["id"]), {"role": user["role"]})

    response = client.get(
        "/profiles/journalist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_expert_cannot_manage_journalist_profile() -> None:
    client, _database_path = _make_client()
    user = create_user(
        email="expert@example.com",
        role="expert",
        full_name="Chuyên gia B",
    )
    token = create_access_token(str(user["id"]), {"role": user["role"]})

    response = client.patch(
        "/profiles/journalist",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Chuyên gia B"},
    )

    assert response.status_code == 403


def test_profile_requires_authentication() -> None:
    client, _database_path = _make_client()

    response = client.get("/profiles/journalist")

    assert response.status_code == 401

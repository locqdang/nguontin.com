from __future__ import annotations

import os
from pathlib import Path
import tempfile

from fastapi.testclient import TestClient

from app.core.config import settings


def _make_client() -> tuple[TestClient, str]:
    temp_dir = tempfile.mkdtemp(prefix="nguontin-auth-test-")
    database_path = str(Path(temp_dir) / "test.db")
    os.environ["DATABASE_PATH"] = database_path
    os.environ["JWT_SECRET"] = "test-secret"
    settings.database_path = database_path
    settings.jwt_secret = "test-secret"

    from app.main import app
    from app.core.db import init_db

    init_db()
    return TestClient(app), database_path


def test_register_login_and_me_flow() -> None:
    client, _database_path = _make_client()

    register_response = client.post(
        "/auth/register",
        json={
            "email": "journalist@example.com",
            "password": "nguontin123",
            "role": "journalist",
            "full_name": "Phóng viên An",
        },
    )
    assert register_response.status_code == 201
    register_payload = register_response.json()
    assert register_payload["user"]["role"] == "journalist"
    assert register_payload["user"]["email"] == "journalist@example.com"

    login_response = client.post(
        "/auth/login",
        json={
            "email": "journalist@example.com",
            "password": "nguontin123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["full_name"] == "Phóng viên An"


def test_register_rejects_duplicate_email() -> None:
    client, _database_path = _make_client()
    payload = {
        "email": "dup@example.com",
        "password": "nguontin123",
        "role": "expert",
        "full_name": "Chuyên gia Bình",
    }

    assert client.post("/auth/register", json=payload).status_code == 201
    duplicate_response = client.post("/auth/register", json=payload)

    assert duplicate_response.status_code == 409


def test_login_rejects_invalid_password() -> None:
    client, _database_path = _make_client()
    client.post(
        "/auth/register",
        json={
            "email": "expert@example.com",
            "password": "nguontin123",
            "role": "expert",
            "full_name": "Chuyên gia C",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={"email": "expert@example.com", "password": "sai-sai-sai"},
    )

    assert login_response.status_code == 401

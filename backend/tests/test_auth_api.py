from __future__ import annotations

import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.users import create_user


def _make_client() -> tuple[TestClient, str]:
    temp_dir = tempfile.mkdtemp(prefix="nguontin-auth-test-")
    database_path = str(Path(temp_dir) / "test.db")
    os.environ["DATABASE_PATH"] = database_path
    os.environ["JWT_SECRET"] = "test-secret"
    settings.database_path = database_path
    settings.jwt_secret = "test-secret"
    settings.n8n_email_login_webhook_url = ""
    settings.n8n_email_login_webhook_secret = ""

    from app.main import app
    from app.core.db import init_db

    init_db()
    return TestClient(app), database_path


def test_login_start_verify_and_me_flow() -> None:
    client, _database_path = _make_client()
    create_user(
        email="journalist@example.com",
        role="journalist",
        full_name="Phóng viên An",
    )

    start_response = client.post(
        "/auth/email/start",
        json={
            "email": "journalist@example.com",
            "auth_flow": "login",
        },
    )
    assert start_response.status_code == 202
    code = start_response.json()["dev_login_code"]

    verify_response = client.post(
        "/auth/email/verify",
        json={
            "email": "journalist@example.com",
            "code": code,
        },
    )
    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["user"]["role"] == "journalist"
    assert verify_payload["user"]["email"] == "journalist@example.com"
    assert verify_payload["user"]["auth_preference"] == "email_login"
    token = verify_payload["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["full_name"] == "Phóng viên An"


def test_login_start_rejects_unknown_email() -> None:
    client, _database_path = _make_client()

    response = client.post(
        "/auth/email/start",
        json={"email": "missing@example.com", "auth_flow": "login"},
    )
    assert response.status_code == 404


def test_login_verify_rejects_invalid_code() -> None:
    client, _database_path = _make_client()
    create_user(
        email="expert@example.com",
        role="expert",
        full_name="Chuyên gia C",
    )

    login_start = client.post(
        "/auth/email/start",
        json={"email": "expert@example.com", "auth_flow": "login"},
    )
    assert login_start.status_code == 202

    login_response = client.post(
        "/auth/email/verify",
        json={"email": "expert@example.com", "code": "000000"},
    )

    assert login_response.status_code == 401


def test_register_start_and_verify_create_user() -> None:
    client, _database_path = _make_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "role": "expert",
            "full_name": "Chuyên gia Bình",
        },
    )

    assert response.status_code == 202
    code = response.json()["dev_login_code"]

    verify_response = client.post(
        "/auth/email/verify",
        json={"email": "new@example.com", "code": code},
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["user"]["role"] == "expert"
    assert verify_response.json()["user"]["full_name"] == "Chuyên gia Bình"


def test_register_rejects_duplicate_email() -> None:
    client, _database_path = _make_client()
    create_user(
        email="dup@example.com",
        role="journalist",
        full_name="Phóng viên Trùng",
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "dup@example.com",
            "role": "expert",
            "full_name": "Chuyên gia Bình",
        },
    )

    assert response.status_code == 409


def test_register_verify_works_with_legacy_password_hash_not_null_schema() -> None:
    client, database_path = _make_client()

    import sqlite3
    from app.core.db import init_db

    connection = sqlite3.connect(database_path)
    try:
        cursor = connection.cursor()
        cursor.executescript(
            """
            DROP TABLE users;
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('journalist', 'expert', 'admin')),
                full_name TEXT,
                verification_status TEXT NOT NULL DEFAULT 'not_started'
                    CHECK (verification_status IN ('not_started', 'pending', 'approved', 'rejected')),
                verification_method_label TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                auth_preference TEXT NOT NULL DEFAULT 'email_login',
                email_verified_at TEXT
            );
            """
        )
        connection.commit()
    finally:
        connection.close()

    init_db()

    response = client.post(
        "/auth/register",
        json={
            "email": "legacy@example.com",
            "role": "expert",
            "full_name": "Legacy Expert",
        },
    )

    assert response.status_code == 202
    code = response.json()["dev_login_code"]

    verify_response = client.post(
        "/auth/email/verify",
        json={"email": "legacy@example.com", "code": code},
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["user"]["email"] == "legacy@example.com"


def test_register_requires_role_and_full_name() -> None:
    client, _database_path = _make_client()

    response = client.post(
        "/auth/email/start",
        json={
            "email": "new@example.com",
            "auth_flow": "register",
        },
    )

    assert response.status_code == 422


def test_login_start_uses_n8n_webhook_when_configured() -> None:
    client, _database_path = _make_client()
    create_user(
        email="mail@example.com",
        role="journalist",
        full_name="Nguoi Gui Mail",
    )

    settings.n8n_email_login_webhook_url = "https://n8n.example.com/webhook/nguontin-email-login"
    settings.n8n_email_login_webhook_secret = "super-secret"

    with patch("app.api.auth.send_email_login_code") as mock_send_email_login_code:
        response = client.post(
            "/auth/email/start",
            json={
                "email": "mail@example.com",
                "auth_flow": "login",
            },
        )

    settings.n8n_email_login_webhook_url = ""
    settings.n8n_email_login_webhook_secret = ""

    assert response.status_code == 202
    payload = response.json()
    assert payload["delivery_channel"] == "n8n_email"
    assert payload["dev_login_code"] is None
    mock_send_email_login_code.assert_called_once()


def test_sso_contract_routes_exist() -> None:
    client, _database_path = _make_client()
    settings.google_client_id = "google-client-id"
    settings.google_client_secret = "google-client-secret"
    settings.google_oauth_redirect_uri = "https://api.example.com/auth/sso/google/callback"

    start_response = client.get("/auth/sso/google/start")
    assert start_response.status_code == 200
    start_payload = start_response.json()
    assert start_payload["provider"] == "google"
    assert "accounts.google.com" in start_payload["authorization_url"]
    assert "state=" in start_payload["authorization_url"]

    with patch("app.api.auth._complete_google_sso") as mock_complete_google_sso:
        mock_complete_google_sso.return_value = {
            "email": "sso@example.com",
            "full_name": "SSO User",
            "email_verified_at": "2026-01-01T00:00:00+00:00",
        }
        callback_response = client.get(
            "/auth/sso/google/callback",
            params={"code": "provider-code", "state": start_payload["state"]},
            follow_redirects=False,
        )

    assert callback_response.status_code == 302
    redirect_location = callback_response.headers["location"]
    assert "success=0" in redirect_location
    assert "Vui+l%C3%B2ng+%C4%91%C4%83ng+k%C3%BD+tr%C6%B0%E1%BB%9Bc" in redirect_location

    register_start = client.get(
        "/auth/sso/google/start",
        params={"auth_flow": "register", "role": "expert", "full_name": "SSO Expert"},
    )
    assert register_start.status_code == 200

    with patch("app.api.auth._complete_google_sso") as mock_complete_google_sso:
        mock_complete_google_sso.return_value = {
            "email": "sso-register@example.com",
            "full_name": "SSO Expert",
            "email_verified_at": "2026-01-01T00:00:00+00:00",
        }
        register_callback = client.get(
            "/auth/sso/google/callback",
            params={"code": "provider-code", "state": register_start.json()["state"]},
            follow_redirects=False,
        )

    assert register_callback.status_code == 302
    assert "success=1" in register_callback.headers["location"]
    assert "access_token=" in register_callback.headers["location"]

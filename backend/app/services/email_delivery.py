"""Email delivery helpers for passwordless login codes."""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    """Raised when the external email delivery channel fails."""



def send_email_login_code(*, email: str, code: str, auth_flow: str, expires_in_minutes: int) -> None:
    """Send the passwordless login code through the configured delivery channel."""
    if not settings.n8n_email_login_webhook_url:
        return

    payload: dict[str, Any] = {
        "email": email,
        "code": code,
        "auth_flow": auth_flow,
        "expires_in_minutes": expires_in_minutes,
        "app_name": settings.app_name,
        "frontend_base_url": settings.frontend_base_url,
        "subject": _build_subject(auth_flow),
        "message": _build_message(code=code, auth_flow=auth_flow, expires_in_minutes=expires_in_minutes),
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "NguonTin-Backend/0.1",
    }
    if settings.n8n_email_login_webhook_secret:
        headers["X-NguonTin-Webhook-Secret"] = settings.n8n_email_login_webhook_secret

    webhook_request = request.Request(
        settings.n8n_email_login_webhook_url,
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(webhook_request, timeout=settings.email_delivery_timeout_seconds) as response:
            status_code = getattr(response, "status", response.getcode())
            if status_code >= 400:
                raise EmailDeliveryError(f"n8n webhook returned HTTP {status_code}")
    except error.HTTPError as exc:
        raise EmailDeliveryError(f"n8n webhook returned HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise EmailDeliveryError(f"n8n webhook unreachable: {exc.reason}") from exc



def _build_subject(auth_flow: str) -> str:
    if auth_flow == "register":
        return "Ma xac thuc tao tai khoan NguonTin"
    return "Ma dang nhap NguonTin"



def _build_message(*, code: str, auth_flow: str, expires_in_minutes: int) -> str:
    action = "tao tai khoan" if auth_flow == "register" else "dang nhap"
    return (
        f"Ma xac thuc de {action} NguonTin cua ban la {code}. "
        f"Ma nay het han sau {expires_in_minutes} phut."
    )

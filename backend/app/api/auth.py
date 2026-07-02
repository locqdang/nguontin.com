"""Authentication routes."""

from __future__ import annotations

import secrets
import sqlite3
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.models.enums import UserRole
from app.schemas.auth import (
    AuthResponse,
    EmailStartRequest,
    EmailStartResponse,
    EmailVerifyRequest,
    SsoCallbackResponse,
    SsoStartResponse,
    UserResponse,
)
from app.services.email_delivery import EmailDeliveryError, send_email_login_code
from app.services.email_login import create_email_login_challenge, consume_email_login_challenge
from app.services.users import (
    ALLOWED_SELF_SERVICE_ROLES,
    create_user,
    get_user_by_email,
    update_user_email_verification,
)

router = APIRouter(prefix="/auth", tags=["auth"])
SUPPORTED_SSO_PROVIDERS = {"google", "linkedin"}
logger = logging.getLogger(__name__)


def serialize_user(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=UserRole(user["role"]),
        full_name=user.get("full_name"),
        verification_status=user["verification_status"],
        auth_preference=user.get("auth_preference") or "email_login",
    )


@router.post("/login", response_model=EmailStartResponse, status_code=status.HTTP_202_ACCEPTED)
def login(payload: EmailStartRequest) -> EmailStartResponse:
    login_payload = payload.model_copy(update={"role": None, "full_name": None})
    return email_start(login_payload)


@router.post("/register", response_model=EmailStartResponse, status_code=status.HTTP_202_ACCEPTED)
def register(payload: EmailStartRequest) -> EmailStartResponse:
    register_payload = payload.model_copy(update={"auth_flow": "register"})
    return email_start(register_payload)


@router.post("/email/start", response_model=EmailStartResponse, status_code=status.HTTP_202_ACCEPTED)
def email_start(payload: EmailStartRequest) -> EmailStartResponse:
    existing_user = get_user_by_email(payload.email)

    if payload.auth_flow == "login" and existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email này chưa có tài khoản hoạt động.",
        )

    if payload.auth_flow == "register":
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email này đã có tài khoản. Vui lòng đăng nhập thay vì tạo mới.",
            )
        if payload.role is None or payload.full_name is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cần chọn vai trò và nhập họ tên để tạo tài khoản.",
            )
        if payload.role.value not in ALLOWED_SELF_SERVICE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể tự tạo tài khoản nhà báo hoặc chuyên gia.",
            )

    challenge = create_email_login_challenge(
        email=payload.email,
        auth_flow=payload.auth_flow,
        intended_role=payload.role.value if payload.role else None,
        intended_full_name=payload.full_name,
    )

    delivery_channel = "console_dev_code"
    dev_login_code = challenge["code"]
    message = "Mã đăng nhập đã được tạo cho môi trường phát triển. Dùng mã này để hoàn tất đăng nhập."

    if settings.n8n_email_login_webhook_url:
        try:
            send_email_login_code(
                email=challenge["email"],
                code=challenge["code"],
                auth_flow=payload.auth_flow,
                expires_in_minutes=settings.email_login_code_ttl_minutes,
            )
        except EmailDeliveryError as exc:
            logger.exception("Email login delivery failed for %s", challenge["email"])
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Không thể gửi mã đăng nhập qua email lúc này. Vui lòng thử lại sau ít phút.",
            ) from exc
        delivery_channel = "n8n_email"
        dev_login_code = None
        message = "Mã đăng nhập đã được gửi vào email của bạn. Vui lòng kiểm tra hộp thư để tiếp tục."

    return EmailStartResponse(
        message=message,
        delivery_channel=delivery_channel,
        expires_in_minutes=settings.email_login_code_ttl_minutes,
        email=challenge["email"],
        auth_flow=payload.auth_flow,
        dev_login_code=dev_login_code,
    )


@router.post("/email/verify", response_model=AuthResponse)
def email_verify(payload: EmailVerifyRequest) -> AuthResponse:
    challenge = consume_email_login_challenge(email=payload.email, code=payload.code)
    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã đăng nhập không hợp lệ hoặc đã hết hạn.",
        )

    user = get_user_by_email(payload.email)
    try:
        if user is None and challenge["auth_flow"] == "register":
            if not challenge.get("intended_role") or not challenge.get("intended_full_name"):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Thiếu thông tin để hoàn tất tạo tài khoản mới.",
                )
            user = create_user(
                email=payload.email,
                role=challenge["intended_role"],
                full_name=challenge["intended_full_name"],
                auth_preference="email_login",
                email_verified_at=challenge["consumed_at"],
            )
        elif user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy tài khoản phù hợp cho email này.",
            )
        else:
            user = update_user_email_verification(
                user_id=user["id"],
                verified_at=challenge["consumed_at"],
            )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Không thể hoàn tất đăng nhập email cho tài khoản này.",
        ) from exc

    response_user = serialize_user(user)
    return AuthResponse(
        access_token=create_access_token(str(user["id"]), {"role": user["role"]}),
        user=response_user,
    )


@router.get("/sso/{provider}/start", response_model=SsoStartResponse)
def sso_start(provider: str) -> SsoStartResponse:
    normalized_provider = provider.lower().strip()
    if normalized_provider not in SUPPORTED_SSO_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nhà cung cấp SSO chưa được hỗ trợ.")

    state = secrets.token_urlsafe(24)
    authorization_url = (
        f"{settings.frontend_base_url}/auth/sso?"
        + urlencode(
            {
                "provider": normalized_provider,
                "state": state,
                "redirect_uri": f"{settings.frontend_base_url}/auth/sso/{normalized_provider}/callback",
            }
        )
    )
    return SsoStartResponse(
        provider=normalized_provider,
        authorization_url=authorization_url,
        state=state,
        message="Hợp đồng điều hướng SSO đã sẵn sàng cho bước tích hợp provider thực tế.",
    )


@router.get("/sso/{provider}/callback", response_model=SsoCallbackResponse)
def sso_callback(
    provider: str,
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=8, max_length=255),
) -> SsoCallbackResponse:
    normalized_provider = provider.lower().strip()
    if normalized_provider not in SUPPORTED_SSO_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nhà cung cấp SSO chưa được hỗ trợ.")

    return SsoCallbackResponse(
        provider=normalized_provider,
        state=state,
        message=(
            "Callback SSO đã nhận đủ state và code. Bước đổi token với nhà cung cấp thực tế sẽ được nối vào pha tích hợp tiếp theo."
        ),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return serialize_user(current_user)

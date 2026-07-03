"""Authentication routes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
import logging
import secrets
from app.core.db import IntegrityError
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.responses import RedirectResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.models.enums import UserRole
from app.schemas.auth import (
    AuthResponse,
    EmailStartRequest,
    EmailStartResponse,
    EmailVerifyRequest,
    SsoStartResponse,
    UserResponse,
)
from app.services.email_delivery import EmailDeliveryError, send_email_login_code
from app.services.email_login import create_email_login_challenge, consume_email_login_challenge
from app.services.users import (
    ALLOWED_SELF_SERVICE_ROLES,
    create_user,
    get_user_by_email,
    update_user_auth,
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


def _build_frontend_sso_redirect(*, success: bool, message: str, token: str | None = None, user: dict | None = None) -> str:
    payload: dict[str, str] = {
        "success": "1" if success else "0",
        "message": message,
    }
    if token:
        payload["access_token"] = token
    if user:
        payload["user"] = json.dumps(serialize_user(user).model_dump(mode="json"), ensure_ascii=False)
    return f"{settings.frontend_base_url}/auth/sso?{urlencode(payload)}"


def _create_sso_state(
    *,
    provider: str,
    auth_flow: str,
    role: str | None,
    full_name: str | None,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    payload = {
        "provider": provider,
        "auth_flow": auth_flow,
        "role": role,
        "full_name": full_name,
        "nonce": secrets.token_urlsafe(16),
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _decode_sso_state(state: str) -> dict[str, str | None]:
    try:
        payload = jwt.decode(state, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Trạng thái SSO không hợp lệ hoặc đã hết hạn.",
        ) from exc
    return payload


def _normalize_provider(provider: str) -> str:
    normalized_provider = provider.lower().strip()
    if normalized_provider not in SUPPORTED_SSO_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nhà cung cấp SSO chưa được hỗ trợ.")
    return normalized_provider


def _provider_config(provider: str) -> dict[str, str]:
    if provider == "google":
        if not settings.google_client_id or not settings.google_client_secret or not settings.google_oauth_redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google SSO chưa được cấu hình đầy đủ trên máy chủ.",
            )
        return {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
            "scope": "openid email profile",
        }
    
    if provider == "linkedin":
        if (
            not settings.linkedin_client_id
            or not settings.linkedin_client_secret
            or not settings.linkedin_oauth_redirect_uri
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LinkedIn SSO chưa được cấu hình đầy đủ trên máy chủ.",
            )

        return {
            "client_id": settings.linkedin_client_id,
            "client_secret": settings.linkedin_client_secret,
            "redirect_uri": settings.linkedin_oauth_redirect_uri,
            "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
            "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
            "userinfo_url": "https://api.linkedin.com/v2/userinfo",
            "scope": "openid profile email",
        }

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"{provider.title()} SSO chưa được cấu hình trên máy chủ.",
    )


def _post_form(url: str, data: dict[str, str]) -> dict:
    encoded = urlencode(data).encode("utf-8")
    request = Request(url, data=encoded, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urlopen(request, timeout=settings.oauth_http_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logger.warning("OAuth token exchange failed: %s", body)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể hoàn tất xác thực với nhà cung cấp SSO lúc này.",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể kết nối tới nhà cung cấp SSO lúc này.",
        ) from exc


def _get_json(url: str, headers: dict[str, str]) -> dict:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=settings.oauth_http_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logger.warning("OAuth userinfo fetch failed: %s", body)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể lấy hồ sơ SSO từ nhà cung cấp lúc này.",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể kết nối tới nhà cung cấp SSO lúc này.",
        ) from exc


def _complete_google_sso(*, code: str) -> dict[str, str | None]:
    provider = _provider_config("google")
    token_payload = _post_form(
        provider["token_url"],
        {
            "code": code,
            "client_id": provider["client_id"],
            "client_secret": provider["client_secret"],
            "redirect_uri": provider["redirect_uri"],
            "grant_type": "authorization_code",
        },
    )
    access_token = token_payload.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nhà cung cấp SSO không trả về access token hợp lệ.",
        )

    profile = _get_json(provider["userinfo_url"], {"Authorization": f"Bearer {access_token}"})
    email = str(profile.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nhà cung cấp SSO không trả về email hợp lệ.",
        )

    full_name = str(profile.get("name") or "").strip() or None
    email_verified = bool(profile.get("email_verified"))
    return {
        "email": email,
        "full_name": full_name,
        "email_verified_at": datetime.now(UTC).isoformat() if email_verified else None,
    }

def _complete_linkedin_sso(*, code: str) -> dict[str, str | None]:
    provider = _provider_config("linkedin")
    token_payload = _post_form(
        provider["token_url"],
        {
            "code": code,
            "client_id": provider["client_id"],
            "client_secret": provider["client_secret"],
            "redirect_uri": provider["redirect_uri"],
            "grant_type": "authorization_code",
        },
    )

    access_token = token_payload.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nhà cung cấp SSO không trả về access token hợp lệ.",
        )

    profile = _get_json(provider["userinfo_url"], {"Authorization": f"Bearer {access_token}"})

    email = str(profile.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LinkedIn không trả về email hợp lệ.",
        )

    full_name = str(profile.get("name") or "").strip() or None

    return {
        "email": email,
        "full_name": full_name,
        "email_verified_at": datetime.now(UTC).isoformat(),
    }

def _complete_sso(provider: str, code: str) -> dict[str, str | None]:
    if provider == "google":
        return _complete_google_sso(code=code)
    
    if provider == "linkedin":
        return _complete_linkedin_sso(code=code)
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Nhà cung cấp SSO chưa được cấu hình.")


def _finalize_sso_user(*, provider: str, sso_identity: dict[str, str | None], state_payload: dict[str, str | None]) -> dict:
    email = str(sso_identity["email"])
    existing_user = get_user_by_email(email)
    verified_at = sso_identity.get("email_verified_at") or datetime.now(UTC).isoformat()
    auth_preference = f"{provider}_oauth"

    try:
        if existing_user is not None:
            return update_user_auth(
                user_id=existing_user["id"],
                auth_preference=auth_preference,
                email_verified_at=verified_at,
            )

        if state_payload.get("auth_flow") != "register":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email SSO này chưa có tài khoản. Vui lòng đăng ký trước.",
            )

        role = state_payload.get("role")
        full_name = state_payload.get("full_name") or sso_identity.get("full_name")
        if not role or not full_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Thiếu vai trò hoặc họ tên để hoàn tất đăng ký bằng SSO.",
            )
        if role not in ALLOWED_SELF_SERVICE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể tự tạo tài khoản nhà báo hoặc chuyên gia.",
            )

        return create_user(
            email=email,
            role=role,
            full_name=full_name,
            auth_preference=auth_preference,
            email_verified_at=verified_at,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Không thể hoàn tất đăng nhập SSO cho tài khoản này.",
        ) from exc


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
    except IntegrityError as exc:
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
def sso_start(
    provider: str,
    auth_flow: str = Query("login", pattern="^(login|register)$"),
    role: str | None = Query(default=None),
    full_name: str | None = Query(default=None, min_length=1, max_length=120),
) -> SsoStartResponse:
    normalized_provider = _normalize_provider(provider)
    provider_cfg = _provider_config(normalized_provider)

    if auth_flow == "register":
        if not role or not full_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cần chọn vai trò và nhập họ tên trước khi đăng ký bằng SSO.",
            )
        if role not in ALLOWED_SELF_SERVICE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể tự tạo tài khoản nhà báo hoặc chuyên gia.",
            )

    state = _create_sso_state(
        provider=normalized_provider,
        auth_flow=auth_flow,
        role=role,
        full_name=full_name,
    )
    authorization_url = provider_cfg["auth_url"] + "?" + urlencode(
        {
            "client_id": provider_cfg["client_id"],
            "redirect_uri": provider_cfg["redirect_uri"],
            "response_type": "code",
            "scope": provider_cfg["scope"],
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return SsoStartResponse(
        provider=normalized_provider,
        authorization_url=authorization_url,
        state=state,
        message="Đã tạo liên kết chuyển hướng SSO tới nhà cung cấp.",
    )


@router.get("/sso/{provider}/callback")
def sso_callback(
    provider: str,
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=8, max_length=4096),
) -> RedirectResponse:
    normalized_provider = _normalize_provider(provider)

    try:
        state_payload = _decode_sso_state(state)
        if state_payload.get("provider") != normalized_provider:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Trạng thái SSO không khớp với nhà cung cấp.",
            )
        sso_identity = _complete_sso(normalized_provider, code)
        user = _finalize_sso_user(provider=normalized_provider, sso_identity=sso_identity, state_payload=state_payload)
        access_token = create_access_token(str(user["id"]), {"role": user["role"]})
        redirect_url = _build_frontend_sso_redirect(
            success=True,
            message="Đăng nhập SSO thành công.",
            token=access_token,
            user=user,
        )
    except HTTPException as exc:
        redirect_url = _build_frontend_sso_redirect(success=False, message=exc.detail)

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return serialize_user(current_user)

"""Authentication routes."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.users import (
    ALLOWED_SELF_SERVICE_ROLES,
    create_user,
    ensure_email_available,
    get_user_by_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=UserRole(user["role"]),
        full_name=user.get("full_name"),
        verification_status=user["verification_status"],
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> AuthResponse:
    if payload.role.value not in ALLOWED_SELF_SERVICE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ có thể tự đăng ký vai trò nhà báo hoặc chuyên gia.",
        )

    try:
        ensure_email_available(payload.email)
        user = create_user(
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role.value,
            full_name=payload.full_name,
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được sử dụng.",
        ) from exc

    response_user = serialize_user(user)
    return AuthResponse(
        access_token=create_access_token(str(user["id"]), {"role": user["role"]}),
        user=response_user,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )

    response_user = serialize_user(user)
    return AuthResponse(
        access_token=create_access_token(str(user["id"]), {"role": user["role"]}),
        user=response_user,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return serialize_user(current_user)

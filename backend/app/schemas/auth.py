"""Request and response schemas for auth and shared user payloads."""
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole, VerificationStatus


class EmailStartRequest(BaseModel):
    email: EmailStr
    auth_flow: Literal["login", "register"] = "login"
    role: UserRole | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=120)


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=12)


class SsoCallbackRequest(BaseModel):
    code: str = Field(min_length=1)
    state: str = Field(min_length=8, max_length=255)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    full_name: str | None
    verification_status: VerificationStatus
    auth_preference: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class EmailStartResponse(BaseModel):
    message: str
    delivery_channel: str = "console_dev_code"
    expires_in_minutes: int
    email: EmailStr
    auth_flow: Literal["login", "register"]
    dev_login_code: str | None = None


class SsoStartResponse(BaseModel):
    provider: str
    authorization_url: str
    state: str
    message: str


class SsoCallbackResponse(BaseModel):
    provider: str
    message: str
    state: str
    callback_received: bool = True

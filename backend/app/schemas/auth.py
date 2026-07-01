"""Request and response schemas for auth and shared user payloads."""

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole, VerificationStatus


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
    full_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    full_name: str | None
    verification_status: VerificationStatus


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

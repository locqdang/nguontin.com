"""Profile schemas for role-aware profile endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class JournalistProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    outlet_name: str | None = Field(default=None, max_length=160)
    beat: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)
    region: str | None = Field(default=None, max_length=120)
    contact_note: str | None = Field(default=None, max_length=500)


class JournalistProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: str
    full_name: str
    outlet_name: str | None = None
    beat: str | None = None
    bio: str | None = None
    region: str | None = None
    contact_note: str | None = None


class ExpertProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    headline: str | None = Field(default=None, max_length=160)
    organization_name: str | None = Field(default=None, max_length=160)
    job_title: str | None = Field(default=None, max_length=160)
    specialties: list[str] = Field(default_factory=list, max_length=12)
    bio: str | None = Field(default=None, max_length=2000)
    region: str | None = Field(default=None, max_length=120)
    contact_note: str | None = Field(default=None, max_length=500)


class ExpertProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: str
    full_name: str
    headline: str | None = None
    organization_name: str | None = None
    job_title: str | None = None
    specialties: list[str] = Field(default_factory=list)
    bio: str | None = None
    region: str | None = None
    contact_note: str | None = None

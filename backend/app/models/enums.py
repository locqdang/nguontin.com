"""Shared enum values for NguonTin workflow state."""

from enum import StrEnum


class UserRole(StrEnum):
    JOURNALIST = "journalist"
    EXPERT = "expert"
    ADMIN = "admin"


class VerificationStatus(StrEnum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

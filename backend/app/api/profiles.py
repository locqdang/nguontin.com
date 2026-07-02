"""Profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.enums import UserRole
from app.schemas.profiles import JournalistProfileResponse, JournalistProfileUpdateRequest
from app.services.profiles import get_journalist_profile, upsert_journalist_profile

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/journalist", response_model=JournalistProfileResponse)
def get_my_journalist_profile(current_user: dict = Depends(get_current_user)) -> JournalistProfileResponse:
    if current_user["role"] != UserRole.JOURNALIST.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ tài khoản nhà báo mới có hồ sơ nhà báo.",
        )

    profile = get_journalist_profile(user_id=current_user["id"])
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ nhà báo của bạn chưa được tạo.",
        )

    return JournalistProfileResponse(**profile)


@router.patch("/journalist", response_model=JournalistProfileResponse)
def update_my_journalist_profile(
    payload: JournalistProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> JournalistProfileResponse:
    if current_user["role"] != UserRole.JOURNALIST.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ tài khoản nhà báo mới có thể cập nhật hồ sơ nhà báo.",
        )

    profile = upsert_journalist_profile(
        user_id=current_user["id"],
        full_name=payload.full_name,
        outlet_name=payload.outlet_name,
        beat=payload.beat,
        bio=payload.bio,
        region=payload.region,
        contact_note=payload.contact_note,
    )
    return JournalistProfileResponse(**profile)

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User, UserProfile
from ...schemas.user import UserOut, UserProfileOut, UserWithProfileOut, UserProfileUpdateRequest

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


@router.get("/me", response_model=UserWithProfileOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    return UserWithProfileOut(
        user=UserOut.model_validate(current_user),
        profile=UserProfileOut.model_validate(profile) if profile else None,
    )


@router.patch("/me/profile", response_model=UserProfileOut)
async def update_my_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return UserProfileOut.model_validate(profile)


@router.post("/me/profile/image", response_model=UserProfileOut)
async def upload_profile_image(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "فقط فایل‌های تصویری با فرمت jpeg، png یا webp مجاز هستند",
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "حجم فایل نباید بیشتر از ۵ مگابایت باشد",
        )

    extension = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[file.content_type]
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{extension}"

    upload_dir = Path(settings.UPLOAD_DIR) / "profile_images"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    image_url = f"/uploads/profile_images/{filename}"

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    profile.profile_image_url = image_url

    await db.commit()
    await db.refresh(profile)

    return UserProfileOut.model_validate(profile)
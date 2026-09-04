from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ...models.user import User
from ...schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    VerifyOtpRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    AccessTokenResponse,
    UserOut,
)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.phone_number == payload.phone_number))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "این شماره تماس قبلاً ثبت شده است")

    user = User(
        phone_number=payload.phone_number,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_active=False,  # تا وریفای OTP فعال نمی‌شود
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # TODO (Phase 2): تولید OTP واقعی و ارسال از طریق SMS provider،
    # مطابق Section G مستند معماری. فعلاً فقط کاربر غیرفعال ساخته می‌شود.
    return RegisterResponse(user_id=user.id, message="کد تایید برای شما ارسال خواهد شد (Phase 2)")


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    # TODO (Phase 2): پیاده‌سازی واقعی جدول OTP و بررسی انقضا (طبق Section G).
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "OTP verification not implemented yet — Phase 2",
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone_number == payload.phone_number))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "شماره تماس یا رمز عبور اشتباه است")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "حساب کاربری هنوز فعال نشده است")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    return AccessTokenResponse(access_token=create_access_token(data["sub"]))


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # JWT های stateless نیاز به blacklist سمت سرور دارند اگر invalidation فوری لازم باشد
    # (خارج از اسکلت فعلی).
    return {"success": True}

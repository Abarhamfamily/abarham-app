from datetime import datetime, timedelta, timezone

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
from ...models.otp import OtpCode, OtpPurpose
from ...models.user import User
from ...services.sms_provider import generate_otp_code, send_sms
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
    await db.flush()

    code = generate_otp_code()
    now = datetime.now(timezone.utc)
    otp = OtpCode(
        user_id=user.id,
        code=code,
        purpose=OtpPurpose.REGISTER.value,
        expires_at=now + timedelta(minutes=5),
        created_at=now,
    )
    db.add(otp)
    await db.commit()
    await db.refresh(user)

    send_sms(user.phone_number, f"کد تایید آبرهام: {code}")

    return RegisterResponse(
        user_id=user.id,
        message="کد تایید برای شما ارسال شد",
        otp_code=code,
    )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.phone_number == payload.phone_number))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "کاربری با این شماره یافت نشد")

    if user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "این حساب قبلاً فعال شده است")

    otp_result = await db.execute(
        select(OtpCode)
        .where(
            OtpCode.user_id == user.id,
            OtpCode.purpose == OtpPurpose.REGISTER.value,
            OtpCode.is_used == False,
        )
        .order_by(OtpCode.created_at.desc())
        .limit(1)
    )
    otp = otp_result.scalar_one_or_none()

    if not otp:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "کد تاییدی برای این کاربر یافت نشد")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if otp.expires_at < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "کد تایید منقضی شده است")

    if otp.attempts >= 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "تعداد تلاش‌های مجاز به پایان رسیده است")

    if otp.code != payload.otp:
        otp.attempts += 1
        await db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "کد تایید نادرست است")

    otp.is_used = True
    user.is_active = True
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user=UserOut.model_validate(user),
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

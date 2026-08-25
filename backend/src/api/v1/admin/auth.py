from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.security import verify_password, hash_password
from ....core.admin_security import (
    create_admin_access_token,
    create_admin_refresh_token,
    get_current_admin,
)
from ....core.security import decode_token
from ....models.admin import Admin
from ....schemas.admin_auth import (
    AdminLoginRequest,
    AdminTokenResponse,
    AdminRefreshRequest,
    AdminAccessTokenResponse,
    AdminOut,
    AdminChangePasswordRequest,
)

router = APIRouter()


@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.username == payload.username))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "نام کاربری یا رمز عبور اشتباه است")

    if not admin.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "حساب ادمین غیرفعال است")

    return AdminTokenResponse(
        access_token=create_admin_access_token(str(admin.id)),
        refresh_token=create_admin_refresh_token(str(admin.id)),
        admin=AdminOut.model_validate(admin),
    )


@router.post("/refresh", response_model=AdminAccessTokenResponse)
async def admin_refresh(payload: AdminRefreshRequest):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "admin_refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    return AdminAccessTokenResponse(access_token=create_admin_access_token(data["sub"]))


@router.post("/logout")
async def admin_logout(current_admin: Admin = Depends(get_current_admin)):
    return {"success": True}


@router.get("/me", response_model=AdminOut)
async def admin_me(current_admin: Admin = Depends(get_current_admin)):
    return AdminOut.model_validate(current_admin)


@router.post("/change-password")
async def change_password(
    payload: AdminChangePasswordRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_admin.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "رمز عبور فعلی اشتباه است")

    current_admin.password_hash = hash_password(payload.new_password)
    await db.commit()
    return {"success": True}

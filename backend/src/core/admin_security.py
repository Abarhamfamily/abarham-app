"""
احراز هویت پنل مدیریت — کاملاً مجزا از احراز هویت User App.

طراحی جداسازی:
  - جدول جداگانه (Admin، نه User).
  - نوع claim متفاوت در JWT: "admin_access" / "admin_refresh" به‌جای
    "access" / "refresh" کاربران عادی. یعنی حتی اگر توکن یک کاربر عادی به
    این endpoint ها ارسال شود، به دلیل عدم تطابق «type»، رد می‌شود؛ و
    برعکس، توکن ادمین هرگز در get_current_user (کاربران عادی) پذیرفته
    نمی‌شود.
  - هش پسورد از همان core.security.hash_password/verify_password استفاده
    می‌کند (فقط فراخوانی، بدون تغییر در آن فایل) تا منطق تکراری نشود.

این فایل جدید است و هیچ فایل موجودی را تغییر نمی‌دهد.
"""
from datetime import timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import create_token, decode_token
from ..core.config import settings
from ..models.admin import Admin

admin_bearer_scheme = HTTPBearer(auto_error=False)


def create_admin_access_token(admin_id: str) -> str:
    return create_token(
        admin_id,
        "admin_access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_admin_refresh_token(admin_id: str) -> str:
    return create_token(
        admin_id,
        "admin_refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Admin authentication required")

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "admin_access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired admin token")

    try:
        admin_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")

    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()

    if not admin or not admin.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Admin not found or inactive")

    return admin


def require_super_admin(admin: Admin = Depends(get_current_admin)) -> Admin:
    if admin.role != "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Super admin access required")
    return admin

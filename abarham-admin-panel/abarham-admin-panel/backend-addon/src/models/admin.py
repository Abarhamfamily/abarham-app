"""
مدل Admin کاملاً مستقل از User است — نه ارثی، نه مشترک با جدول users.
هدف: احراز هویت پنل مدیریت هیچ‌گاه نباید با احراز هویت User App تداخل
داشته باشد (نه در دیتابیس، نه در JWT، نه در dependency ها).

این فایل جدید است و هیچ فایل موجودی (از جمله src/models/user.py) را
تغییر نمی‌دهد.
"""
import enum

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base
from .common import TimestampMixin, UuidPkMixin


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT = "support"  # دسترسی محدودتر (فقط مشاهده)، در صورت نیاز در آینده اعمال شود


class Admin(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "admins"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=AdminRole.ADMIN.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

"""
مدل‌های دامنه (Domain) مستقل از ORM. این کلاس‌ها برای استفاده در لایه‌ی
Service و Schema هستند، نه برای نگاشت مستقیم به دیتابیس (که در models/ است).
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from uuid import UUID


@dataclass
class User:
    id: UUID
    phone_number: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    email: Optional[str] = None
    national_id: Optional[str] = None


@dataclass
class UserProfile:
    id: UUID
    user_id: UUID
    vehicle_has_capacity: bool = False
    empty_seats: int = 0
    birth_date: Optional[date] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None
    profile_image_url: Optional[str] = None
    national_id_image_url: Optional[str] = None

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminUserProfileOut(BaseModel):
    birth_date: Optional[date] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None
    vehicle_has_capacity: bool = False
    empty_seats: int = 0
    profile_image_url: Optional[str] = None
    national_id_image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminUserOut(BaseModel):
    id: UUID
    phone_number: str
    full_name: str
    email: Optional[str] = None
    national_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserDetailOut(AdminUserOut):
    profile: Optional[AdminUserProfileOut] = None


class AdminUserListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class AdminUserListResponse(BaseModel):
    data: list[AdminUserOut]
    meta: AdminUserListMeta


class AdminUserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

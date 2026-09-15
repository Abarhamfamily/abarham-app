from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserOut(BaseModel):
    id: UUID
    phone_number: str
    email: Optional[str] = None
    full_name: str
    national_id: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class UserProfileOut(BaseModel):
    birth_date: Optional[date] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None
    vehicle_has_capacity: bool = False
    empty_seats: int = 0
    profile_image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserWithProfileOut(BaseModel):
    user: UserOut
    profile: Optional[UserProfileOut] = None


class UserProfileUpdateRequest(BaseModel):
    birth_date: Optional[date] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None
    vehicle_has_capacity: Optional[bool] = None
    empty_seats: Optional[int] = None
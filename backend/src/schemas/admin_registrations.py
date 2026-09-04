from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminRegistrationOut(BaseModel):
    id: UUID
    user_id: UUID
    trip_id: UUID
    status: str
    total_price: Decimal
    deposit_paid: Decimal
    remaining_amount: Decimal
    passenger_count: int
    vehicle_type: Optional[str] = None
    empty_seats_provided: int
    notes: Optional[str] = None
    payment_deadline: Optional[datetime] = None
    registered_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # اطلاعات کمکی برای نمایش در جدول ادمین، بدون نیاز به join جداگانه در فرانت
    user_full_name: Optional[str] = None
    user_phone_number: Optional[str] = None
    trip_title: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminRegistrationListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class AdminRegistrationListResponse(BaseModel):
    data: list[AdminRegistrationOut]
    meta: AdminRegistrationListMeta


class AdminRegistrationUpdateRequest(BaseModel):
    status: str  # 'confirmed' | 'cancelled' | 'completed' | 'expired'
    notes: Optional[str] = None

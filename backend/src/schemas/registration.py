from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .waitlist import WaitlistOut


class RegistrationCreateRequest(BaseModel):
    trip_id: UUID
    passenger_count: int = 1
    vehicle_type: Optional[str] = None  # 'own' | 'other' | None
    empty_seats_provided: Optional[int] = 0
    notes: Optional[str] = None


class RegistrationOut(BaseModel):
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
    payment_deadline: Optional[datetime] = None
    registered_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaymentOut(BaseModel):
    id: UUID
    registration_id: UUID
    amount: Decimal
    type: str
    status: str

    model_config = {"from_attributes": True}


class RegistrationCreateResponse(BaseModel):
    registration: Optional[RegistrationOut] = None
    payment: Optional[PaymentOut] = None
    waitlist_entry: Optional[WaitlistOut] = None
    message: str


class SimpleMessageResponse(BaseModel):
    success: bool
    message: Optional[str] = None

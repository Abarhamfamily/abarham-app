import enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class RegistrationStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class VehicleType(str, enum.Enum):
    OWN = "own"
    OTHER = "other"
    NONE = "none"


@dataclass
class Registration:
    id: UUID
    user_id: UUID
    trip_id: UUID
    status: RegistrationStatus
    total_price: Decimal
    deposit_paid: Decimal
    remaining_amount: Decimal
    passenger_count: int
    registered_at: datetime
    payment_deadline: Optional[datetime] = None
    vehicle_type: Optional[VehicleType] = None
    empty_seats_provided: int = 0
    notes: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

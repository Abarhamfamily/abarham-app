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


def calculate_registration_price(
    trip_price: Decimal,
    other_vehicle_price: Decimal | None,
    vehicle_type: str | None,
    passenger_count: int,
) -> Decimal:
    """
    محاسبه‌ی قیمت کل ثبت‌نام بر اساس قیمت پایه‌ی تور، نوع وسیله نقلیه و تعداد مسافران.

    Raises:
        ValueError: اگر vehicle_type == 'other' باشد اما other_vehicle_price تعریف نشده باشد,
                    یا اگر passenger_count <= 0 باشد.
    """
    if passenger_count <= 0:
        raise ValueError("تعداد مسافران باید بزرگ‌تر از صفر باشد")

    if vehicle_type == "own":
        per_passenger = trip_price
    else:
        if other_vehicle_price is None:
            raise ValueError("هزینه‌ی ماشین سایر اعضا برای این تور تعریف نشده است")
        per_passenger = trip_price + other_vehicle_price

    return per_passenger * passenger_count

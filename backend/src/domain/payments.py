import enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class PaymentType(str, enum.Enum):
    DEPOSIT = "deposit"
    REMAINING = "remaining"
    FULL = "full"


class PaymentMethod(str, enum.Enum):
    WALLET = "wallet"
    ONLINE = "online"
    RECEIPT = "receipt"  # فیش بانکی دستی، مطابق ربات تلگرام فعلی


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


@dataclass
class Payment:
    id: UUID
    registration_id: UUID
    user_id: UUID
    amount: Decimal
    type: PaymentType
    status: PaymentStatus
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
    method: Optional[PaymentMethod] = None
    reference_code: Optional[str] = None
    receipt_url: Optional[str] = None
    confirmed_at: Optional[datetime] = None

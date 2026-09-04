import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from ..core.database import Base
from .common import TimestampMixin, UuidPkMixin


class PaymentType(str, enum.Enum):
    DEPOSIT = "deposit"
    REMAINING = "remaining"
    FULL = "full"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Payment(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )

    registration_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("registrations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=PaymentStatus.PENDING.value, nullable=False, index=True)
    method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    reference_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

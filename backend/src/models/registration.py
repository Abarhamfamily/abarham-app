import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from ..core.database import Base
from .common import TimestampMixin, UuidPkMixin


class RegistrationStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Registration(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "registrations"
    __table_args__ = (
        CheckConstraint("total_price >= 0", name="ck_registrations_total_price_non_negative"),
        CheckConstraint("deposit_paid >= 0", name="ck_registrations_deposit_paid_non_negative"),
        CheckConstraint("remaining_amount >= 0", name="ck_registrations_remaining_non_negative"),
        CheckConstraint("passenger_count > 0", name="ck_registrations_passenger_count_positive"),
        CheckConstraint("empty_seats_provided >= 0", name="ck_registrations_empty_seats_non_negative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default=RegistrationStatus.PENDING_PAYMENT.value, nullable=False
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    payment_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    passenger_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    empty_seats_provided: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

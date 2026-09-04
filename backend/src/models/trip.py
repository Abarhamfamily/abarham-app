import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, Numeric, CheckConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base
from .common import TimestampMixin, UuidPkMixin


class TripStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Trip(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_trips_price_non_negative"),
        CheckConstraint("deposit_amount >= 0", name="ck_trips_deposit_non_negative"),
        CheckConstraint("capacity > 0", name="ck_trips_capacity_positive"),
        CheckConstraint(
            "remaining_capacity >= 0 AND remaining_capacity <= capacity",
            name="ck_trips_remaining_capacity_bounds",
        ),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # optimistic locking
    status: Mapped[str] = mapped_column(String(50), default=TripStatus.PUBLISHED.value, nullable=False)
    transportation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accommodation_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_point: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    departure_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    cancellation_policy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

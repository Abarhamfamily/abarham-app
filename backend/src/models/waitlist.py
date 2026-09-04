import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from ..core.database import Base
from .common import TimestampMixin, UuidPkMixin


class WaitlistStatus(str, enum.Enum):
    WAITING = "waiting"
    NOTIFIED = "notified"
    EXPIRED = "expired"
    REGISTERED = "registered"


class Waitlist(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "waitlist"
    __table_args__ = (
        UniqueConstraint("user_id", "trip_id", name="uq_waitlist_user_trip"),
        CheckConstraint("position > 0", name="ck_waitlist_position_positive"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=WaitlistStatus.WAITING.value, nullable=False)
    notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

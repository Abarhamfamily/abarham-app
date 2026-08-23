import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from ..core.database import Base
from .common import TimestampMixin, UuidPkMixin


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    CREDIT_USAGE = "credit_usage"
    REFUND = "refund"
    GIFT_CREDIT = "gift_credit"
    FEE = "fee"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVERSED = "reversed"


class Wallet(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "wallets"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_wallets_user_id"),
        CheckConstraint("balance >= 0", name="ck_wallets_balance_non_negative"),
        CheckConstraint("pending_balance >= 0", name="ck_wallets_pending_balance_non_negative"),
        CheckConstraint("total_deposited >= 0", name="ck_wallets_total_deposited_non_negative"),
        CheckConstraint("total_withdrawn >= 0", name="ck_wallets_total_withdrawn_non_negative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    pending_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_deposited: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_withdrawn: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # optimistic locking


class Transaction(Base, UuidPkMixin):
    __tablename__ = "transactions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default=TransactionStatus.PENDING.value, nullable=False)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transaction_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

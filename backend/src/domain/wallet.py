import enum
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


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


@dataclass
class Wallet:
    id: UUID
    user_id: UUID
    balance: Decimal
    pending_balance: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal
    version: int
    created_at: datetime
    updated_at: datetime


@dataclass
class Transaction:
    id: UUID
    wallet_id: UUID
    amount: Decimal
    type: TransactionType
    status: TransactionStatus
    created_at: datetime
    reference_id: Optional[UUID] = None
    description: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    confirmed_at: Optional[datetime] = None

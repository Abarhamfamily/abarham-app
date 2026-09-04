from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminWalletOut(BaseModel):
    id: UUID
    user_id: UUID
    balance: Decimal
    pending_balance: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal

    user_full_name: Optional[str] = None
    user_phone_number: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminWalletListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class AdminWalletListResponse(BaseModel):
    data: list[AdminWalletOut]
    meta: AdminWalletListMeta


class AdminTransactionOut(BaseModel):
    id: UUID
    wallet_id: UUID
    amount: Decimal
    type: str
    status: str
    reference_id: Optional[UUID] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminWalletAdjustRequest(BaseModel):
    amount: Decimal  # مثبت = افزایش موجودی، منفی = کاهش موجودی
    description: str

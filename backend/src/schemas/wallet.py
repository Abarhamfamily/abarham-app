from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class WalletOut(BaseModel):
    id: UUID
    user_id: UUID
    balance: Decimal
    pending_balance: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    id: UUID
    wallet_id: UUID
    amount: Decimal
    type: str
    status: str
    reference_id: Optional[UUID] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletDepositRequest(BaseModel):
    amount: Decimal
    idempotency_key: str


class WalletWithdrawRequest(BaseModel):
    amount: Decimal
    idempotency_key: str


class WalletChargeRequest(BaseModel):
    amount: Decimal


class WalletChargeResponse(BaseModel):
    transaction_id: UUID
    payment_url: str
    authority: str


class WalletChargeVerifyResponse(BaseModel):
    success: bool
    message: str
    wallet: Optional[WalletOut] = None

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PaymentCreateRequest(BaseModel):
    registration_id: UUID
    amount: Decimal
    idempotency_key: str
    method: str = "online"  # 'wallet' | 'online'


class PaymentOut(BaseModel):
    id: UUID
    registration_id: UUID
    amount: Decimal
    type: str
    status: str
    method: Optional[str] = None
    reference_code: Optional[str] = None
    receipt_url: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    idempotency_key: str

    model_config = {"from_attributes": True}


class PaymentCreateResponse(BaseModel):
    payment: PaymentOut
    status: str


class UploadReceiptResponse(BaseModel):
    receipt_url: str


class ConfirmPaymentRequest(BaseModel):
    reference_code: Optional[str] = None

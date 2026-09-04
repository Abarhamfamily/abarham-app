from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminPaymentOut(BaseModel):
    id: UUID
    registration_id: UUID
    user_id: UUID
    amount: Decimal
    type: str
    status: str
    method: Optional[str] = None
    reference_code: Optional[str] = None
    receipt_url: Optional[str] = None
    description: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime

    user_full_name: Optional[str] = None
    user_phone_number: Optional[str] = None
    trip_title: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminPaymentListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class AdminPaymentListResponse(BaseModel):
    data: list[AdminPaymentOut]
    meta: AdminPaymentListMeta


class AdminPaymentConfirmRequest(BaseModel):
    reference_code: Optional[str] = None


class AdminPaymentRejectRequest(BaseModel):
    reason: Optional[str] = None

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminTripOut(BaseModel):
    id: UUID
    title: str
    destination: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    price: Decimal
    deposit_amount: Decimal
    capacity: int
    remaining_capacity: int
    version: int
    status: str
    transportation_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    accommodation_info: Optional[str] = None
    meeting_point: Optional[str] = None
    departure_time: Optional[str] = None
    requirements: Optional[dict] = None
    rules: Optional[dict] = None
    cancellation_policy: Optional[str] = None
    image_urls: Optional[list] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminTripListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class AdminTripListResponse(BaseModel):
    data: list[AdminTripOut]
    meta: AdminTripListMeta


class AdminTripCreateRequest(BaseModel):
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    price: Decimal
    deposit_amount: Decimal
    capacity: int
    status: str = "draft"
    description: Optional[str] = None
    transportation_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    accommodation_info: Optional[str] = None
    meeting_point: Optional[str] = None
    departure_time: Optional[str] = None
    requirements: Optional[dict] = None
    rules: Optional[dict] = None
    cancellation_policy: Optional[str] = None
    image_urls: Optional[list] = None


class AdminTripUpdateRequest(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    price: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    transportation_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    accommodation_info: Optional[str] = None
    meeting_point: Optional[str] = None
    departure_time: Optional[str] = None
    requirements: Optional[dict] = None
    rules: Optional[dict] = None
    cancellation_policy: Optional[str] = None
    image_urls: Optional[list] = None

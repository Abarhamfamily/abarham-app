from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TripOut(BaseModel):
    id: UUID
    title: str
    destination: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    price: Decimal
    deposit_amount: Decimal
    other_vehicle_price: Optional[Decimal] = None
    capacity: int
    remaining_capacity: int
    status: str
    transportation_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    meeting_point: Optional[str] = None
    departure_time: Optional[str] = None

    model_config = {"from_attributes": True}


class TripListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class TripListResponse(BaseModel):
    data: list[TripOut]
    meta: TripListMeta


class TripAvailabilityResponse(BaseModel):
    total_capacity: int
    remaining_capacity: int
    waitlist_count: int

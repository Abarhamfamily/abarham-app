import enum
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class TripStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Trip:
    id: UUID
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    price: Decimal
    deposit_amount: Decimal
    capacity: int
    remaining_capacity: int
    version: int
    status: TripStatus
    description: Optional[str] = None
    transportation_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    accommodation_info: Optional[str] = None
    meeting_point: Optional[str] = None
    departure_time: Optional[str] = None
    requirements: Optional[dict] = None
    rules: Optional[dict] = None
    cancellation_policy: Optional[str] = None
    image_urls: Optional[list] = field(default_factory=list)

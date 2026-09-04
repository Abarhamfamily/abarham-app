import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


class WaitlistStatus(str, enum.Enum):
    WAITING = "waiting"
    NOTIFIED = "notified"
    EXPIRED = "expired"
    REGISTERED = "registered"


@dataclass
class Waitlist:
    id: UUID
    user_id: UUID
    trip_id: UUID
    position: int
    status: WaitlistStatus
    created_at: datetime
    notified_at: Optional[datetime] = None

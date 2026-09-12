from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class WaitlistOut(BaseModel):
    id: UUID
    user_id: UUID
    trip_id: UUID
    position: int
    status: str
    notified_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
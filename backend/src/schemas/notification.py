from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: UUID
    type: str
    title: str
    content: str
    data: Optional[dict] = None
    read_at: Optional[datetime] = None
    sent_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    count: int


class SimpleSuccessResponse(BaseModel):
    success: bool

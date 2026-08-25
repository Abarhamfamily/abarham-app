from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdminNotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    content: str
    data: Optional[dict] = None
    read_at: Optional[datetime] = None
    sent_at: datetime

    user_full_name: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminNotificationListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class AdminNotificationListResponse(BaseModel):
    data: list[AdminNotificationOut]
    meta: AdminNotificationListMeta


class AdminNotificationCreateRequest(BaseModel):
    title: str
    content: str
    type: str = "admin_message"
    user_id: Optional[UUID] = None  # اگر خالی باشد و all_active_users=True باشد، برای همه ارسال می‌شود
    all_active_users: bool = False
    data: Optional[dict] = None


class AdminNotificationCreateResponse(BaseModel):
    created_count: int

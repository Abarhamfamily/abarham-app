from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.admin_security import get_current_admin
from ....models.admin import Admin
from ....models.user import User
from ....models.notification import Notification
from ....schemas.admin_notifications import (
    AdminNotificationOut,
    AdminNotificationListResponse,
    AdminNotificationListMeta,
    AdminNotificationCreateRequest,
    AdminNotificationCreateResponse,
)

router = APIRouter()


@router.get("", response_model=AdminNotificationListResponse)
async def list_notifications(
    user_id: Optional[UUID] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification, User).join(User, Notification.user_id == User.id)
    count_query = select(func.count()).select_from(Notification)

    if user_id:
        query = query.where(Notification.user_id == user_id)
        count_query = count_query.where(Notification.user_id == user_id)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.order_by(Notification.sent_at.desc()).limit(limit).offset(offset))
    rows = result.all()

    data = []
    for notification, user in rows:
        out = AdminNotificationOut.model_validate(notification)
        out.user_full_name = user.full_name
        data.append(out)

    return AdminNotificationListResponse(
        data=data,
        meta=AdminNotificationListMeta(total=total, limit=limit, offset=offset),
    )


@router.post("", response_model=AdminNotificationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: AdminNotificationCreateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not payload.all_active_users and not payload.user_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "باید یا user_id مشخص شود یا all_active_users=true باشد",
        )

    target_user_ids: list[UUID] = []

    if payload.all_active_users:
        result = await db.execute(select(User.id).where(User.is_active.is_(True)))
        target_user_ids = [row[0] for row in result.all()]
    else:
        user = await db.get(User, payload.user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "کاربر یافت نشد")
        target_user_ids = [user.id]

    now = datetime.now(timezone.utc)
    notifications = [
        Notification(
            user_id=uid,
            type=payload.type,
            title=payload.title,
            content=payload.content,
            data=payload.data,
            sent_at=now,
        )
        for uid in target_user_ids
    ]
    db.add_all(notifications)
    await db.commit()

    return AdminNotificationCreateResponse(created_count=len(notifications))

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.notification import Notification
from ...schemas.notification import NotificationOut, UnreadCountResponse, SimpleSuccessResponse

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    read: bool | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if read is True:
        query = query.where(Notification.read_at.is_not(None))
    elif read is False:
        query = query.where(Notification.read_at.is_(None))

    result = await db.execute(
        query.order_by(Notification.sent_at.desc()).limit(limit).offset(offset)
    )
    return [NotificationOut.model_validate(n) for n in result.scalars().all()]


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = (
        await db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == current_user.id, Notification.read_at.is_(None))
        )
    ).scalar_one()
    return UnreadCountResponse(count=count)


@router.put("/{notification_id}/read", response_model=SimpleSuccessResponse)
async def mark_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notification = await db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "اعلان یافت نشد")

    if notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
        await db.commit()

    return SimpleSuccessResponse(success=True)


@router.put("/read-all", response_model=SimpleSuccessResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return SimpleSuccessResponse(success=True)

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
from ....models.trip import Trip
from ....models.registration import Registration, RegistrationStatus
from ....schemas.admin_registrations import (
    AdminRegistrationOut,
    AdminRegistrationListResponse,
    AdminRegistrationListMeta,
    AdminRegistrationUpdateRequest,
)

router = APIRouter()

VALID_STATUSES = {s.value for s in RegistrationStatus}


def _to_out(registration: Registration, user: Optional[User], trip: Optional[Trip]) -> AdminRegistrationOut:
    out = AdminRegistrationOut.model_validate(registration)
    out.user_full_name = user.full_name if user else None
    out.user_phone_number = user.phone_number if user else None
    out.trip_title = trip.title if trip else None
    return out


@router.get("", response_model=AdminRegistrationListResponse)
async def list_registrations(
    status_filter: Optional[str] = Query(None, alias="status"),
    trip_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Registration, User, Trip).join(User, Registration.user_id == User.id).join(
        Trip, Registration.trip_id == Trip.id
    )
    count_query = select(func.count()).select_from(Registration)

    if status_filter:
        query = query.where(Registration.status == status_filter)
        count_query = count_query.where(Registration.status == status_filter)
    if trip_id:
        query = query.where(Registration.trip_id == trip_id)
        count_query = count_query.where(Registration.trip_id == trip_id)
    if user_id:
        query = query.where(Registration.user_id == user_id)
        count_query = count_query.where(Registration.user_id == user_id)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(
        query.order_by(Registration.registered_at.desc()).limit(limit).offset(offset)
    )
    rows = result.all()

    return AdminRegistrationListResponse(
        data=[_to_out(reg, user, trip) for reg, user, trip in rows],
        meta=AdminRegistrationListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{registration_id}", response_model=AdminRegistrationOut)
async def get_registration(
    registration_id: UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    registration = await db.get(Registration, registration_id)
    if not registration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام یافت نشد")

    user = await db.get(User, registration.user_id)
    trip = await db.get(Trip, registration.trip_id)
    return _to_out(registration, user, trip)


@router.patch("/{registration_id}", response_model=AdminRegistrationOut)
async def update_registration_status(
    registration_id: UUID,
    payload: AdminRegistrationUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"وضعیت نامعتبر. مقادیر مجاز: {', '.join(sorted(VALID_STATUSES))}",
        )

    registration = await db.get(Registration, registration_id)
    if not registration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام یافت نشد")

    previous_status = registration.status
    registration.status = payload.status
    if payload.notes is not None:
        registration.notes = payload.notes

    now = datetime.now(timezone.utc)
    if payload.status == RegistrationStatus.CONFIRMED.value and previous_status != RegistrationStatus.CONFIRMED.value:
        registration.confirmed_at = now
    if payload.status == RegistrationStatus.CANCELLED.value and previous_status != RegistrationStatus.CANCELLED.value:
        registration.cancelled_at = now
        # نکته: در این اسکلت، آزادسازی خودکار ظرفیت تور (remaining_capacity)
        # پیاده‌سازی نشده چون منطق رزرو ظرفیت هنوز در Phase 4 کاربر است
        # (به TODO در src/api/v1/registrations.py مراجعه کنید). اگر لغو یک
        # ثبت‌نام باید ظرفیت را دستی آزاد کند، این مقدار را جداگانه در تور
        # ویرایش کنید.

    await db.commit()
    await db.refresh(registration)

    user = await db.get(User, registration.user_id)
    trip = await db.get(Trip, registration.trip_id)
    return _to_out(registration, user, trip)

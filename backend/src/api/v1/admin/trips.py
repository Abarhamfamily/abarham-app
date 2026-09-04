from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.admin_security import get_current_admin
from ....models.admin import Admin
from ....models.trip import Trip
from ....models.registration import Registration
from ....schemas.admin_trips import (
    AdminTripOut,
    AdminTripListResponse,
    AdminTripListMeta,
    AdminTripCreateRequest,
    AdminTripUpdateRequest,
)

router = APIRouter()


@router.get("", response_model=AdminTripListResponse)
async def list_trips(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None, description="جست‌وجو در عنوان یا مقصد"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Trip)
    count_query = select(func.count()).select_from(Trip)

    if status_filter:
        query = query.where(Trip.status == status_filter)
        count_query = count_query.where(Trip.status == status_filter)

    if search:
        pattern = f"%{search}%"
        condition = Trip.title.ilike(pattern) | Trip.destination.ilike(pattern)
        query = query.where(condition)
        count_query = count_query.where(condition)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.order_by(Trip.start_date.desc()).limit(limit).offset(offset))
    trips = result.scalars().all()

    return AdminTripListResponse(
        data=[AdminTripOut.model_validate(t) for t in trips],
        meta=AdminTripListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{trip_id}", response_model=AdminTripOut)
async def get_trip(
    trip_id: UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تور یافت نشد")
    return AdminTripOut.model_validate(trip)


@router.post("", response_model=AdminTripOut, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: AdminTripCreateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if payload.end_date <= payload.start_date:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "تاریخ پایان باید بعد از تاریخ شروع باشد")

    data = payload.model_dump()
    trip = Trip(**data, remaining_capacity=payload.capacity, version=1)
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return AdminTripOut.model_validate(trip)


@router.put("/{trip_id}", response_model=AdminTripOut)
async def update_trip(
    trip_id: UUID,
    payload: AdminTripUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تور یافت نشد")

    data = payload.model_dump(exclude_unset=True)

    if "capacity" in data and data["capacity"] is not None:
        new_capacity = data["capacity"]
        already_taken = trip.capacity - trip.remaining_capacity
        if new_capacity < already_taken:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"ظرفیت جدید نمی‌تواند کمتر از تعداد نفرات ثبت‌نام‌شده‌ی فعلی ({already_taken}) باشد",
            )
        trip.remaining_capacity = new_capacity - already_taken

    for key, value in data.items():
        setattr(trip, key, value)

    trip.version += 1  # هماهنگ با استراتژی optimistic locking مستند معماری

    await db.commit()
    await db.refresh(trip)
    return AdminTripOut.model_validate(trip)


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تور یافت نشد")

    # نکته‌ی مهم: SQLite (دیتابیس Development این پروژه) به‌صورت پیش‌فرض
    # foreign key constraint ها را enforce نمی‌کند، پس نمی‌توان صرفاً به
    # IntegrityError دیتابیس تکیه کرد (روی PostgreSQL/Production کار
    # می‌کرد، ولی روی SQLite دور می‌زد و رکورد یتیم Registration باقی
    # می‌گذاشت). به همین دلیل این بررسی را صریحاً در لایه‌ی اپلیکیشن انجام
    # می‌دهیم تا رفتار روی هر دو دیتابیس یکسان و قابل‌اعتماد باشد.
    registration_count = (
        await db.execute(
            select(func.count()).select_from(Registration).where(Registration.trip_id == trip_id)
        )
    ).scalar_one()

    if registration_count > 0:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "این تور دارای ثبت‌نام است و قابل حذف نیست (به‌جای حذف، وضعیت را به 'cancelled' تغییر دهید)",
        )

    try:
        await db.delete(trip)
        await db.commit()
    except IntegrityError:
        # لایه‌ی محافظ دوم، برای هر محدودیت دیگری که ممکن است در آینده
        # اضافه شود (مثلاً روی PostgreSQL که FK واقعاً enforce می‌شود).
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "این تور به دلیل وابستگی به رکوردهای دیگر قابل حذف نیست",
        )

    return {"success": True}

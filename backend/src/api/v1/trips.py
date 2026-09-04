from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models.trip import Trip
from ...models.waitlist import Waitlist, WaitlistStatus
from ...schemas.trip import TripOut, TripListResponse, TripListMeta, TripAvailabilityResponse

router = APIRouter()


@router.get("", response_model=TripListResponse)
async def list_trips(
    status_filter: Optional[str] = Query(None, alias="status"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Trip)
    count_query = select(func.count()).select_from(Trip)

    if status_filter:
        query = query.where(Trip.status == status_filter)
        count_query = count_query.where(Trip.status == status_filter)
    if from_date:
        query = query.where(Trip.start_date >= from_date)
        count_query = count_query.where(Trip.start_date >= from_date)
    if to_date:
        query = query.where(Trip.start_date <= to_date)
        count_query = count_query.where(Trip.start_date <= to_date)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.order_by(Trip.start_date).limit(limit).offset(offset))
    trips = result.scalars().all()

    return TripListResponse(
        data=[TripOut.model_validate(t) for t in trips],
        meta=TripListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{trip_id}", response_model=TripOut)
async def get_trip(trip_id: UUID, db: AsyncSession = Depends(get_db)):
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تور یافت نشد")
    return TripOut.model_validate(trip)


@router.get("/{trip_id}/availability", response_model=TripAvailabilityResponse)
async def get_trip_availability(trip_id: UUID, db: AsyncSession = Depends(get_db)):
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تور یافت نشد")

    waitlist_count = (
        await db.execute(
            select(func.count())
            .select_from(Waitlist)
            .where(Waitlist.trip_id == trip_id, Waitlist.status == WaitlistStatus.WAITING.value)
        )
    ).scalar_one()

    return TripAvailabilityResponse(
        total_capacity=trip.capacity,
        remaining_capacity=trip.remaining_capacity,
        waitlist_count=waitlist_count,
    )

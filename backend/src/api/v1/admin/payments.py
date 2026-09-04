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
from ....models.payment import Payment, PaymentStatus
from ....schemas.admin_payments import (
    AdminPaymentOut,
    AdminPaymentListResponse,
    AdminPaymentListMeta,
    AdminPaymentConfirmRequest,
    AdminPaymentRejectRequest,
)

router = APIRouter()


def _to_out(payment: Payment, user: Optional[User], trip_title: Optional[str]) -> AdminPaymentOut:
    out = AdminPaymentOut.model_validate(payment)
    out.user_full_name = user.full_name if user else None
    out.user_phone_number = user.phone_number if user else None
    out.trip_title = trip_title
    return out


@router.get("", response_model=AdminPaymentListResponse)
async def list_payments(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Payment, User, Trip.title)
        .join(User, Payment.user_id == User.id)
        .join(Registration, Payment.registration_id == Registration.id)
        .join(Trip, Registration.trip_id == Trip.id)
    )
    count_query = select(func.count()).select_from(Payment)

    if status_filter:
        query = query.where(Payment.status == status_filter)
        count_query = count_query.where(Payment.status == status_filter)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.order_by(Payment.created_at.desc()).limit(limit).offset(offset))
    rows = result.all()

    return AdminPaymentListResponse(
        data=[_to_out(payment, user, trip_title) for payment, user, trip_title in rows],
        meta=AdminPaymentListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{payment_id}", response_model=AdminPaymentOut)
async def get_payment(
    payment_id: UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "پرداخت یافت نشد")

    user = await db.get(User, payment.user_id)
    registration = await db.get(Registration, payment.registration_id)
    trip = await db.get(Trip, registration.trip_id) if registration else None
    return _to_out(payment, user, trip.title if trip else None)


@router.post("/{payment_id}/confirm", response_model=AdminPaymentOut)
async def confirm_payment(
    payment_id: UUID,
    payload: AdminPaymentConfirmRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "پرداخت یافت نشد")

    if payment.status != PaymentStatus.PENDING.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "فقط پرداخت‌های در انتظار بررسی قابل تأیید هستند")

    registration = await db.get(Registration, payment.registration_id)
    if not registration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام مرتبط یافت نشد")

    now = datetime.now(timezone.utc)

    # طبق Section H مستند معماری: Payment Isolation — این پرداخت فقط روی
    # همین Registration اثر می‌گذارد.
    payment.status = PaymentStatus.CONFIRMED.value
    payment.confirmed_at = now
    if payload.reference_code:
        payment.reference_code = payload.reference_code

    registration.deposit_paid = registration.deposit_paid + payment.amount
    registration.remaining_amount = max(registration.total_price - registration.deposit_paid, 0)
    if registration.deposit_paid >= registration.total_price:
        registration.status = RegistrationStatus.CONFIRMED.value
        registration.confirmed_at = now

    await db.commit()
    await db.refresh(payment)

    user = await db.get(User, payment.user_id)
    trip = await db.get(Trip, registration.trip_id)
    return _to_out(payment, user, trip.title if trip else None)


@router.post("/{payment_id}/reject", response_model=AdminPaymentOut)
async def reject_payment(
    payment_id: UUID,
    payload: AdminPaymentRejectRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "پرداخت یافت نشد")

    if payment.status != PaymentStatus.PENDING.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "فقط پرداخت‌های در انتظار بررسی قابل رد شدن هستند")

    payment.status = PaymentStatus.FAILED.value
    if payload.reason:
        payment.description = payload.reason

    await db.commit()
    await db.refresh(payment)

    user = await db.get(User, payment.user_id)
    registration = await db.get(Registration, payment.registration_id)
    trip = await db.get(Trip, registration.trip_id) if registration else None
    return _to_out(payment, user, trip.title if trip else None)

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...domain.registrations import calculate_registration_price
from ...models.trip import Trip
from ...models.user import User
from ...models.registration import Registration, RegistrationStatus
from ...models.waitlist import Waitlist, WaitlistStatus
from ...models.wallet import Wallet
from ...schemas.registration import (
    RegistrationCreateRequest,
    RegistrationCreateResponse,
    RegistrationOut,
    RegistrationWithTripOut,
    PaymentOut,
)
from ...schemas.waitlist import WaitlistOut
from ...services.trip_capacity import try_decrement_trip_capacity, try_increment_trip_capacity
from ...services.wallet_balance import try_decrement_wallet_balance, try_increment_wallet_balance
from ...models.notification import Notification
from ...schemas.registration import SimpleMessageResponse
from ...services.payment_idempotency import get_or_create_deposit_payment

router = APIRouter()


@router.post("", response_model=RegistrationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    payload: RegistrationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # مرحله ۱ - پیدا کردن تور
    trip = await db.get(Trip, payload.trip_id)
    if not trip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تور یافت نشد")

    try:
        # مرحله ۲ - جلوگیری از ثبت‌نام تکراری
        existing_registration = await db.execute(
            select(Registration).where(
                Registration.user_id == current_user.id,
                Registration.trip_id == trip.id,
            )
        )
        if existing_registration.scalar_one_or_none() is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "شما قبلاً برای این تور ثبت‌نام کرده‌اید"
            )

        # مرحله ۳ - محاسبه قیمت
        try:
            calculated_price = calculate_registration_price(
                trip_price=trip.price,
                other_vehicle_price=trip.other_vehicle_price,
                vehicle_type=payload.vehicle_type,
                passenger_count=payload.passenger_count,
            )
        except ValueError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

        # مرحله ۴ - بررسی و کاهش موجودی کیف پول
        wallet_result = await db.execute(
            select(Wallet).where(Wallet.user_id == current_user.id)
        )
        wallet = wallet_result.scalar_one_or_none()
        if not wallet:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "کیف پول یافت نشد")

        wallet_decremented = await try_decrement_wallet_balance(
            db=db,
            user_id=current_user.id,
            current_version=wallet.version,
            amount=trip.deposit_amount,
        )
        if not wallet_decremented:
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED, "موجودی کیف پول کافی نیست"
            )

        # مرحله ۵ - تلاش برای کاهش ظرفیت تور
        capacity_decremented = await try_decrement_trip_capacity(
            db=db,
            trip_id=trip.id,
            current_version=trip.version,
            passenger_count=payload.passenger_count,
        )

        if capacity_decremented:
            registration = Registration(
                user_id=current_user.id,
                trip_id=trip.id,
                status=RegistrationStatus.PENDING_PAYMENT.value,
                total_price=calculated_price,
                deposit_paid=Decimal("0"),
                remaining_amount=calculated_price,
                passenger_count=payload.passenger_count,
                vehicle_type=payload.vehicle_type,
                empty_seats_provided=payload.empty_seats_provided or 0,
                notes=payload.notes,
                registered_at=datetime.now(timezone.utc),
            )
            db.add(registration)
            await db.flush()

            payment, _ = await get_or_create_deposit_payment(
                db=db,
                registration_id=registration.id,
                user_id=current_user.id,
                amount=trip.deposit_amount,
            )

            await db.commit()
            await db.refresh(registration)
            await db.refresh(payment)

            return RegistrationCreateResponse(
                registration=RegistrationOut.model_validate(registration),
                payment=PaymentOut.model_validate(payment),
                waitlist_entry=None,
                message="ثبت‌نام با موفقیت انجام شد",
            )
        else:
            existing_waitlist = await db.execute(
                select(Waitlist).where(
                    Waitlist.user_id == current_user.id,
                    Waitlist.trip_id == trip.id,
                )
            )
            if existing_waitlist.scalar_one_or_none() is not None:
                await db.execute(
                    update(Wallet).where(Wallet.user_id == current_user.id).values(
                        balance=Wallet.balance + trip.deposit_amount, version=Wallet.version + 1
                    )
                )
                await db.commit()
                raise HTTPException(
                    status.HTTP_409_CONFLICT, "شما قبلاً در لیست انتظار این تور هستید"
                )

            waitlist_count_result = await db.execute(
                select(Waitlist).where(Waitlist.trip_id == trip.id)
            )
            position = len(waitlist_count_result.scalars().all()) + 1

            waitlist_entry = Waitlist(
                user_id=current_user.id,
                trip_id=trip.id,
                position=position,
                status=WaitlistStatus.WAITING.value,
            )
            db.add(waitlist_entry)

            await db.execute(
                update(Wallet).where(Wallet.user_id == current_user.id).values(
                    balance=Wallet.balance + trip.deposit_amount, version=Wallet.version + 1
                )
            )

            await db.commit()
            await db.refresh(waitlist_entry)

            return RegistrationCreateResponse(
                registration=None,
                payment=None,
                waitlist_entry=WaitlistOut.model_validate(waitlist_entry),
                message="ظرفیت تور تکمیل است؛ شما به لیست انتظار اضافه شدید",
            )

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "خطای داخلی سرور در پردازش ثبت‌نام",
        )


@router.get("/my", response_model=list[RegistrationWithTripOut])
async def list_my_registrations(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Registration, Trip.title, Trip.destination)
        .join(Trip, Registration.trip_id == Trip.id)
        .where(Registration.user_id == current_user.id)
    )
    if status_filter:
        query = query.where(Registration.status == status_filter)

    result = await db.execute(query.order_by(Registration.registered_at.desc()))
    rows = result.all()

    return [
        RegistrationWithTripOut(
            id=reg.id,
            trip_id=reg.trip_id,
            trip_title=trip_title,
            trip_destination=trip_destination,
            status=reg.status,
            total_price=reg.total_price,
            deposit_paid=reg.deposit_paid,
            remaining_amount=reg.remaining_amount,
            passenger_count=reg.passenger_count,
            vehicle_type=reg.vehicle_type,
            registered_at=reg.registered_at,
        )
        for reg, trip_title, trip_destination in rows
    ]


@router.get("/{registration_id}", response_model=RegistrationOut)
async def get_registration(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    registration = await db.get(Registration, registration_id)
    if not registration or registration.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام یافت نشد")
    return RegistrationOut.model_validate(registration)


@router.delete("/{registration_id}")
async def cancel_registration(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    registration = await db.get(Registration, registration_id)
    if not registration or registration.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام یافت نشد")

    if registration.status == RegistrationStatus.CANCELLED.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "این ثبت‌نام قبلاً لغو شده است")

    try:
        trip = await db.get(Trip, registration.trip_id)
        if not trip:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "تور مرتبط یافت نشد")

        if registration.deposit_paid > 0:
            incremented = await try_increment_wallet_balance(
                db=db,
                user_id=current_user.id,
                current_version=(
                    await db.execute(
                        select(Wallet).where(Wallet.user_id == current_user.id)
                    )
                ).scalar_one().version,
                amount=registration.deposit_paid,
            )
            if not incremented:
                await db.rollback()
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "خطا در بازگشت وجه به کیف پول، لطفاً دوباره تلاش کنید",
                )

        capacity_released = await try_increment_trip_capacity(
            db=db,
            trip_id=trip.id,
            current_version=trip.version,
            passenger_count=registration.passenger_count,
        )
        if not capacity_released:
            await db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "خطا در آزادسازی ظرفیت تور، لطفاً دوباره تلاش کنید",
            )

        registration.status = RegistrationStatus.CANCELLED.value
        registration.cancelled_at = datetime.now(timezone.utc)

        waitlist_result = await db.execute(
            select(Waitlist)
            .where(
                Waitlist.trip_id == trip.id,
                Waitlist.status == WaitlistStatus.WAITING.value,
            )
            .order_by(Waitlist.position.asc())
            .limit(1)
        )
        first_waiting = waitlist_result.scalar_one_or_none()

        if first_waiting:
            first_waiting.status = WaitlistStatus.NOTIFIED.value
            first_waiting.notified_at = datetime.now(timezone.utc)

            notification = Notification(
                user_id=first_waiting.user_id,
                type="waitlist_spot_available",
                title="ظرفیت خالی شد",
                content=f"یک جای خالی برای تور «{trip.title}» ایجاد شده است. می‌توانید اکنون ثبت‌نام کنید.",
                data={"trip_id": str(trip.id)},
            )
            db.add(notification)

        await db.commit()

        return SimpleMessageResponse(success=True, message="ثبت‌نام با موفقیت لغو شد")

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "خطای داخلی سرور در پردازش لغو ثبت‌نام",
        )

from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.admin_security import get_current_admin
from ....models.admin import Admin
from ....models.user import User
from ....models.trip import Trip, TripStatus
from ....models.registration import Registration, RegistrationStatus
from ....models.payment import Payment, PaymentStatus
from ....models.wallet import Wallet
from ....models.notification import Notification
from ....schemas.admin_dashboard import DashboardStats

router = APIRouter()


@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    active_users = (
        await db.execute(select(func.count()).select_from(User).where(User.is_active.is_(True)))
    ).scalar_one()

    total_trips = (await db.execute(select(func.count()).select_from(Trip))).scalar_one()
    published_trips = (
        await db.execute(
            select(func.count()).select_from(Trip).where(Trip.status == TripStatus.PUBLISHED.value)
        )
    ).scalar_one()

    total_registrations = (await db.execute(select(func.count()).select_from(Registration))).scalar_one()
    pending_payment_registrations = (
        await db.execute(
            select(func.count())
            .select_from(Registration)
            .where(Registration.status == RegistrationStatus.PENDING_PAYMENT.value)
        )
    ).scalar_one()
    confirmed_registrations = (
        await db.execute(
            select(func.count())
            .select_from(Registration)
            .where(Registration.status == RegistrationStatus.CONFIRMED.value)
        )
    ).scalar_one()

    pending_payments_count = (
        await db.execute(
            select(func.count()).select_from(Payment).where(Payment.status == PaymentStatus.PENDING.value)
        )
    ).scalar_one()

    confirmed_payments_total = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PaymentStatus.CONFIRMED.value
            )
        )
    ).scalar_one()

    total_wallet_balance = (
        await db.execute(select(func.coalesce(func.sum(Wallet.balance), 0)))
    ).scalar_one()

    unread_notifications = (
        await db.execute(
            select(func.count()).select_from(Notification).where(Notification.read_at.is_(None))
        )
    ).scalar_one()

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_trips=total_trips,
        published_trips=published_trips,
        total_registrations=total_registrations,
        pending_payment_registrations=pending_payment_registrations,
        confirmed_registrations=confirmed_registrations,
        pending_payments_count=pending_payments_count,
        confirmed_payments_total=Decimal(confirmed_payments_total),
        total_wallet_balance=Decimal(total_wallet_balance),
        unread_notifications=unread_notifications,
    )

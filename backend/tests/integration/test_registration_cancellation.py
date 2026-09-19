import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.core.deps import get_current_user
from src.main import app
from src.models import User, Trip, Wallet, Notification, Waitlist
from src.models.registration import Registration, RegistrationStatus
from src.models.waitlist import WaitlistStatus
from src.models.payment import Payment, PaymentStatus, PaymentType
@pytest.mark.asyncio
async def test_cancel_registration_refunds_wallet_and_releases_capacity(
    client, db_session
):
    """یک Registration با deposit_paid مشخص — لغو بازگشت وجه + آزادسازی ظرفیت."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456789", full_name="Test User")
    trip = Trip(
        id=trip_id,
        title="Test Trip",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=5,
        remaining_capacity=5,
        version=1,
    )
    # مقادیر پس از ثبت‌نام واقعی: کیف پول کسر شده، ظرفیت کاهش یافته
    wallet = Wallet(user_id=user_id, balance=Decimal("90"), version=2)
    trip.remaining_capacity = 4
    trip.version = 2

    # Registration مستقیم در DB با deposit_paid=0 (همان‌طور که در واقعیت است)
    registration = Registration(
        id=uuid.uuid4(),
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.CONFIRMED.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("0"),
        remaining_amount=Decimal("50"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    # Payment واقعی با status=PENDING (همان‌طور که در واقعیت ایجاد می‌شود)
    payment = Payment(
        id=uuid.uuid4(),
        registration_id=registration.id,
        user_id=user_id,
        amount=Decimal("10"),
        type=PaymentType.DEPOSIT.value,
        status=PaymentStatus.PENDING.value,
        idempotency_key=f"registration:{registration.id}:deposit",
    )

    db_session.add_all([user, trip, wallet, registration, payment])
    await db_session.commit()

    initial_balance = Decimal("100")
    initial_remaining = 5

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # لغو ثبت‌نام
    response = await client.delete(f"/api/v1/registrations/{registration.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True

    # بررسی مستقیم دیتابیس
    result_wallet = await db_session.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    wallet = result_wallet.scalar_one()
    # پس از ثبت‌نام: 100 - 10 = 90؛ پس از لغو: 90 + 10 = 100 (برگشت به initial)
    assert wallet.balance == initial_balance
    # version: 1 (initial) -> 2 (پس از کسر در ثبت‌نام) -> 3 (پس از بازگشت در لغو)
    assert wallet.version == 3

    result_trip = await db_session.execute(
        select(Trip).where(Trip.id == trip_id)
    )
    trip = result_trip.scalar_one()
    assert trip.remaining_capacity == initial_remaining
    # version: 1 -> 2 (کسر در ثبت‌نام) -> 3 (بازگشت در ل-go)
    assert trip.version == 3

    result_reg = await db_session.execute(
        select(Registration).where(Registration.id == registration.id)
    )
    reg = result_reg.scalar_one()
    assert reg.status == RegistrationStatus.CANCELLED.value

    # بررسی Payment به REFUNDED تغییر کرده
    result_pay = await db_session.execute(
        select(Payment).where(Payment.id == payment.id)
    )
    pay = result_pay.scalar_one()
    assert pay.status == PaymentStatus.REFUNDED.value

@pytest.mark.asyncio
async def test_cancel_registration_notifies_first_waitlist_entry(
    client, db_session
):
    """یک Trip با Registration فعال و Waitlist entry (position=1, WAITING) — لغو باعث notify."""
    user_id = uuid.uuid4()
    waitlist_user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456789", full_name="Test User")
    waitlist_user = User(id=waitlist_user_id, phone_number="09123456790", full_name="Waitlist User")
    trip = Trip(
        id=trip_id,
        title="Test Trip Notify",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=1,
        remaining_capacity=0,
        version=1,
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("100"), version=1)

    # Registration فعال (پر کردن ظرفیت)
    registration = Registration(
        id=uuid.uuid4(),
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.CONFIRMED.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    # Waitlist entry
    waitlist_entry = Waitlist(
        id=uuid.uuid4(),
        user_id=waitlist_user_id,
        trip_id=trip_id,
        position=1,
        status=WaitlistStatus.WAITING.value,
    )

    db_session.add_all([user, waitlist_user, trip, wallet, registration, waitlist_entry])
    await db_session.commit()

    initial_notifications = await db_session.execute(
        select(Notification).where(Notification.user_id == waitlist_user_id)
    )
    assert initial_notifications.scalar_one_or_none() is None

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # لغو ثبت‌نام registration فعال
    response = await client.delete(f"/api/v1/registrations/{registration.id}")
    assert response.status_code == 200

    # بررسی Notification برای waitlist user
    result_notif = await db_session.execute(
        select(Notification).where(Notification.user_id == waitlist_user_id)
    )
    notification = result_notif.scalar_one_or_none()
    assert notification is not None
    assert notification.type == "waitlist_spot_available"

    # بررسی Waitlist.status -> NOTIFIED
    result_waitlist = await db_session.execute(
        select(Waitlist).where(Waitlist.id == waitlist_entry.id)
    )
    updated_waitlist = result_waitlist.scalar_one()
    assert updated_waitlist.status == WaitlistStatus.NOTIFIED.value
@pytest.mark.asyncio
async def test_cancel_already_cancelled_registration_returns_400(
    client, db_session
):
    """ثبت‌نامی که قبلاً CANCELLED است — لغو مجدد 400."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456789", full_name="Test User")
    trip = Trip(
        id=trip_id,
        title="Test Trip",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=5,
        remaining_capacity=5,
        version=1,
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("100"), version=1)

    registration = Registration(
        id=uuid.uuid4(),
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.CANCELLED.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        cancelled_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    db_session.add_all([user, trip, wallet, registration])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.delete(f"/api/v1/registrations/{registration.id}")
    assert response.status_code == 400
    body = response.json()
    assert "قبلاً لغو شده" in body["detail"]

@pytest.mark.asyncio
async def test_cancel_other_users_registration_returns_404(
    client, db_session
):
    """ثبت‌نام متعلق به کاربر دیگر — 404."""
    owner_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    owner = User(id=owner_id, phone_number="09123456789", full_name="Owner")
    other_user = User(id=other_user_id, phone_number="09123456790", full_name="Other User")
    trip = Trip(
        id=trip_id,
        title="Test Trip",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=5,
        remaining_capacity=5,
        version=1,
    )
    wallet = Wallet(user_id=owner_id, balance=Decimal("100"), version=1)

    registration = Registration(
        id=uuid.uuid4(),
        user_id=owner_id,
        trip_id=trip_id,
        status=RegistrationStatus.CONFIRMED.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    db_session.add_all([owner, other_user, trip, wallet, registration])
    await db_session.commit()

    async def override_get_current_user():
        return other_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.delete(f"/api/v1/registrations/{registration.id}")
    assert response.status_code == 404
    body = response.json()
    assert "یافت نشد" in body["detail"]
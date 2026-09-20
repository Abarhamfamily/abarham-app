import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.core.deps import get_current_user
from src.main import app
from src.models import User, Trip, Wallet
from src.models.registration import Registration, RegistrationStatus
from src.models.payment import Payment, PaymentStatus, PaymentType


@pytest.mark.asyncio
async def test_pay_remaining_amount_success(client, db_session):
    """پرداخت موفق مبلغ باقی‌مانده از طریق کیف پول."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    reg_id = uuid.uuid4()
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
        id=reg_id,
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.PENDING_PAYMENT.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    db_session.add_all([user, trip, wallet, registration])
    await db_session.commit()

    idempotency_key = f"payment:{reg_id}:remaining"

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/payments",
        json={
            "registration_id": str(reg_id),
            "amount": "40",
            "idempotency_key": idempotency_key,
            "method": "wallet",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "paid"
    assert Decimal(body["payment"]["amount"]) == Decimal("40")
    assert body["payment"]["type"] == PaymentType.REMAINING.value
    assert body["payment"]["status"] == PaymentStatus.CONFIRMED.value
    assert body["payment"]["method"] == "wallet"
    assert body["payment"]["idempotency_key"] == idempotency_key

    result_wallet = await db_session.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    wallet = result_wallet.scalar_one()
    assert wallet.balance == Decimal("60")
    assert wallet.version == 2

    result_reg = await db_session.execute(
        select(Registration).where(Registration.id == reg_id)
    )
    registration = result_reg.scalar_one()
    assert registration.deposit_paid == Decimal("50")
    assert registration.remaining_amount == Decimal("0")
    assert registration.status == RegistrationStatus.CONFIRMED.value
    assert registration.confirmed_at is not None

    result_payment = await db_session.execute(
        select(Payment).where(Payment.idempotency_key == idempotency_key)
    )
    payment = result_payment.scalar_one()
    assert payment.amount == Decimal("40")
    assert payment.type == PaymentType.REMAINING.value
    assert payment.status == PaymentStatus.CONFIRMED.value
    assert payment.method == "wallet"
    assert payment.confirmed_at is not None


@pytest.mark.asyncio
async def test_pay_remaining_wrong_amount_returns_422(client, db_session):
    """مبلغ ارسالی متفاوت از remaining_amount — 422."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    reg_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456791", full_name="Test User 2")
    trip = Trip(
        id=trip_id,
        title="Test Trip 2",
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
        id=reg_id,
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.PENDING_PAYMENT.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    db_session.add_all([user, trip, wallet, registration])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/payments",
        json={
            "registration_id": str(reg_id),
            "amount": "30",
            "idempotency_key": "test-wrong-amount-1",
            "method": "wallet",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert "باقی‌مانده" in body["detail"]

    result_reg = await db_session.execute(
        select(Registration).where(Registration.id == reg_id)
    )



@pytest.mark.asyncio
async def test_pay_remaining_insufficient_balance_returns_402(client, db_session):
    """موجودی کیف پول کمتر از مبلغ — 402 و Registration تغییر نکرده."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    reg_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456792", full_name="Test User 3")
    trip = Trip(
        id=trip_id,
        title="Test Trip 3",
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
    wallet = Wallet(user_id=user_id, balance=Decimal("30"), version=1)

    registration = Registration(
        id=reg_id,
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.PENDING_PAYMENT.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    db_session.add_all([user, trip, wallet, registration])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/payments",
        json={
            "registration_id": str(reg_id),
            "amount": "40",
            "idempotency_key": "test-insufficient-balance-1",
            "method": "wallet",
        },
    )
    assert response.status_code == 402
    body = response.json()
    assert "موجودی کیف پول کافی نیست" in body["detail"]

    result_wallet = await db_session.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    wallet = result_wallet.scalar_one()
    assert wallet.balance == Decimal("30")
    assert wallet.version == 1

    result_reg = await db_session.execute(
        select(Registration).where(Registration.id == reg_id)
    )
    registration = result_reg.scalar_one()
    assert registration.remaining_amount == Decimal("40")
    assert registration.status == RegistrationStatus.PENDING_PAYMENT.value


@pytest.mark.asyncio
async def test_pay_remaining_idempotent_duplicate_request(client, db_session):
    """همان idempotency_key دوبار — دومی already_processed و کیف پول فقط یک‌بار کسر شده."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    reg_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456793", full_name="Test User 4")
    trip = Trip(
        id=trip_id,
        title="Test Trip 4",
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
        id=reg_id,
        user_id=user_id,
        trip_id=trip_id,
        status=RegistrationStatus.PENDING_PAYMENT.value,
        total_price=Decimal("50"),
        deposit_paid=Decimal("10"),
        remaining_amount=Decimal("40"),
        passenger_count=1,
        registered_at=now,
        vehicle_type="own",
        empty_seats_provided=0,
    )

    db_session.add_all([user, trip, wallet, registration])
    await db_session.commit()

    idempotency_key = f"payment:{reg_id}:remaining:duplicate"

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response1 = await client.post(
        "/api/v1/payments",
        json={
            "registration_id": str(reg_id),
            "amount": "40",
            "idempotency_key": idempotency_key,
            "method": "wallet",
        },
    )
    assert response1.status_code == 201
    body1 = response1.json()
    assert body1["status"] == "paid"

    response2 = await client.post(
        "/api/v1/payments",
        json={
            "registration_id": str(reg_id),
            "amount": "40",
            "idempotency_key": idempotency_key,
            "method": "wallet",
        },
    )
    assert response2.status_code == 201
    body2 = response2.json()
    assert body2["status"] == "already_processed"
    assert body2["payment"]["id"] == body1["payment"]["id"]

    result_wallet = await db_session.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    wallet = result_wallet.scalar_one()
    assert wallet.balance == Decimal("60")
    assert wallet.version == 2

    result_reg = await db_session.execute(
        select(Registration).where(Registration.id == reg_id)
    )
    registration = result_reg.scalar_one()
    assert registration.remaining_amount == Decimal("0")
    assert registration.status == RegistrationStatus.CONFIRMED.value
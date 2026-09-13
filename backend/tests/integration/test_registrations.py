import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.core.deps import get_current_user
from src.main import app
from src.models import User, Trip, Wallet
from src.models.registration import Registration


@pytest.mark.asyncio
async def test_successful_registration_own_vehicle(client, db_session):
    """تور با vehicle_type='own' و other_vehicle_price=None — ثبت‌نام موفق."""
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
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("100"), version=1)

    db_session.add_all([user, trip, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/registrations",
        json={
            "trip_id": str(trip_id),
            "passenger_count": 1,
            "vehicle_type": "own",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["registration"] is not None
    assert body["payment"] is not None
    assert body["waitlist_entry"] is None
    assert body["message"] == "ثبت‌نام با موفقیت انجام شد"


@pytest.mark.asyncio
async def test_successful_registration_other_vehicle(client, db_session):
    """تور با vehicle_type='other' و other_vehicle_price مشخص — ثبت‌نام موفق."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456781", full_name="Test User 2")
    trip = Trip(
        id=trip_id,
        title="Test Trip Other",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=Decimal("10"),
        capacity=5,
        remaining_capacity=5,
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("100"), version=1)

    db_session.add_all([user, trip, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/registrations",
        json={
            "trip_id": str(trip_id),
            "passenger_count": 1,
            "vehicle_type": "other",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["registration"] is not None
    assert body["waitlist_entry"] is None


@pytest.mark.asyncio
async def test_registration_trip_not_found(client, db_session):
    """ثبت‌نام با trip_id تصادفی — 404."""
    user_id = uuid.uuid4()
    user = User(id=user_id, phone_number="09123456782", full_name="Test User 3")
    db_session.add(user)
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/registrations",
        json={
            "trip_id": str(uuid.uuid4()),
            "passenger_count": 1,
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_registration_rejected(client, db_session):
    """دوبار ثبت‌نام با همان trip و کاربر — بار دوم 409."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456783", full_name="Test User 4")
    trip = Trip(
        id=trip_id,
        title="Test Trip Dup",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=5,
        remaining_capacity=5,
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("100"), version=1)

    db_session.add_all([user, trip, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    payload = {"trip_id": str(trip_id), "passenger_count": 1, "vehicle_type": "own"}

    response1 = await client.post("/api/v1/registrations", json=payload)
    assert response1.status_code == 201

    response2 = await client.post("/api/v1/registrations", json=payload)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_insufficient_wallet_balance(client, db_session):
    """موجودی کیف پول کافی نیست — 402 و هیچ ثبت‌نامی ساخته نشده."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456784", full_name="Test User 5")
    trip = Trip(
        id=trip_id,
        title="Test Trip Low Balance",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=5,
        remaining_capacity=5,
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("5"), version=1)

    db_session.add_all([user, trip, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/registrations",
        json={
            "trip_id": str(trip_id),
            "passenger_count": 1,
            "vehicle_type": "own",
        },
    )
    assert response.status_code == 402

    result = await db_session.execute(select(Registration).where(Registration.trip_id == trip_id))
    registration = result.scalar_one_or_none()
    assert registration is None


@pytest.mark.asyncio
async def test_waitlist_when_capacity_full(client, db_session):
    """ظرفیت تور پر — وارد Waitlist می‌شود، موجودی کیف پول تغییری نمی‌کند."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456785", full_name="Test User 6")
    trip = Trip(
        id=trip_id,
        title="Test Trip Full",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=1,
        remaining_capacity=0,
    )
    wallet = Wallet(user_id=user_id, balance=Decimal("120"), version=1)

    db_session.add_all([user, trip, wallet])
    await db_session.commit()

    initial_balance = Decimal("120")

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/registrations",
        json={
            "trip_id": str(trip_id),
            "passenger_count": 1,
            "vehicle_type": "own",
        },
    )
    assert response.status_code == 201
    body = response.json()
    print(f"DEBUG response body: {body}")
    assert body["registration"] is None
    assert body["waitlist_entry"] is not None
    assert body["payment"] is None

    result = await db_session.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    print(f"DEBUG wallet balance: {wallet.balance}, version: {wallet.version}")
    assert wallet.balance == initial_balance


@pytest.mark.asyncio
async def test_other_vehicle_without_price_returns_422(client, db_session):
    """تور با other_vehicle_price=None و vehicle_type='other' — 422."""
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = User(id=user_id, phone_number="09123456786", full_name="Test User 7")
    trip = Trip(
        id=trip_id,
        title="Test Trip No Price",
        destination="Test Destination",
        start_date=now,
        end_date=now,
        price=Decimal("50"),
        deposit_amount=Decimal("10"),
        other_vehicle_price=None,
        capacity=5,
        remaining_capacity=5,
    )
    db_session.add_all([user, trip])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/registrations",
        json={
            "trip_id": str(trip_id),
            "passenger_count": 1,
            "vehicle_type": "other",
        },
    )
    assert response.status_code == 422
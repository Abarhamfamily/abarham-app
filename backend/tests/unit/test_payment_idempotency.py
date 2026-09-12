import pytest
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.models.trip import Trip
from src.models.registration import Registration
from src.models.payment import Payment
from src.services.payment_idempotency import (
    generate_deposit_idempotency_key,
    get_or_create_deposit_payment,
)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        phone_number="09123456789",
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_trip(db_session: AsyncSession):
    """Create a test trip."""
    trip = Trip(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        title="Test Trip",
        destination="Test Destination",
        description="Test trip for payment idempotency testing",
        start_date=datetime(2024, 12, 31, 10, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2024, 12, 31, 18, 0, 0, tzinfo=timezone.utc),
        price=Decimal("100000"),
        deposit_amount=Decimal("30000"),
        capacity=10,
        remaining_capacity=10,
        version=1,
        status="published",
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


@pytest_asyncio.fixture
async def test_registration(db_session: AsyncSession, test_user: User, test_trip: Trip):
    """Create a test registration."""
    registration = Registration(
        id=UUID("66666666-6666-6666-6666-666666666666"),
        user_id=test_user.id,
        trip_id=test_trip.id,
        status="pending_payment",
        total_price=Decimal("100000"),
        deposit_paid=Decimal("0"),
        remaining_amount=Decimal("100000"),
        passenger_count=1,
        empty_seats_provided=0,
        registered_at=datetime.now(timezone.utc),
    )
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration

@pytest.mark.asyncio
async def test_generate_deposit_idempotency_key():
    """Test that idempotency key is generated correctly."""
    registration_id = UUID("66666666-6666-6666-6666-666666666666")
    key = generate_deposit_idempotency_key(registration_id)
    assert key == f"registration:{registration_id}:deposit"


@pytest.mark.asyncio
async def test_get_or_create_deposit_payment_first_call_creates_new(
    db_session: AsyncSession, test_registration: Registration, test_user: User
):
    """First call with a registration_id should create a new Payment."""
    # Act
    payment, was_created = await get_or_create_deposit_payment(
        db=db_session,
        registration_id=test_registration.id,
        user_id=test_user.id,
        amount=Decimal("30000"),
    )

    # Assert
    assert was_created is True
    assert payment.registration_id == test_registration.id
    assert payment.user_id == test_user.id
    assert payment.amount == Decimal("30000")
    assert payment.type == "deposit"
    assert payment.status == "pending"
    assert payment.idempotency_key == f"registration:{test_registration.id}:deposit"


@pytest.mark.asyncio
async def test_get_or_create_deposit_payment_second_call_returns_existing(
    db_session: AsyncSession, test_registration: Registration, test_user: User
):
    """Second call with same registration_id should return existing Payment without creating new one."""
    # Act - First call
    payment1, was_created1 = await get_or_create_deposit_payment(
        db=db_session,
        registration_id=test_registration.id,
        user_id=test_user.id,
        amount=Decimal("30000"),
    )

    # Act - Second call (simulating retry)
    payment2, was_created2 = await get_or_create_deposit_payment(
        db=db_session,
        registration_id=test_registration.id,
        user_id=test_user.id,
        amount=Decimal("30000"),
    )

    # Assert
    assert was_created1 is True
    assert was_created2 is False
    assert payment1.id == payment2.id  # Same object
    assert payment1.idempotency_key == payment2.idempotency_key

    # Verify only one Payment exists in database for this registration
    result = await db_session.execute(
        select(Payment).where(Payment.registration_id == test_registration.id)
    )
    payments = result.scalars().all()
    assert len(payments) == 1


@pytest.mark.asyncio
async def test_get_or_create_deposit_payment_different_registration_creates_separate(
    db_session: AsyncSession, test_user: User, test_trip: Trip
):
    """Different registration_ids should create separate Payments."""
    # Create second registration
    registration2 = Registration(
        id=UUID("77777777-7777-7777-7777-777777777777"),
        user_id=test_user.id,
        trip_id=test_trip.id,
        status="pending_payment",
        total_price=Decimal("150000"),
        deposit_paid=Decimal("0"),
        remaining_amount=Decimal("150000"),
        passenger_count=1,
        empty_seats_provided=0,
        registered_at=datetime.now(timezone.utc),
    )
    db_session.add(registration2)
    await db_session.commit()

    # Create payments for both registrations
    payment1, created1 = await get_or_create_deposit_payment(
        db=db_session,
        registration_id=UUID("66666666-6666-6666-6666-666666666666"),
        user_id=test_user.id,
        amount=Decimal("30000"),
    )

    payment2, created2 = await get_or_create_deposit_payment(
        db=db_session,
        registration_id=registration2.id,
        user_id=test_user.id,
        amount=Decimal("45000"),
    )

    # Assert
    assert created1 is True
    assert created2 is True
    assert payment1.id != payment2.id
    assert payment1.idempotency_key != payment2.idempotency_key
    assert payment1.registration_id != payment2.registration_id
    assert payment1.amount == Decimal("30000")
    assert payment2.amount == Decimal("45000")

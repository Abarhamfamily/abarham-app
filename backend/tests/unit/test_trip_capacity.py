import pytest
from uuid import UUID

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal

from src.models.trip import Trip
from src.services.trip_capacity import try_decrement_trip_capacity


@pytest_asyncio.fixture
async def test_trip(db_session: AsyncSession):
    """Create a test trip for our unit tests."""
    trip = Trip(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        title="Test Trip",
        destination="Test Destination",
        description="Test trip for unit testing",
        start_date=datetime(2024, 12, 31, 10, 0, 0),
        end_date=datetime(2024, 12, 31, 10, 0, 0),
        price=Decimal("100000"),
        deposit_amount=Decimal("100000"),
        other_vehicle_price=Decimal("20000"),
        capacity=10,
        remaining_capacity=10,
        status="published",
        version=1,
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


@pytest.mark.asyncio
async def test_successful_capacity_decrement(db_session: AsyncSession, test_trip: Trip):
    """Test successful capacity decrement with valid version and sufficient capacity."""
    # Arrange
    initial_capacity = test_trip.remaining_capacity
    initial_version = test_trip.version
    passenger_count = 2

    # Act
    result = await try_decrement_trip_capacity(
        db=db_session,
        trip_id=test_trip.id,
        current_version=initial_version,
        passenger_count=passenger_count,
    )

    # Assert
    assert result is True
    await db_session.refresh(test_trip)
    assert test_trip.remaining_capacity == initial_capacity - passenger_count
    assert test_trip.version == initial_version + 1


@pytest.mark.asyncio
async def test_capacity_decrement_insufficient_capacity(db_session: AsyncSession, test_trip: Trip):
    """Test capacity decrement failure due to insufficient remaining capacity."""
    # Arrange
    initial_capacity = test_trip.remaining_capacity
    initial_version = test_trip.version
    passenger_count = initial_capacity + 1  # More than available

    # Act
    result = await try_decrement_trip_capacity(
        db=db_session,
        trip_id=test_trip.id,
        current_version=initial_version,
        passenger_count=passenger_count,
    )

    # Assert
    assert result is False
    await db_session.refresh(test_trip)
    assert test_trip.remaining_capacity == initial_capacity  # No change
    assert test_trip.version == initial_version  # No change


@pytest.mark.asyncio
async def test_capacity_decrement_wrong_version(db_session: AsyncSession, test_trip: Trip):
    """Test capacity decrement failure due to version mismatch (simulating race condition)."""
    # Arrange - First successful decrement to advance version
    await try_decrement_trip_capacity(
        db=db_session,
        trip_id=test_trip.id,
        current_version=test_trip.version,
        passenger_count=1,
    )
    await db_session.refresh(test_trip)

    initial_capacity = test_trip.remaining_capacity
    wrong_version = test_trip.version + 1  # Wrong version
    passenger_count = 1

    # Act - Try to decrement with wrong version
    result = await try_decrement_trip_capacity(
        db=db_session,
        trip_id=test_trip.id,
        current_version=wrong_version,
        passenger_count=passenger_count,
    )

    # Assert
    assert result is False
    await db_session.refresh(test_trip)
    assert test_trip.remaining_capacity == initial_capacity  # No change
    # Note: version remains unchanged because WHERE version clause failed

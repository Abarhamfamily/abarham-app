import pytest
from uuid import UUID

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from src.models.user import User
from src.models.wallet import Wallet
from src.services.wallet_balance import (
    try_decrement_wallet_balance,
    try_increment_wallet_balance,
    try_reserve_wallet_balance,
    try_release_wallet_balance,
)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for our wallet tests."""
    user = User(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        phone_number="09123456789",
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_wallet(db_session: AsyncSession, test_user: User):
    """Create a test wallet for our unit tests."""
    wallet = Wallet(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        user_id=test_user.id,
        balance=Decimal("100000"),
        pending_balance=Decimal("0"),
        total_deposited=Decimal("100000"),
        total_withdrawn=Decimal("0"),
        version=1,
    )
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)
    return wallet


@pytest.mark.asyncio
async def test_successful_balance_decrement(db_session: AsyncSession, test_wallet: Wallet):
    """Test successful balance decrement with valid balance and sufficient version."""
    # Arrange
    initial_balance = test_wallet.balance
    initial_version = test_wallet.version
    amount = Decimal("50000")

    # Act
    result = await try_decrement_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=amount,
    )

    # Assert
    assert result is True
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance - amount
    assert test_wallet.version == initial_version + 1


@pytest.mark.asyncio
async def test_balance_decrement_insufficient_balance(db_session: AsyncSession, test_wallet: Wallet):
    """Test balance decrement failure due to insufficient balance."""
    # Arrange
    initial_balance = test_wallet.balance
    initial_version = test_wallet.version
    amount = initial_balance + 1  # More than available

    # Act
    result = await try_decrement_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=amount,
    )

    # Assert
    assert result is False
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance  # No change
    assert test_wallet.version == initial_version  # No change


@pytest.mark.asyncio
async def test_balance_decrement_wrong_version(db_session: AsyncSession, test_wallet: Wallet):
    """Test balance decrement failure due to version mismatch (simulating race condition)."""
    # Arrange - First successful decrement to advance version
    await try_decrement_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=test_wallet.version,
        amount=Decimal("10000"),
    )
    await db_session.refresh(test_wallet)

    initial_balance = test_wallet.balance
    wrong_version = test_wallet.version + 1  # Wrong version
    amount = Decimal("5000")

    # Act - Try to decrement with wrong version
    result = await try_decrement_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=wrong_version,
        amount=amount,
    )

    # Assert
    assert result is False
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance  # No change
    # Note: version remains unchanged because WHERE version clause failed


@pytest.mark.asyncio
async def test_successful_balance_increment(db_session: AsyncSession, test_wallet: Wallet):
    """Test successful balance increment with valid version."""
    # Arrange
    initial_balance = test_wallet.balance
    initial_total_deposited = test_wallet.total_deposited
    initial_version = test_wallet.version
    amount = Decimal("25000")  # Less than balance (not required for increment, but realistic)

    # Act
    result = await try_increment_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=amount,
    )

    # Assert
    assert result is True
    await db_session.commit()
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance + amount
    assert test_wallet.total_deposited == initial_total_deposited + amount
    assert test_wallet.version == initial_version + 1


@pytest.mark.asyncio
async def test_balance_increment_wrong_version(db_session: AsyncSession, test_wallet: Wallet):
    """Test balance increment failure due to version mismatch (simulating race condition)."""
    # Arrange
    initial_balance = test_wallet.balance
    initial_total_deposited = test_wallet.total_deposited
    initial_version = test_wallet.version
    wrong_version = test_wallet.version + 1  # Wrong version
    amount = Decimal("5000")

    # Act - Try to increment with wrong version
    result = await try_increment_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=wrong_version,
        amount=amount,
    )

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_successful_balance_reserve(
    db_session: AsyncSession, test_wallet: Wallet
):
    """Test successful reserve (balance -> pending_balance) with sufficient balance."""
    # Arrange
    initial_balance = test_wallet.balance
    initial_pending = test_wallet.pending_balance
    initial_version = test_wallet.version
    amount = Decimal("30000")

    # Act
    result = await try_reserve_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=amount,
    )

    # Assert
    assert result is True
    await db_session.commit()
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance - amount
    assert test_wallet.pending_balance == initial_pending + amount
    assert test_wallet.version == initial_version + 1


@pytest.mark.asyncio
async def test_balance_reserve_insufficient_balance(
    db_session: AsyncSession, test_wallet: Wallet
):
    """Test reserve failure due to insufficient balance."""
    # Arrange
    initial_balance = test_wallet.balance
    initial_version = test_wallet.version
    amount = initial_balance + 1  # More than available

    # Act
    result = await try_reserve_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=amount,
    )

    # Assert
    assert result is False
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance  # No change
    assert test_wallet.pending_balance == Decimal("0")  # No change
    assert test_wallet.version == initial_version  # No change


@pytest.mark.asyncio
async def test_successful_balance_release(
    db_session: AsyncSession, test_wallet: Wallet
):
    """Test successful release (pending_balance -> balance) for admin rejection."""
    # First reserve some amount to create a pending balance
    reserve_amount = Decimal("30000")
    await try_reserve_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=test_wallet.version,
        amount=reserve_amount,
    )
    await db_session.commit()
    await db_session.refresh(test_wallet)

    initial_balance = test_wallet.balance
    initial_pending = test_wallet.pending_balance
    initial_version = test_wallet.version

    # Act - Release the reserved amount
    result = await try_release_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=reserve_amount,
    )

    # Assert
    assert result is True
    await db_session.commit()
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance + reserve_amount
    assert test_wallet.pending_balance == initial_pending - reserve_amount
    assert test_wallet.version == initial_version + 1


@pytest.mark.asyncio
async def test_balance_release_insufficient_pending(
    db_session: AsyncSession, test_wallet: Wallet
):
    """Test release failure due to insufficient pending balance."""
    # Arrange
    initial_pending = test_wallet.pending_balance
    initial_version = test_wallet.version
    amount = initial_pending + 1  # More than pending

    # Act
    result = await try_release_wallet_balance(
        db=db_session,
        user_id=test_wallet.user_id,
        current_version=initial_version,
        amount=amount,
    )

    # Assert
    assert result is False
    await db_session.refresh(test_wallet)
    assert test_wallet.balance == test_wallet.balance  # No change
    assert test_wallet.pending_balance == initial_pending  # No change
    assert test_wallet.version == initial_version  # No change
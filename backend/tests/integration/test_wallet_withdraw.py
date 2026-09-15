import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import status
from sqlalchemy import select

from src.core.deps import get_current_user
from src.main import app
from src.models import User, Wallet
from src.models.wallet import TransactionType, TransactionStatus
from src.schemas.wallet import WalletWithdrawRequest


@pytest.mark.asyncio
async def test_withdraw_success_reserves_balance(client, db_session):
    """تست موفق: برداشت ۵۰۰۰۰ از موجودی ۱۰۰۰۰۰ (کمتر از ۸۰٪) و رزرو موفق."""
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user_model = User(id=user_id, phone_number="09123456789", full_name="Test User")
    wallet = Wallet(user_id=user_id, balance=Decimal("100000"), version=1)

    db_session.add_all([user_model, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user_model

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/wallet/withdraw",
        json={
            "amount": "50000",
            "card_number": "1234567890",
        },
    )
    assert response.status_code == 201

    body = response.json()
    assert Decimal(body["amount"]) == Decimal("50000")
    assert body["status"].upper() == "PENDING"

    #Verify database state
    result = await db_session.execute(select(Wallet).where(Wallet.user_id == user_id))
    db_wallet = result.scalar_one_or_none()
    assert db_wallet is not None
    assert db_wallet.balance == Decimal("50000"), f"Expected balance 50000, got {db_wallet.balance}"
    assert db_wallet.pending_balance == Decimal("50000"), f"Expected pending_balance 50000, got {db_wallet.pending_balance}"


@pytest.mark.asyncio
async def test_withdraw_exceeds_80_percent_rejected(client, db_session):
    """تست rejected: برداشت ۹۰۰۰۰ از موجودی ۱۰۰۰۰۰ (بیشتر از ۸۰٪ = ۸۰۰۰۰) - باید ۴۰۰ برگرداند."""
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user_model = User(id=user_id, phone_number="09123456789", full_name="Test User")
    wallet = Wallet(user_id=user_id, balance=Decimal("100000"), version=1)

    db_session.add_all([user_model, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user_model

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/wallet/withdraw",
        json={
            "amount": "90000",
            "card_number": "1234567890",
        },
    )
    assert response.status_code == 400

    body = response.json()
    assert "۸۰٪" in body["detail"] or "maximum" in body["detail"].lower()


@pytest.mark.asyncio
async def test_withdraw_duplicate_pending_rejected(client, db_session):
    """تست rejected: یک withdraw موفق سپس یک دومی که pending است - باید ۴۰۹ برگرداند."""
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user_model = User(id=user_id, phone_number="09123456789", full_name="Test User")
    wallet = Wallet(user_id=user_id, balance=Decimal("100000"), version=1)

    db_session.add_all([user_model, wallet])
    await db_session.commit()

    async def override_get_current_user():
        return user_model

    app.dependency_overrides[get_current_user] = override_get_current_user

    # First withdrawal
    await client.post(
        "/api/v1/wallet/withdraw",
        json={
            "amount": "30000",
            "card_number": "1234567890",
        },
    )

    # Second withdrawal while first is still PENDING
    response = await client.post(
        "/api/v1/wallet/withdraw",
        json={
            "amount": "20000",
            "card_number": "0987654321",
        },
    )
    assert response.status_code == 409

    body = response.json()
    assert "در حال بررسی" in body["detail"] or "pending" in body["detail"].lower()


@pytest.mark.asyncio
async def test_withdraw_no_wallet_returns_404(client, db_session):
    """تست rejected: ورداشت برای کاربر بدون کیف پول - باید ۴۰۴ برگرداند."""
    user_id = uuid.uuid4()

    user_model = User(id=user_id, phone_number="09123456789", full_name="Test User")

    db_session.add(user_model)
    await db_session.commit()

    async def override_get_current_user():
        return user_model

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/wallet/withdraw",
        json={
            "amount": "1000",
            "card_number": "1234567890",
        },
    )
    assert response.status_code == 404

    body = response.json()
    assert "کیف پول" in body["detail"] or "wallet" in body["detail"].lower()
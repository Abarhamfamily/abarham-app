import pytest
from decimal import Decimal

from src.models.user import User
from src.models.wallet import Wallet, Transaction, TransactionType, TransactionStatus
from src.core.security import hash_password


async def _seed_wallet_with_withdrawal(db_session, balance="0", amount="50000", status=TransactionStatus.PENDING.value):
    """Seed a wallet with a withdrawal transaction."""
    user = User(phone_number="+989123456789", full_name="test user", password_hash=hash_password("Pass12345"))
    db_session.add(user)
    await db_session.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal(balance), pending_balance=Decimal(amount) if status == TransactionStatus.PENDING.value else Decimal("0"), version=1)
    db_session.add(wallet)
    await db_session.flush()

    from datetime import datetime, timezone
    base_dt = datetime(2024, 1, 1, tzinfo=timezone.utc)

    if status == TransactionStatus.PENDING.value:
        desc = "withdrawal via app"
        conf_at = None
        meta = {"card_number": "1234567890"}
    elif status == TransactionStatus.CONFIRMED.value:
        desc = "confirmed"
        conf_at = base_dt
        meta = None
    elif status == TransactionStatus.REVERSED.value:
        desc = "reversed"
        conf_at = base_dt
        meta = None
    else:
        desc = "unknown"
        conf_at = None
        meta = None

    transaction = Transaction(
        wallet_id=wallet.id,
        amount=Decimal(amount),
        type=TransactionType.WITHDRAWAL.value,
        status=status,
        description=desc,
        created_at=base_dt,
        confirmed_at=conf_at,
        transaction_metadata=meta,
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(wallet)
    return wallet, transaction


@pytest.mark.asyncio
async def test_list_withdrawals_shows_pending(client, admin_token, db_session):
    """test: shows pending withdrawal requests."""
    wallet, transaction = await _seed_wallet_with_withdrawal(db_session, balance="100000", amount="50000", status=TransactionStatus.PENDING.value)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.get("/api/v1/admin/wallet/withdrawals", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert item["wallet_id"] == str(wallet.id)
    assert item["amount"] == "50000" or item["amount"] == "50000.00"
    assert item["status"] == TransactionStatus.PENDING.value
    assert item["card_number"] == "1234567890"
    assert item["user_full_name"] == "test user"
    assert item["user_phone_number"] == "+989123456789"


@pytest.mark.asyncio
async def test_approve_withdrawal_finalizes_amount(client, admin_token, db_session):
    wallet, transaction = await _seed_wallet_with_withdrawal(db_session, balance="50000", amount="50000", status=TransactionStatus.PENDING.value)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(f"/api/v1/admin/wallet/withdrawals/{transaction.id}/approve", headers=headers)
    assert resp.status_code == 200
    item = resp.json()
    assert item["status"] == TransactionStatus.CONFIRMED.value

    db_wallet = await db_session.get(Wallet, wallet.id)
    assert db_wallet.pending_balance == Decimal("0")
    assert db_wallet.total_withdrawn == Decimal("50000")
    assert db_wallet.balance == Decimal("50000")
    assert db_wallet.version == 2

    db_transaction = await db_session.get(Transaction, transaction.id)
    assert db_transaction.status == TransactionStatus.CONFIRMED.value
    assert db_transaction.confirmed_at is not None


@pytest.mark.asyncio
async def test_reject_withdrawal_returns_amount_to_balance(client, admin_token, db_session):
    """test: reject returns amount to balance."""
    wallet, transaction = await _seed_wallet_with_withdrawal(db_session, balance="50000", amount="50000", status=TransactionStatus.PENDING.value)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(f"/api/v1/admin/wallet/withdrawals/{transaction.id}/reject", headers=headers, json={"reason": "invalid card details"})
    assert resp.status_code == 200
    item = resp.json()
    assert item["status"] == TransactionStatus.REVERSED.value

    db_wallet = await db_session.get(Wallet, wallet.id)
    assert db_wallet.balance == Decimal("100000")
    assert db_wallet.pending_balance == Decimal("0")
    assert db_wallet.total_withdrawn == Decimal("0")
    assert db_wallet.version == 2

    db_transaction = await db_session.get(Transaction, transaction.id)
    assert db_transaction.status == TransactionStatus.REVERSED.value
    assert "invalid card details" in db_transaction.description


@pytest.mark.asyncio
async def test_approve_already_processed_withdrawal_rejected(client, admin_token, db_session):
    """test: approve already processed withdrawal is rejected."""
    wallet, transaction = await _seed_wallet_with_withdrawal(db_session, balance="50000", amount="50000", status=TransactionStatus.CONFIRMED.value)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(f"/api/v1/admin/wallet/withdrawals/{transaction.id}/approve", headers=headers)
    assert resp.status_code == 400
    assert "فقط درخواست‌های در انتظار بررسی قابل تأیید هستند" in resp.json()["detail"]
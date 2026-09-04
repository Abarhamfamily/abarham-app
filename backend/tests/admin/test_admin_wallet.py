import pytest


async def _seed_wallet(db_session, balance="0"):
    from decimal import Decimal
    from src.models.user import User
    from src.models.wallet import Wallet
    from src.core.security import hash_password

    user = User(phone_number="+989121111111", full_name="کاربر", password_hash=hash_password("Pass12345"))
    db_session.add(user)
    await db_session.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal(balance))
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)
    return wallet


@pytest.mark.asyncio
async def test_wallet_adjust_increase(client, admin_token, db_session):
    wallet = await _seed_wallet(db_session, balance="0")
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(
        f"/api/v1/admin/wallet/{wallet.id}/adjust",
        headers=headers,
        json={"amount": "50000", "description": "هدیه"},
    )
    assert resp.status_code == 201
    assert resp.json()["amount"] == "50000.00"

    list_resp = await client.get("/api/v1/admin/wallet", headers=headers)
    assert list_resp.json()["data"][0]["balance"] == "50000.00"


@pytest.mark.asyncio
async def test_wallet_adjust_cannot_go_negative(client, admin_token, db_session):
    wallet = await _seed_wallet(db_session, balance="10000")
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(
        f"/api/v1/admin/wallet/{wallet.id}/adjust",
        headers=headers,
        json={"amount": "-50000", "description": "برداشت اشتباه"},
    )
    assert resp.status_code == 400

import pytest
from decimal import Decimal
from datetime import datetime, timezone


async def _seed_registration_with_payment(db_session, amount="300000", total_price="1000000"):
    from src.models.user import User
    from src.models.trip import Trip
    from src.models.registration import Registration
    from src.models.payment import Payment
    from src.core.security import hash_password

    user = User(phone_number="+989121111111", full_name="کاربر", password_hash=hash_password("Pass12345"))
    db_session.add(user)
    await db_session.flush()

    trip = Trip(
        title="تور",
        destination="مقصد",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc),
        price=Decimal(total_price),
        deposit_amount=Decimal(amount),
        capacity=10,
        remaining_capacity=10,
    )
    db_session.add(trip)
    await db_session.flush()

    registration = Registration(
        user_id=user.id,
        trip_id=trip.id,
        status="pending_payment",
        total_price=Decimal(total_price),
        deposit_paid=Decimal("0"),
        remaining_amount=Decimal(total_price),
        registered_at=datetime.now(timezone.utc),
    )
    db_session.add(registration)
    await db_session.flush()

    payment = Payment(
        registration_id=registration.id,
        user_id=user.id,
        amount=Decimal(amount),
        type="deposit",
        status="pending",
        idempotency_key="test-key",
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    await db_session.refresh(registration)
    return payment, registration


@pytest.mark.asyncio
async def test_confirm_payment_updates_registration(client, admin_token, db_session):
    payment, registration = await _seed_registration_with_payment(db_session)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(
        f"/api/v1/admin/payments/{payment.id}/confirm",
        headers=headers,
        json={"reference_code": "REF1"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"

    reg_resp = await client.get(f"/api/v1/admin/registrations/{registration.id}", headers=headers)
    body = reg_resp.json()
    assert body["deposit_paid"] == "300000.00"
    assert body["status"] == "pending_payment"  # هنوز کامل پرداخت نشده


@pytest.mark.asyncio
async def test_confirm_full_payment_marks_registration_confirmed(client, admin_token, db_session):
    payment, registration = await _seed_registration_with_payment(
        db_session, amount="1000000", total_price="1000000"
    )
    headers = {"Authorization": f"Bearer {admin_token}"}

    await client.post(f"/api/v1/admin/payments/{payment.id}/confirm", headers=headers, json={})

    reg_resp = await client.get(f"/api/v1/admin/registrations/{registration.id}", headers=headers)
    body = reg_resp.json()
    assert body["status"] == "confirmed"
    assert body["remaining_amount"] == "0.00"


@pytest.mark.asyncio
async def test_reject_payment(client, admin_token, db_session):
    payment, _ = await _seed_registration_with_payment(db_session)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post(
        f"/api/v1/admin/payments/{payment.id}/reject",
        headers=headers,
        json={"reason": "فیش نامعتبر"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "failed"


@pytest.mark.asyncio
async def test_cannot_confirm_already_confirmed_payment(client, admin_token, db_session):
    payment, _ = await _seed_registration_with_payment(db_session)
    headers = {"Authorization": f"Bearer {admin_token}"}

    await client.post(f"/api/v1/admin/payments/{payment.id}/confirm", headers=headers, json={})
    second = await client.post(f"/api/v1/admin/payments/{payment.id}/confirm", headers=headers, json={})
    assert second.status_code == 400

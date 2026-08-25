import uuid

import pytest


@pytest.mark.asyncio
async def test_create_and_list_trip(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post(
        "/api/v1/admin/trips",
        headers=headers,
        json={
            "title": "تور تست",
            "destination": "شمال",
            "start_date": "2026-09-01T06:00:00Z",
            "end_date": "2026-09-03T20:00:00Z",
            "price": "1000000",
            "deposit_amount": "300000",
            "capacity": 10,
            "status": "published",
        },
    )
    assert create_resp.status_code == 201
    trip = create_resp.json()
    assert trip["remaining_capacity"] == 10

    # باید در endpoint عمومی User App هم دیده شود (یک دیتابیس مشترک واقعی)
    public_resp = await client.get("/api/v1/trips", params={"status": "published"})
    assert public_resp.status_code == 200
    assert public_resp.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_update_trip_capacity_below_taken_rejected(client, admin_token, db_session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post(
        "/api/v1/admin/trips",
        headers=headers,
        json={
            "title": "تور تست ۲",
            "destination": "جنوب",
            "start_date": "2026-09-01T06:00:00Z",
            "end_date": "2026-09-03T20:00:00Z",
            "price": "1000000",
            "deposit_amount": "300000",
            "capacity": 10,
        },
    )
    trip_id = create_resp.json()["id"]

    # به‌صورت مصنوعی ۸ نفر را «ثبت‌نام‌شده» فرض می‌کنیم (remaining=2)
    from src.models.trip import Trip

    trip = await db_session.get(Trip, uuid.UUID(trip_id))
    trip.remaining_capacity = 2
    await db_session.commit()

    # کاهش ظرفیت به کمتر از تعداد ثبت‌نام‌شده (10-2=8) باید رد شود
    update_resp = await client.put(
        f"/api/v1/admin/trips/{trip_id}", headers=headers, json={"capacity": 5}
    )
    assert update_resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_trip_with_registration_blocked(client, admin_token, db_session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post(
        "/api/v1/admin/trips",
        headers=headers,
        json={
            "title": "تور با ثبت‌نام",
            "destination": "شرق",
            "start_date": "2026-09-01T06:00:00Z",
            "end_date": "2026-09-03T20:00:00Z",
            "price": "1000000",
            "deposit_amount": "300000",
            "capacity": 10,
        },
    )
    trip_id = create_resp.json()["id"]

    from decimal import Decimal
    from datetime import datetime, timezone
    from src.models.user import User
    from src.models.registration import Registration
    from src.core.security import hash_password

    user = User(phone_number="+989121111111", full_name="کاربر", password_hash=hash_password("Pass12345"))
    db_session.add(user)
    await db_session.flush()

    registration = Registration(
        user_id=user.id,
        trip_id=uuid.UUID(trip_id),
        status="pending_payment",
        total_price=Decimal("1000000"),
        deposit_paid=Decimal("0"),
        remaining_amount=Decimal("1000000"),
        registered_at=datetime.now(timezone.utc),
    )
    db_session.add(registration)
    await db_session.commit()

    delete_resp = await client.delete(f"/api/v1/admin/trips/{trip_id}", headers=headers)
    assert delete_resp.status_code == 409

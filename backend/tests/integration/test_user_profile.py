import uuid

import pytest
from sqlalchemy import select

from src.core.deps import get_current_user
from src.main import app
from src.models import User
from src.models.user import UserProfile


@pytest.mark.asyncio
async def test_get_profile_when_none_exists(client, db_session):
    """کاربر بدون UserProfile — GET /me باید user را برگرداند و profile را null کند."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        phone_number="09123456789",
        email="user@example.com",
        full_name="کاربر تست",
        national_id="1234567890",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.get("/api/v1/users/me")

    assert response.status_code == 200
    body = response.json()
    assert body["profile"] is None
    assert body["user"]["id"] == str(user_id)
    assert body["user"]["phone_number"] == "09123456789"
    assert body["user"]["email"] == "user@example.com"
    assert body["user"]["full_name"] == "کاربر تست"
    assert body["user"]["national_id"] == "1234567890"
    assert body["user"]["is_active"] is True


@pytest.mark.asyncio
async def test_update_profile_creates_if_not_exists(client, db_session):
    """PATCH /me/profile بدون UserProfile موجود — باید پروفایل بسازد."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        phone_number="09123456790",
        full_name="کاربر تست",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.patch(
        "/api/v1/users/me/profile",
        json={
            "emergency_contact_name": "علی",
            "empty_seats": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["emergency_contact_name"] == "علی"
    assert body["empty_seats"] == 2
    assert body["vehicle_has_capacity"] is False

    # Verify persistence with a second GET
    get_response = await client.get("/api/v1/users/me")
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["profile"]["emergency_contact_name"] == "علی"
    assert get_body["profile"]["empty_seats"] == 2


@pytest.mark.asyncio
async def test_update_profile_partial_update(client, db_session):
    """PATCH فقط یک فیلد — بقیه‌ی فیلدها نباید تغییر کنند."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        phone_number="09123456791",
        full_name="کاربر تست",
        is_active=True,
    )
    profile = UserProfile(
        user_id=user_id,
        birth_date=None,
        emergency_contact_name="تماس قبلی",
        emergency_contact_phone="09111111111",
        medical_notes="یادداشت پزشکی قبلی",
        vehicle_has_capacity=True,
        empty_seats=3,
        profile_image_url=None,
        national_id_image_url=None,
    )
    db_session.add_all([user, profile])
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.patch(
        "/api/v1/users/me/profile",
        json={
            "emergency_contact_name": "تماس جدید",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["emergency_contact_name"] == "تماس جدید"
    assert body["emergency_contact_phone"] == "09111111111"
    assert body["medical_notes"] == "یادداشت پزشکی قبلی"
    assert body["vehicle_has_capacity"] is True
    assert body["empty_seats"] == 3

    # Verify the other fields are still unchanged in the database
    result = await db_session.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    saved_profile = result.scalar_one_or_none()
    assert saved_profile is not None
    assert saved_profile.emergency_contact_phone == "09111111111"
    assert saved_profile.medical_notes == "یادداشت پزشکی قبلی"
    assert saved_profile.vehicle_has_capacity is True
    assert saved_profile.empty_seats == 3


@pytest.mark.asyncio
async def test_upload_profile_image_success(client, db_session):
    """POST /me/profile_image با تصویر jpeg — 200 و profile_image_url صحیح."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        phone_number="09123456792",
        full_name="کاربر تست",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.post(
        "/api/v1/users/me/profile/image",
        files={"file": ("test.jpg", b"fake image content", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile_image_url"] is not None
    assert "/uploads/profile_images/" in body["profile_image_url"]
    assert body["emergency_contact_name"] is None  # no profile fields set yet
import pytest


@pytest.mark.asyncio
async def test_register_creates_inactive_user(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": "+989121234567",
            "full_name": "Test User",
            "password": "SuperSecret123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert "user_id" in body


@pytest.mark.asyncio
async def test_register_duplicate_phone_conflict(client):
    payload = {
        "phone_number": "+989121234567",
        "full_name": "Test User",
        "password": "SuperSecret123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_fails_for_inactive_user(client):
    """کاربر تازه‌ثبت‌نام‌شده تا وریفای OTP (Phase 2) غیرفعال است."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": "+989121234567",
            "full_name": "Test User",
            "password": "SuperSecret123",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone_number": "+989121234567", "password": "SuperSecret123"},
    )
    assert response.status_code == 403

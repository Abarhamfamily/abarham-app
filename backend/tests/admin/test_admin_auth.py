import pytest


@pytest.mark.asyncio
async def test_admin_login_success(client, seed_admin):
    response = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": "SuperSecret123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["admin"]["username"] == "admin"
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client, seed_admin):
    response = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": "WrongPassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_endpoint_requires_token(client):
    response = await client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_me(client, admin_token):
    response = await client.get(
        "/api/v1/admin/auth/me", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_user_token_rejected_on_admin_endpoint(client, seed_admin):
    """توکن یک کاربر عادی (User App) هرگز نباید روی endpoint های ادمین کار کند."""
    await client.post(
        "/api/v1/auth/register",
        json={"phone_number": "+989120000001", "full_name": "Normal User", "password": "UserPass123"},
    )
    # کاربر با OTP هنوز فعال نشده، پس مستقیم توکن جعلی از نوع اشتباه می‌سازیم
    # تا رفتار type mismatch را دقیق تست کنیم (سناریوی واقعی‌تر: توکن یک
    # کاربر واقعاً فعال که از core.security.create_access_token گرفته شده).
    from src.core.security import create_access_token

    fake_user_token = create_access_token("00000000-0000-0000-0000-000000000000")
    response = await client.get(
        "/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {fake_user_token}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_token_rejected_on_user_endpoint(client, admin_token):
    """توکن ادمین هرگز نباید روی endpoint های User App کار کند."""
    response = await client.get(
        "/api/v1/registrations/my", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401

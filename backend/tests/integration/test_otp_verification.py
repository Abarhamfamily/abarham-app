import pytest


@pytest.mark.asyncio
async def test_register_returns_otp_code_and_creates_inactive_user(client):
    """ثبت‌نام باید 201 برگرداند، otp_code ۶ رقمی در پاسخ باشد و کاربر غیرعالی باشد."""
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
    otp_code = body.get("otp_code", "")
    assert len(otp_code) == 6 and otp_code.isdigit(), f"otp_code should be 6 digits, got: {otp_code!r}"

    # Verify user is inactive in DB
    from sqlalchemy import select
    from src.models.user import User
    db = client._transport.app.dependency_overrides  # not used directly
    # Use the session from the client fixture via override
    # The override_get_db yields the same db_session used by the app
    # We can query through the app's dependency, but simpler: use the fixture's session
    # Actually we can get it from the app's dependency_overrides
    from src.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    # Get the overridden session
    override = client._transport.app.dependency_overrides.get(get_db)
    assert override is not None
    session = None
    async for s in override():
        session = s
        break
    assert session is not None

    result = await session.execute(select(User).where(User.phone_number == "+989121234567"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.is_active is False


@pytest.mark.asyncio
async def test_verify_otp_success_activates_user(client):
    """verify_otp با کد صحیح باید 200 برگرداند، token بدهد و کاربر را فعال کند."""
    # Register first
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": "+98987654321",
            "full_name": "Otp User",
            "password": "SuperSecret123",
        },
    )
    assert reg_resp.status_code == 201
    otp_code = reg_resp.json()["otp_code"]

    # Verify OTP
    verify_resp = await client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone_number": "+98987654321",
            "otp": otp_code,
        },
    )
    assert verify_resp.status_code == 200
    body = verify_resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert "user" in body
    assert body["user"]["is_active"] is True

    # Check DB
    from sqlalchemy import select
    from src.models.user import User
    from src.core.database import get_db

    override = client._transport.app.dependency_overrides.get(get_db)
    session = None
    async for s in override():
        session = s
        break
    result = await session.execute(select(User).where(User.phone_number == "+98987654321"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.is_active is True


@pytest.mark.asyncio
async def test_verify_otp_wrong_code_returns_400(client):
    """verify_otp با کد اشتباه باید 400 برگرداند و کاربر غیرعالی بماند."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": "+989111111111",
            "full_name": "Wrong Code User",
            "password": "SuperSecret123",
        },
    )
    assert reg_resp.status_code == 201

    verify_resp = await client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone_number": "+989111111111",
            "otp": "000000",
        },
    )
    assert verify_resp.status_code == 400

    # User still inactive
    from sqlalchemy import select
    from src.models.user import User
    from src.core.database import get_db

    override = client._transport.app.dependency_overrides.get(get_db)
    session = None
    async for s in override():
        session = s
        break
    result = await session.execute(select(User).where(User.phone_number == "+989111111111"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.is_active is False


@pytest.mark.asyncio
async def test_verify_otp_already_active_returns_400(client):
    """پس از verify موفق، دوباره verify-otp باید 400 برگرداند (account already active)."""
    phone = "+989222222222"
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "full_name": "Double Verify User",
            "password": "SuperSecret123",
        },
    )
    assert reg_resp.status_code == 201
    otp_code = reg_resp.json()["otp_code"]

    # First verify succeeds
    first = await client.post(
        "/api/v1/auth/verify-otp",
        json={"phone_number": phone, "otp": otp_code},
    )
    assert first.status_code == 200

    # Second verify should fail with 400
    second = await client.post(
        "/api/v1/auth/verify-otp",
        json={"phone_number": phone, "otp": otp_code},
    )
    assert second.status_code == 400
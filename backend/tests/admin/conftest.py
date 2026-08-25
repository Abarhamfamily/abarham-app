"""
Fixture های اختصاصی تست‌های Admin Panel.

نکته‌ی مهم: در پروژه‌ی واقعی، include_router روتر ادمین باید طبق
INTEGRATION.md به‌صورت دستی به src/main.py اضافه شود (این deliverable هیچ
فایل موجودی را تغییر نمی‌دهد). برای تست، همان app واقعی را می‌گیریم و
روتر ادمین را در حافظه (فقط برای دوره‌ی تست) روی آن سوار می‌کنیم — این
دقیقاً همان کاری است که کاربر باید در main.py واقعی انجام دهد.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.database import Base, get_db
from src.core.security import hash_password
from src.main import app
from src.models.admin import Admin, AdminRole
from src.api.v1.admin import router as admin_router

# ایمپورت همه‌ی مدل‌ها (شامل admin) تا Base.metadata کامل باشد
from src import models  # noqa: F401

if not any(getattr(r, "prefix", "") == "/api/v1/admin" for r in app.routes):
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_admin(db_session):
    """یک ادمین آماده با رمز شناخته‌شده برای استفاده در تست‌ها می‌سازد."""
    admin = Admin(
        username="admin",
        full_name="Test Admin",
        password_hash=hash_password("SuperSecret123"),
        role=AdminRole.SUPER_ADMIN.value,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def admin_token(client, seed_admin):
    response = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": "SuperSecret123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

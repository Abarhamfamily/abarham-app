import asyncio
from sqlalchemy import select

# Async session factory, engine and Base from the project
from src.core.database import AsyncSessionLocal, engine, Base
from src.models.user import User
from src.core.security import hash_password

PHONE_NUMBER = "+989120000001"
FULL_NAME = "Test User Flutter"
RAW_PASSWORD = "Test@1234"

async def ensure_tables():
    """Create tables if they do not exist (runs Alembic equivalent for tests)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main() -> None:
    # Make sure the DB schema exists
    await ensure_tables()

    async with AsyncSessionLocal() as session:
        # Check for existing user
        result = await session.execute(select(User).where(User.phone_number == PHONE_NUMBER))
        existing = result.scalars().first()
        if existing:
            print("کاربر از قبل وجود دارد")
            return

        # Insert new test user
        user = User(
            phone_number=PHONE_NUMBER,
            full_name=FULL_NAME,
            password_hash=hash_password(RAW_PASSWORD),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print("کاربر تست با موفقیت ساخته شد")

if __name__ == "__main__":
    asyncio.run(main())

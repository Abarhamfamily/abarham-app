import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from src.core.database import AsyncSessionLocal
from src.models.trip import Trip


async def seed_trip():
    async with AsyncSessionLocal() as db:
        trip = Trip(
            title="تور آزمایشی ابرهام",
            destination="جنگل‌های شمال",
            description="این یک تور آزمایشی برای اتصال Frontend به Backend است.",
            start_date=datetime.now() + timedelta(days=30),
            end_date=datetime.now() + timedelta(days=32),
            price=Decimal("5000000.00"),
            deposit_amount=Decimal("1250000.00"),
            capacity=20,
            remaining_capacity=20,
            version=1,
            status="published",
            transportation_type="personal_car",
            difficulty_level="easy",
            accommodation_info="Camping",
            meeting_point="تهران",
            departure_time="06:00",
            requirements=None,
            rules=None,
            cancellation_policy=None,
            image_urls=None,
        )

        db.add(trip)
        await db.commit()
        await db.refresh(trip)

        print(f"Trip created: {trip.id}")
        print(f"Title: {trip.title}")


if __name__ == "__main__":
    asyncio.run(seed_trip())
import asyncio
from decimal import Decimal
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.models.user import User
from src.models.wallet import Wallet
from src.models.trip import Trip


async def main():
    async with AsyncSessionLocal() as session:
        user = await session.scalar(
            select(User).where(User.phone_number == '+989120000001')
        )
        if not user:
            print('کاربر تست پیدا نشد.')
            return

        wallet = await session.scalar(
            select(Wallet).where(Wallet.user_id == user.id)
        )
        if not wallet:
            wallet = Wallet(
                user_id=user.id,
                balance=Decimal('5000000'),
                pending_balance=Decimal('0'),
                total_deposited=Decimal('5000000'),
                total_withdrawn=Decimal('0'),
                version=1,
            )
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            print('کیف پول جدید ساخته شد.')
        else:
            print(f'کیف پول از قبل وجود دارد، موجودی فعلی: {wallet.balance}')

        trip = await session.scalar(
            select(Trip).where(Trip.title == 'تور آزمایشی ابرهام')
        )
        if not trip:
            print('تور تستی پیدا نشد.')
            return

        if trip.other_vehicle_price is None:
            trip.other_vehicle_price = Decimal('500000')
            await session.commit()
            await session.refresh(trip)
            print('قیمت other_vehicle_price به‌روزرسانی شد.')
        else:
            print(f'قیمت other_vehicle_price از قبل تنظیم شده: {trip.other_vehicle_price}')

        print(f'\nموجودی نهایی کیف پول: {wallet.balance}')
        print(f'قیمت other_vehicle_price تور: {trip.other_vehicle_price}')


if __name__ == '__main__':
    asyncio.run(main())
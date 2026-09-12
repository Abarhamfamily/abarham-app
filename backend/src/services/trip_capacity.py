from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..models.trip import Trip


async def try_decrement_trip_capacity(
    db: AsyncSession,
    trip_id: UUID,
    current_version: int,
    passenger_count: int,
) -> bool:
    """
    تلاش برای کاهش ظرفیت باقی‌مانده‌ی تور با استفاده از optimistic locking.

    این تابع commit یا rollback نمی‌کند — مسئولیت تراکنش با فراخواننده است.
    فقط UPDATE را در session اجرا می‌کند و نتیجه (موفق/ناموفق) را برمی‌گرداند.

    Returns:
        True اگر به‌روزرسانی موفق بود (یعنی هنوز ظرفیت کافی و version درست بود).
        False اگر به‌دلیل تغییر version (توسط یک درخواست هم‌زمان دیگر) یا کمبود ظرفیت، به‌روزرسانی هیچ ردیفی را تحت تأثیر قرار نداد.
    """
    result = await db.execute(
        update(Trip)
        .where(
            Trip.id == trip_id,
            Trip.remaining_capacity >= passenger_count,
            Trip.version == current_version,
        )
        .values(
            remaining_capacity=Trip.remaining_capacity - passenger_count,
            version=Trip.version + 1,
        )
    )
    return result.rowcount > 0
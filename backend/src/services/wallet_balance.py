from decimal import Decimal
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.wallet import Wallet


async def try_decrement_wallet_balance(
    db: AsyncSession,
    user_id: UUID,
    current_version: int,
    amount: Decimal,
) -> bool:
    """
    تلاش برای کاهش موجودی کیف پول کاربر با استفاده از optimistic locking.

    این تابع commit یا rollback نمی‌کند — مسئولیت تراکنش با فراخواننده است.

    Returns:
        True اگر به‌روزرسانی موفق بود (یعنی موجودی کافی و version درست بود).
        False اگر به‌دلیل تغییر version یا کمبود موجودی، به‌روزرسانی هیچ ردیفی را تحت تأثیر قرار نداد.
    """
    result = await db.execute(
        update(Wallet)
        .where(
            Wallet.user_id == user_id,
            Wallet.balance >= amount,
            Wallet.version == current_version,
        )
        .values(
            balance=Wallet.balance - amount,
            version=Wallet.version + 1,
        )
    )
    return result.rowcount > 0


async def try_increment_wallet_balance(
    db: AsyncSession,
    user_id: UUID,
    current_version: int,
    amount: Decimal,
) -> bool:
    """
    تلاش برای افزایش موجودی کیف پول کاربر با استفاده از optimistic locking.

    این تابع commit یا rollback نمی‌کند — مسئولیت تراکنش با فراخواننده است.

    Returns:
        True اگر به‌روزرسانی موفق بود (یعنی version درست بود).
        False اگر به‌دلیل تغییر version، به‌روزرسانی هیچ ردیفی را تحت تأثیر قرار نداد.
    """
    result = await db.execute(
        update(Wallet)
        .where(
            Wallet.user_id == user_id,
            Wallet.version == current_version,
        )
        .values(
            balance=Wallet.balance + amount,
            total_deposited=Wallet.total_deposited + amount,
            version=Wallet.version + 1,
        )
    )
    return result.rowcount > 0
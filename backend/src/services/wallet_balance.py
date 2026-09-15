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


async def try_reserve_wallet_balance(
    db: AsyncSession,
    user_id: UUID,
    current_version: int,
    amount: Decimal,
) -> bool:
    """
    تلاش برای رزرو بخشی از موجودی کیف پول کاربر (انتقال از balance به
    pending_balance) هنگام ثبت درخواست برداشت، با استفاده از optimistic locking.

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
            pending_balance=Wallet.pending_balance + amount,
            version=Wallet.version + 1,
        )
    )
    return result.rowcount > 0


async def try_release_wallet_balance(
    db: AsyncSession,
    user_id: UUID,
    current_version: int,
    amount: Decimal,
) -> bool:
    """
    تلاش برای آزادسازی مبلغ رزروشده (بازگرداندن از pending_balance به balance)
    هنگام رد درخواست برداشت توسط ادمین، با استفاده از optimistic locking.

    این تابع commit یا rollback نمی‌کند — مسئولیت تراکنش با فراخواننده است.

    Returns:
        True اگر به‌روزرسانی موفق بود.
        False اگر به‌دلیل تغییر version یا کمبود pending_balance، هیچ ردیفی تحت تأثیر قرار نگرفت.
    """
    result = await db.execute(
        update(Wallet)
        .where(
            Wallet.user_id == user_id,
            Wallet.pending_balance >= amount,
            Wallet.version == current_version,
        )
        .values(
            balance=Wallet.balance + amount,
            pending_balance=Wallet.pending_balance - amount,
            version=Wallet.version + 1,
        )
    )
    return result.rowcount > 0

from decimal import Decimal
from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.payment import Payment, PaymentType, PaymentStatus


def generate_deposit_idempotency_key(registration_id: UUID) -> str:
    """کلید idempotency برای پرداخت بیعانه‌ی یک ثبت‌نام مشخص را تولید می‌کند."""
    return f"registration:{registration_id}:deposit"


async def get_or_create_deposit_payment(
    db: AsyncSession,
    registration_id: UUID,
    user_id: UUID,
    amount: Decimal,
) -> tuple[Payment, bool]:
    """
    اگر یک Payment با idempotency_key متناظر با این registration از قبل وجود داشته باشد،
    همان را برمی‌گرداند (بدون ساخت رکورد جدید).
    در غیر این صورت، یک Payment جدید (در حالت PENDING) می‌سازد و به session اضافه می‌کند
    (بدون commit — مسئولیت تراکنش با فراخواننده است).

    Returns:
        tuple (payment, was_created):
            payment: شیء Payment (موجود یا تازه‌ساخته‌شده)
            was_created: True اگر تازه ساخته شده، False اگر از قبل وجود داشته
    """
    key = generate_deposit_idempotency_key(registration_id)

    result = await db.execute(select(Payment).where(Payment.idempotency_key == key))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing, False

    payment = Payment(
        registration_id=registration_id,
        user_id=user_id,
        amount=amount,
        type=PaymentType.DEPOSIT.value,
        status=PaymentStatus.PENDING.value,
        idempotency_key=key,
    )
    db.add(payment)
    return payment, True
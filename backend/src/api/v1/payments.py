from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.payment import Payment, PaymentType, PaymentStatus
from ...models.registration import Registration, RegistrationStatus
from ...models.user import User
from ...models.wallet import Wallet
from ...schemas.payment import (
    PaymentCreateRequest,
    PaymentCreateResponse,
    PaymentOut,
    UploadReceiptResponse,
    ConfirmPaymentRequest,
)
from ...services.wallet_balance import try_decrement_wallet_balance

router = APIRouter()


@router.post("", response_model=PaymentCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing_result = await db.execute(
        select(Payment).where(Payment.idempotency_key == payload.idempotency_key)
    )
    existing_payment = existing_result.scalar_one_or_none()
    if existing_payment is not None:
        return PaymentCreateResponse(
            payment=PaymentOut.model_validate(existing_payment),
            status="already_processed",
        )

    registration = await db.get(Registration, payload.registration_id)
    if not registration or registration.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام یافت نشد")

    if registration.status == RegistrationStatus.CANCELLED.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "این ثبت‌نام لغوشده است")

    if registration.remaining_amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "این ثبت‌نام بدهی باقی‌مانده‌ای ندارد")

    if payload.amount != registration.remaining_amount:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "مبلغ ارسالی باید دقیقاً برابر مبلغ باقی‌مانده‌ی ثبت‌نام باشد",
        )

    wallet_result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = wallet_result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "کیف پول یافت نشد")

    decremented = await try_decrement_wallet_balance(
        db=db,
        user_id=current_user.id,
        current_version=wallet.version,
        amount=payload.amount,
    )
    if not decremented:
        await db.rollback()
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "موجودی کیف پول کافی نیست")

    now = datetime.now(timezone.utc)

    payment = Payment(
        registration_id=registration.id,
        user_id=current_user.id,
        amount=payload.amount,
        type=PaymentType.REMAINING.value,
        status=PaymentStatus.CONFIRMED.value,
        method="wallet",
        idempotency_key=payload.idempotency_key,
        confirmed_at=now,
    )
    db.add(payment)

    registration.deposit_paid = registration.deposit_paid + payload.amount
    registration.remaining_amount = registration.remaining_amount - payload.amount
    if registration.remaining_amount <= 0:
        registration.status = RegistrationStatus.CONFIRMED.value
        registration.confirmed_at = now

    await db.commit()
    await db.refresh(payment)

    return PaymentCreateResponse(
        payment=PaymentOut.model_validate(payment),
        status="paid",
    )


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payment = await db.get(Payment, payment_id)
    if not payment or payment.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "پرداخت یافت نشد")
    return PaymentOut.model_validate(payment)


@router.post("/{payment_id}/upload-receipt", response_model=UploadReceiptResponse)
async def upload_receipt(
    payment_id: UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO (Phase 6): ذخیره فایل روی STORAGE_TYPE پیکربندی‌شده (local/S3)
    # و ثبت receipt_url روی رکورد Payment.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Receipt upload not implemented yet — Phase 6",
    )


@router.post("/{payment_id}/confirm")
async def confirm_payment(
    payment_id: UUID,
    payload: ConfirmPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO (Phase 6): این اندپوینت باید محدود به ادمین باشد (نه کاربر عادی)
    # و باید Registration.status را در صورت تکمیل مبلغ به CONFIRMED تغییر دهد.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Payment confirmation not implemented yet — Phase 6",
    )

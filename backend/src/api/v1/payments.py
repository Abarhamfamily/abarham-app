from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.payment import Payment
from ...schemas.payment import (
    PaymentCreateRequest,
    PaymentCreateResponse,
    PaymentOut,
    UploadReceiptResponse,
    ConfirmPaymentRequest,
)

router = APIRouter()


@router.post("", response_model=PaymentCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO (Phase 6): پیاده‌سازی PaymentService.create_payment طبق Section H:
    #   1. بررسی idempotency_key (جدول payment_idempotency یا ستون unique).
    #   2. اعتبارسنجی این‌که amount دقیقاً برابر با بیعانه یا مبلغ باقی‌مانده‌ی
    #      Registration است (Payment Isolation).
    #   3. ثبت Payment و به‌روزرسانی Registration.deposit_paid درون یک تراکنش واحد.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Payment creation not implemented yet — Phase 6",
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

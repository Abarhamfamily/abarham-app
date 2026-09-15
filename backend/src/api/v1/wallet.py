from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.wallet import TransactionType, TransactionStatus
from ...models.wallet import Wallet, Transaction
from ...schemas.wallet import (
    WalletOut,
    TransactionOut,
    WalletDepositRequest,
    WalletWithdrawRequest,
    WalletChargeRequest,
    WalletChargeResponse,
    WalletChargeVerifyResponse,
)
from ...services.payment_gateway import create_payment_request, verify_payment
from ...services.wallet_balance import try_increment_wallet_balance, try_reserve_wallet_balance

router = APIRouter()


@router.get("", response_model=WalletOut)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        # هر کاربر با اولین برخورد یک کیف پول خالی دریافت می‌کند
        wallet = Wallet(user_id=current_user.id)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    return WalletOut.model_validate(wallet)


@router.get("/transactions", response_model=list[TransactionOut])
async def list_transactions(
    type_filter: Optional[str] = Query(None, alias="type"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = wallet_result.scalar_one_or_none()
    if not wallet:
        return []

    query = select(Transaction).where(Transaction.wallet_id == wallet.id)
    if type_filter:
        query = query.where(Transaction.type == type_filter)
    if from_date:
        query = query.where(Transaction.created_at >= from_date)
    if to_date:
        query = query.where(Transaction.created_at <= to_date)

    result = await db.execute(
        query.order_by(Transaction.created_at.desc()).limit(limit).offset(offset)
    )
    return [TransactionOut.model_validate(t) for t in result.scalars().all()]


@router.post("/deposit", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def deposit(
    payload: WalletDepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO (Phase 5): پیاده‌سازی WalletService با قفل ردیف (SELECT ... FOR
    # UPDATE) روی Wallet برای جلوگیری از race condition، طبق Section I.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Wallet deposit not implemented yet — Phase 5",
    )


@router.post("/withdraw", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def withdraw(
    payload: WalletWithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "مبلغ برداشت باید مثبت باشد")

    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "کیف پول یافت نشد")

    max_withdrawable = wallet.balance * Decimal("0.8")
    if payload.amount > max_withdrawable:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "شما تنها می‌توانید تا ۸۰٪ موجودی کیف پول خود را برداشت کنید",
        )

    existing_pending = await db.execute(
        select(Transaction).where(
            Transaction.wallet_id == wallet.id,
            Transaction.type == TransactionType.WITHDRAWAL.value,
            Transaction.status == TransactionStatus.PENDING.value,
        )
    )
    if existing_pending.scalar_one_or_none() is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "یک درخواست برداشت دیگر از شما در حال بررسی است",
        )

    reserved = await try_reserve_wallet_balance(
        db=db,
        user_id=current_user.id,
        current_version=wallet.version,
        amount=payload.amount,
    )
    if not reserved:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "خطا در رزرو موجودی، لطفاً دوباره تلاش کنید",
        )

    transaction = Transaction(
        wallet_id=wallet.id,
        amount=payload.amount,
        type=TransactionType.WITHDRAWAL.value,
        status=TransactionStatus.PENDING.value,
        description=f"درخواست برداشت به کارت {payload.card_number}",
        transaction_metadata={"card_number": payload.card_number},
        created_at=datetime.now(timezone.utc),
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return TransactionOut.model_validate(transaction)


@router.post("/charge", response_model=WalletChargeResponse, status_code=status.HTTP_201_CREATED)
async def charge_wallet(
    payload: WalletChargeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=current_user.id)
        db.add(wallet)
        await db.flush()

    gateway_info = create_payment_request(
        amount=payload.amount,
        description="شارژ کیف پول آبرهام",
    )

    transaction = Transaction(
        wallet_id=wallet.id,
        amount=payload.amount,
        type=TransactionType.DEPOSIT.value,
        status=TransactionStatus.PENDING.value,
        description="شارژ کیف پول (در انتظار تأیید درگاه)",
        transaction_metadata={"authority": gateway_info["authority"]},
        created_at=datetime.now(timezone.utc),
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return WalletChargeResponse(
        transaction_id=transaction.id,
        payment_url=gateway_info["payment_url"],
        authority=gateway_info["authority"],
    )


@router.post("/charge/{transaction_id}/verify", response_model=WalletChargeVerifyResponse)
async def verify_wallet_charge(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    transaction = await db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تراکنش یافت نشد")

    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = wallet_result.scalar_one_or_none()
    if not wallet or transaction.wallet_id != wallet.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "تراکنش یافت نشد")

    if transaction.status != TransactionStatus.PENDING.value:
        return WalletChargeVerifyResponse(
            success=transaction.status == TransactionStatus.CONFIRMED.value,
            message="این تراکنش قبلاً پردازش شده است",
            wallet=WalletOut.model_validate(wallet),
        )

    authority = (transaction.transaction_metadata or {}).get("authority", "")
    is_verified = verify_payment(authority)

    if is_verified:
        incremented = await try_increment_wallet_balance(
            db=db,
            user_id=current_user.id,
            current_version=wallet.version,
            amount=transaction.amount,
        )
        if not incremented:
            await db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "خطا در به‌روزرسانی موجودی، لطفاً دوباره تلاش کنید",
            )
        transaction.status = TransactionStatus.CONFIRMED.value
        transaction.confirmed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(wallet)

        return WalletChargeVerifyResponse(
            success=True,
            message="شارژ کیف پول با موفقیت انجام شد",
            wallet=WalletOut.model_validate(wallet),
        )
    else:
        transaction.status = TransactionStatus.FAILED.value
        await db.commit()

        return WalletChargeVerifyResponse(
            success=False,
            message="پرداخت تأیید نشد",
            wallet=None,
        )

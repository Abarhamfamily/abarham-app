from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.wallet import Wallet, Transaction
from ...schemas.wallet import WalletOut, TransactionOut, WalletDepositRequest, WalletWithdrawRequest

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
    # TODO (Phase 5): باید balance >= amount را قبل از هر برداشت با قفل
    # بررسی کند (طبق تست test_concurrent_withdrawals_prevent_overdraft در
    # Section J).
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Wallet withdrawal not implemented yet — Phase 5",
    )

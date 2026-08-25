from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.admin_security import get_current_admin
from ....models.admin import Admin
from ....models.user import User
from ....models.wallet import Wallet, Transaction, TransactionType, TransactionStatus
from ....schemas.admin_wallet import (
    AdminWalletOut,
    AdminWalletListResponse,
    AdminWalletListMeta,
    AdminTransactionOut,
    AdminWalletAdjustRequest,
)

router = APIRouter()


def _to_out(wallet: Wallet, user: Optional[User]) -> AdminWalletOut:
    out = AdminWalletOut.model_validate(wallet)
    out.user_full_name = user.full_name if user else None
    out.user_phone_number = user.phone_number if user else None
    return out


@router.get("", response_model=AdminWalletListResponse)
async def list_wallets(
    search: Optional[str] = Query(None, description="جست‌وجو در نام یا شماره تماس کاربر"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Wallet, User).join(User, Wallet.user_id == User.id)
    count_query = select(func.count()).select_from(Wallet)

    if search:
        pattern = f"%{search}%"
        condition = User.full_name.ilike(pattern) | User.phone_number.ilike(pattern)
        query = query.join(User, Wallet.user_id == User.id).where(condition)
        count_query = count_query.join(User, Wallet.user_id == User.id).where(condition)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.order_by(Wallet.updated_at.desc()).limit(limit).offset(offset))
    rows = result.all()

    return AdminWalletListResponse(
        data=[_to_out(wallet, user) for wallet, user in rows],
        meta=AdminWalletListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{wallet_id}/transactions", response_model=list[AdminTransactionOut])
async def list_wallet_transactions(
    wallet_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    wallet = await db.get(Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "کیف پول یافت نشد")

    result = await db.execute(
        select(Transaction)
        .where(Transaction.wallet_id == wallet_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [AdminTransactionOut.model_validate(t) for t in result.scalars().all()]


@router.post("/{wallet_id}/adjust", response_model=AdminTransactionOut, status_code=status.HTTP_201_CREATED)
async def adjust_wallet(
    wallet_id: UUID,
    payload: AdminWalletAdjustRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    تعدیل دستی موجودی کیف پول توسط ادمین (مثلاً بازگشت وجه دستی یا اصلاح
    خطای مالی). طبق Section I مستند معماری، موجودی هرگز مستقیم تغییر
    نمی‌کند و همیشه یک رکورد Transaction ثبت می‌شود.

    نکته درباره‌ی همزمانی: چون این یک اقدام تکی و دستی توسط ادمین است (نه
    عملیات با نرخ بالا و همزمان کاربران که در WalletService.use_credit
    نیاز به SELECT...FOR UPDATE دارد)، همین سطح از حفاظت (بررسی مستقیم قبل
    از commit) برای این مسیر مدیریتی کافی است.
    """
    wallet = await db.get(Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "کیف پول یافت نشد")

    new_balance = wallet.balance + payload.amount
    if new_balance < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "موجودی کیف پول نمی‌تواند منفی شود")

    wallet.balance = new_balance
    if payload.amount > 0:
        wallet.total_deposited = wallet.total_deposited + payload.amount
    else:
        wallet.total_withdrawn = wallet.total_withdrawn + (-payload.amount)
    wallet.version += 1

    transaction = Transaction(
        wallet_id=wallet.id,
        amount=payload.amount,
        type=TransactionType.ADJUSTMENT.value,
        status=TransactionStatus.CONFIRMED.value,
        description=f"[ادمین: {current_admin.username}] {payload.description}",
        created_at=datetime.now(timezone.utc),
        confirmed_at=datetime.now(timezone.utc),
    )
    db.add(transaction)

    await db.commit()
    await db.refresh(transaction)
    return AdminTransactionOut.model_validate(transaction)

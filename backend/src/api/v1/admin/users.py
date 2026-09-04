from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....core.database import get_db
from ....core.admin_security import get_current_admin
from ....models.admin import Admin
from ....models.user import User
from ....schemas.admin_users import (
    AdminUserOut,
    AdminUserDetailOut,
    AdminUserListResponse,
    AdminUserListMeta,
    AdminUserUpdateRequest,
)

router = APIRouter()


@router.get("", response_model=AdminUserListResponse)
async def list_users(
    search: Optional[str] = Query(None, description="جست‌وجو در نام، شماره تماس یا کد ملی"),
    is_active: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)
    count_query = select(func.count()).select_from(User)

    if search:
        pattern = f"%{search}%"
        condition = or_(
            User.full_name.ilike(pattern),
            User.phone_number.ilike(pattern),
            User.national_id.ilike(pattern),
        )
        query = query.where(condition)
        count_query = count_query.where(condition)

    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(
        query.order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    users = result.scalars().all()

    return AdminUserListResponse(
        data=[AdminUserOut.model_validate(u) for u in users],
        meta=AdminUserListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{user_id}", response_model=AdminUserDetailOut)
async def get_user(
    user_id: UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "کاربر یافت نشد")
    return AdminUserDetailOut.model_validate(user)


@router.patch("/{user_id}", response_model=AdminUserOut)
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "کاربر یافت نشد")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return AdminUserOut.model_validate(user)

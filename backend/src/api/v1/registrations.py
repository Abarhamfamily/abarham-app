from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.registration import Registration
from ...schemas.registration import (
    RegistrationCreateRequest,
    RegistrationCreateResponse,
    RegistrationOut,
)

router = APIRouter()


@router.post("", response_model=RegistrationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    payload: RegistrationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO (Phase 4): پیاده‌سازی RegistrationService طبق Section H/Section N:
    #   1. جلوگیری از ثبت‌نام تکراری (UNIQUE constraint موجود است، اما پیام
    #      خطای مناسب باید در سرویس مدیریت شود).
    #   2. قفل خوش‌بینانه (optimistic locking) روی Trip.version برای جلوگیری
    #      از overbooking در شرایط همزمانی بالا.
    #   3. اگر ظرفیت پر بود، افزودن به Waitlist به‌جای خطا.
    #   4. ساخت رکورد Payment بیعانه (deposit) هم‌زمان با ثبت‌نام.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Registration creation not implemented yet — Phase 4",
    )


@router.get("/my", response_model=list[RegistrationOut])
async def list_my_registrations(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Registration).where(Registration.user_id == current_user.id)
    if status_filter:
        query = query.where(Registration.status == status_filter)

    result = await db.execute(query.order_by(Registration.registered_at.desc()))
    registrations = result.scalars().all()
    return [RegistrationOut.model_validate(r) for r in registrations]


@router.get("/{registration_id}", response_model=RegistrationOut)
async def get_registration(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    registration = await db.get(Registration, registration_id)
    if not registration or registration.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ثبت‌نام یافت نشد")
    return RegistrationOut.model_validate(registration)


@router.delete("/{registration_id}")
async def cancel_registration(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO (Phase 4): لغو ثبت‌نام باید ظرفیت تور را آزاد کند (با همان قفل
    # خوش‌بینانه) و در صورت وجود Waitlist، نفر بعدی را مطلع کند.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Registration cancellation not implemented yet — Phase 4",
    )

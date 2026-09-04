"""
تمام روترهای پنل مدیریت اینجا در یک APIRouter واحد جمع می‌شوند تا افزودن
آن‌ها به main.py فقط به یک import و یک include_router نیاز داشته باشد
(به INTEGRATION.md مراجعه کنید).
"""
from fastapi import APIRouter

from . import auth, dashboard, users, trips, registrations, payments, wallet, notifications

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["admin-auth"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["admin-dashboard"])
router.include_router(users.router, prefix="/users", tags=["admin-users"])
router.include_router(trips.router, prefix="/trips", tags=["admin-trips"])
router.include_router(registrations.router, prefix="/registrations", tags=["admin-registrations"])
router.include_router(payments.router, prefix="/payments", tags=["admin-payments"])
router.include_router(wallet.router, prefix="/wallet", tags=["admin-wallet"])
router.include_router(notifications.router, prefix="/notifications", tags=["admin-notifications"])

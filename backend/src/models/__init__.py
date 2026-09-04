"""
همه‌ی مدل‌های SQLAlchemy را اینجا ایمپورت می‌کنیم تا:
1. Alembic بتواند همه‌ی جدول‌ها را برای autogenerate کشف کند.
2. جای واحدی برای ایمپورت مدل‌ها در بقیه‌ی پروژه وجود داشته باشد.
"""

from .user import User, UserProfile
from .trip import Trip, TripStatus
from .registration import Registration, RegistrationStatus
from .waitlist import Waitlist, WaitlistStatus
from .wallet import Wallet, Transaction, TransactionType, TransactionStatus
from .payment import Payment, PaymentType, PaymentStatus
from .notification import Notification
from .audit import AuditLog

__all__ = [
    "User",
    "UserProfile",
    "Trip",
    "TripStatus",
    "Registration",
    "RegistrationStatus",
    "Waitlist",
    "WaitlistStatus",
    "Wallet",
    "Transaction",
    "TransactionType",
    "TransactionStatus",
    "Payment",
    "PaymentType",
    "PaymentStatus",
    "Notification",
    "AuditLog",
]

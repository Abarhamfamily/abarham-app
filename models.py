import os
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel, create_engine


# ---------------------------------------------------------------------------
# مدل تور
# ---------------------------------------------------------------------------
class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None          # تاریخ برگزاری (مثلاً ۱۴۰۵/۰۵/۲۱)
    price: float = 0.0
    capacity: int = 0                   # ظرفیت تور (۰ یعنی نامحدود)
    telegram_group_link: Optional[str] = None   # لینک گروه هماهنگی تلگرام سفر
    status: str = "active"              # "active" | "completed"


# ---------------------------------------------------------------------------
# مدل مسافر / شرکت‌کننده
# ---------------------------------------------------------------------------
class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    national_id: str
    phone_number: str
    trip_id: int = Field(foreign_key="trip.id")
    telegram_user_id: Optional[int] = None   # شناسه کاربر تلگرام (برای پرداخت)
    payment_status: str = "پرداخت بیعانه"   # یا "پرداخت کامل"
    paid_amount: float = 0.0


# ---------------------------------------------------------------------------
# مدل پرداخت
# ---------------------------------------------------------------------------
class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    participant_id: int = Field(foreign_key="participant.id")
    trip_id: int = Field(foreign_key="trip.id")
    telegram_user_id: int
    payment_type: str                                    # "deposit" | "full"
    expected_amount: float                               # snapshot مبلغ در لحظه ثبت
    receipt_file_id: str                                 # file_id تلگرام (الزامی)
    receipt_file_unique_id: Optional[str] = None
    receipt_local_path: Optional[str] = None             # "receipts/receipt_<uuid>.jpg"
    status: str = "pending_review"                       # pending_review | confirmed | rejected
    created_at: str
    reviewed_at: Optional[str] = None
    review_note: Optional[str] = None


# ---------------------------------------------------------------------------
# مدل لاگ‌یادآوری (برای جلوگیری از ارسال تکراری پیام‌های زمان‌بندی‌شده)
# ---------------------------------------------------------------------------
class ReminderLog(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "participant_id",
            "trip_id",
            "reminder_type",
            name="uq_reminder_once",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    participant_id: int = Field(foreign_key="participant.id")
    trip_id: int = Field(foreign_key="trip.id")
    reminder_type: str       # "group_link_4_days" | "payment_10_days" | "payment_7_days"
    sent_at: str             # ISO datetime


# ---------------------------------------------------------------------------
# تنظیمات دیتابیس (یک منبع واحد؛ همه‌ی فایل‌ها این engine را ایمپورت می‌کنند)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./abarham.db")

# Render مقدار DATABASE_URL رو با پیشوند "postgres://" می‌ده، ولی SQLAlchemy 1.4+
# پیشوند "postgresql://" رو می‌خواد. این خط این ناسازگاری رو خودکار درست می‌کند.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# آرگومان check_same_thread فقط برای SQLite لازم است؛ برای PostgreSQL نباید پاس داده شود.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

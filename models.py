import os
from typing import Optional

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


# ---------------------------------------------------------------------------
# مدل مسافر / شرکت‌کننده
# ---------------------------------------------------------------------------
class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    national_id: str
    phone_number: str
    trip_id: int = Field(foreign_key="trip.id")
    payment_status: str = "پرداخت بیعانه"   # یا "پرداخت کامل"
    paid_amount: float = 0.0


# ---------------------------------------------------------------------------
# تنظیمات دیتابیس (یک منبع واحد؛ همه‌ی فایل‌ها این engine را ایمپورت می‌کنند)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./abarham.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

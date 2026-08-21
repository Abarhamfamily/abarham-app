import asyncio
import logging
from datetime import datetime, timedelta

import jdatetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models import engine, Trip, Participant, ReminderLog
from payment import is_fully_paid

logger = logging.getLogger("abarham.reminders")

# برای تبدیل اعداد فارسی/عربی به انگلیسی
_FARSI_TO_WEST = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def parse_jalali(date_str: str) -> datetime:
    """تبدیل تاریخ شمسی با پشتیبانی از YYYY/MM/DD و DD/MM/YYYY."""
    cleaned = date_str.strip().translate(_FARSI_TO_WEST)
    parts = [p.strip() for p in cleaned.split("/")]

    if len(parts) != 3:
        raise ValueError(f"فرمت تاریخ نامعتبر: {date_str}")

    if len(parts[0]) == 4:
        # YYYY/MM/DD
        year, month, day = parts
    elif len(parts[2]) == 4:
        # DD/MM/YYYY
        day, month, year = parts
    else:
        raise ValueError(f"سال در تاریخ یافت نشد: {date_str}")

    jd = jdatetime.date(int(year), int(month), int(day))
    g = jd.togregorian()

    return datetime(g.year, g.month, g.day)

async def send_group_link_reminders(bot):
    """ارسال لینک گروه هماهنگی ۴ روز قبل از سفر به مسافران واجدشرایط."""
    now = datetime.now()

    with Session(engine) as session:
        trips = session.exec(
            select(Trip).where(
                Trip.status == "active",
                Trip.telegram_group_link.isnot(None),
                Trip.date.isnot(None),
            )
        ).all()

        for trip in trips:
            # تبدیل تاریخ سفر
            try:
                trip_date = parse_jalali(trip.date)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"⚠️ تاریخ نامعتبر تور {trip.id}: {trip.date} — {e}"
                )
                continue

            # شرط: امروز >= ۴ روز قبل از سفر و هنوز سفر نرسیده
            if not (trip_date - timedelta(days=4) <= now < trip_date):
                continue

            # یافتن مسافران واجدشرایط این تور
            participants = session.exec(
                select(Participant).where(
                    Participant.trip_id == trip.id,
                    Participant.telegram_user_id.isnot(None),
                )
            ).all()

            for participant in participants:
                # محاسبه قیمت efektive بر اساس نوع وسایل نقلیه و انتخاب کاربر
                effective_price = trip.price
                if (
                    trip.transportation_type == "personal_vehicle"
                    and participant.vehicle_choice == "other"
                ):
                    effective_price = trip.price + trip.vehicle_fare
                
                # فقط مسافرانی که پرداخت کامل تأییدشده دارند
                if not is_fully_paid(
                    participant.id,
                    trip.id,
                    effective_price,
                    session,
                ):
                    continue

                # بررسی ارسال تکراری
                existing = session.exec(
                    select(ReminderLog).where(
                        ReminderLog.participant_id == participant.id,
                        ReminderLog.trip_id == trip.id,
                        ReminderLog.reminder_type == "group_link_4_days",
                    )
                ).first()
                if existing:
                    continue

                # ساخت پیام
                message = (
                    f"سلام {participant.full_name}\n\n"
                    f"🏕 سفر {trip.title}\n\n"
                    f"لینک گروه هماهنگی سفر:\n"
                    f"{trip.telegram_group_link}\n\n"
                    "لطفاً برای هماهنگی بیشتر به گروه بپیوندید."
                )

                # ارسال پیام تلگرام
                try:
                    await bot.send_message(
                        chat_id=participant.telegram_user_id,
                        text=message,
                    )
                except Exception as e:
                    logger.error(
                        f"⚠️ خطا در ارسال لینک گروه به کاربر "
                        f"{participant.telegram_user_id} (تور {trip.id}): {e}"
                    )
                    # ادامه می‌دهیم — رکورد ثبت نمی‌شود تا در دوره بعد دوباره تلاش شود
                    continue

                # فقط بعد از ارسال موفق، رکورد را ثبت کن
                log_entry = ReminderLog(
                    participant_id=participant.id,
                    trip_id=trip.id,
                    reminder_type="group_link_4_days",
                    sent_at=datetime.now().isoformat(),
                )
                session.add(log_entry)

                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    logger.warning(
                        f"⚠️ رکورد تکراری برای {participant.id} / "
                        f"تور {trip.id} — رد شد."
                    )
                else:
                    logger.info(
                        f"✅ لینک گروه برای {participant.full_name} "
                        f"(تور {trip.id}) ارسال و ثبت شد."
                    )


def mark_completed_trips() -> None:
    """سفرهای فعالی که تاریخ برگزاری‌شان گذشته را completed می‌کند."""
    now = datetime.now()

    with Session(engine) as session:
        trips = session.exec(
            select(Trip).where(Trip.status == "active")
        ).all()

        changed = 0
        for trip in trips:
            if not trip.date:
                continue
            try:
                trip_date = parse_jalali(trip.date)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"⚠️ تاریخ نامعتبر تور {trip.id}: {trip.date} — {e}"
                )
                continue

            # اگر تاریخ سفر قبل از امروز باشد → completed
            if trip_date < now:
                trip.status = "completed"
                changed += 1

        if changed:
            session.commit()
            logger.info(f"✅ {changed} سفر به‌عنوان برگزارشده علامت‌گذاری شد.")


async def run_reminder_loop(bot):
    """لوپ اصلی Scheduler: بررسی فوری هنگام startup + تکرار هر ساعت."""
    logger.info("🔄 Scheduler: شروع بررسی فوری (catch-up)...")
    try:
        mark_completed_trips()
        await send_group_link_reminders(bot)
    except Exception as e:
        logger.error(f"⚠️ خطا در بررسی اولیه: {e}", exc_info=True)

    while True:
        await asyncio.sleep(3600)
        logger.info("🔄 Scheduler: بررسی دورهای...")
        try:
            mark_completed_trips()
            await send_group_link_reminders(bot)
        except Exception as e:
            logger.error(f"⚠️ خطا در بررسی دورهای: {e}", exc_info=True)
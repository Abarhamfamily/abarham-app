import os
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from migration import run_migrations
from fastapi.responses import HTMLResponse, FileResponse, Response
from sqlmodel import Session, select

from models import engine, create_db_and_tables, Trip, Participant, Payment
from payment import transition_status, get_receipt_path
from bot import start_bot
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("abarham")

# نگه‌داری رفرنس به اپ تلگرام برای shutdown تمیز
telegram_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # اجرای migrationهای دیتابیس
    run_migrations()

    # ساخت جدول‌های جدید در صورت نیاز
    create_db_and_tables()

    # اجرای ربات تلگرام در پس‌زمینه
    global telegram_app

    try:
        telegram_app = await start_bot()
        logger.info("🤖 وب‌سرور و ربات تلگرام فعال شدند.")
    except Exception as e:
        telegram_app = None
        logger.error(f"⚠️ اجرای ربات تلگرام با خطا مواجه شد: {e}")

    yield

    # خاموش کردن تمیز ربات
    if telegram_app is not None:
        try:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()
        except Exception as e:
            logger.error(f"⚠️ خطا هنگام خاموش کردن ربات: {e}")


app = FastAPI(lifespan=lifespan)

# ---------------------------------------------------------------------------
# فایل‌های استاتیک / PWA
# ---------------------------------------------------------------------------
@app.get("/sw.js")
def get_sw():
    if os.path.exists("sw.js"):
        return FileResponse(
            "sw.js",
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache"},
        )
    return Response(content="self.registration.unregister();", media_type="application/javascript")


@app.get("/manifest.json")
def get_manifest():
    if os.path.exists("manifest.json"):
        return FileResponse("manifest.json", media_type="application/json")
    return {}


@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png", media_type="image/png")
    raise HTTPException(404, "لوگو یافت نشد")


@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return "<h1>فایل index.html یافت نشد!</h1>"


# ---------------------------------------------------------------------------
# CRUD تورها
# ---------------------------------------------------------------------------
@app.get("/trips", response_model=List[Trip])
@app.get("/trips/", response_model=List[Trip])
def get_trips():
    with Session(engine) as session:
        return session.exec(select(Trip)).all()


@app.post("/trips", response_model=Trip)
@app.post("/trips/", response_model=Trip)
def create_trip(trip: Trip):
    trip.id = None  # جلوگیری از تزریق id توسط کلاینت
    with Session(engine) as session:
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return trip


@app.put("/trips/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, trip: Trip):
    with Session(engine) as session:
        db_trip = session.get(Trip, trip_id)
        if not db_trip:
            raise HTTPException(404, "تور یافت نشد")
        data = trip.dict(exclude_unset=True, exclude={"id"})
        for key, value in data.items():
            setattr(db_trip, key, value)
        session.add(db_trip)
        session.commit()
        session.refresh(db_trip)
        return db_trip


@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int):
    with Session(engine) as session:
        db_trip = session.get(Trip, trip_id)
        if not db_trip:
            raise HTTPException(404, "تور یافت نشد")

        # حذف آبشاری مسافران مرتبط با این تور
        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()
        for p in participants:
            session.delete(p)

        session.delete(db_trip)
        session.commit()
        return {"ok": True}


# ---------------------------------------------------------------------------
# CRUD مسافران
# ---------------------------------------------------------------------------
@app.get("/participants", response_model=List[Participant])
@app.get("/participants/", response_model=List[Participant])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()


@app.get("/trips/{trip_id}/participants", response_model=List[Participant])
def get_trip_participants(trip_id: int):
    """دریافت لیست شرکت‌کنندگان یک تور خاص"""
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            raise HTTPException(404, "تور یافت نشد")
        return session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()


@app.post("/participants", response_model=Participant)
@app.post("/participants/", response_model=Participant)
def create_participant(participant: Participant):
    participant.id = None
    with Session(engine) as session:
        trip = session.get(Trip, participant.trip_id)
        if not trip:
            raise HTTPException(400, "توری با این شناسه یافت نشد")

        if trip.capacity:
            existing_count = len(
                session.exec(
                    select(Participant).where(Participant.trip_id == participant.trip_id)
                ).all()
            )
            if existing_count >= trip.capacity:
                raise HTTPException(400, "ظرفیت این تور تکمیل شده است")

        session.add(participant)
        session.commit()
        session.refresh(participant)
        return participant


@app.put("/participants/{participant_id}", response_model=Participant)
def update_participant(participant_id: int, participant: Participant):
    with Session(engine) as session:
        db_participant = session.get(Participant, participant_id)
        if not db_participant:
            raise HTTPException(404, "مسافر یافت نشد")
        data = participant.dict(exclude_unset=True, exclude={"id"})
        for key, value in data.items():
            setattr(db_participant, key, value)
        session.add(db_participant)
        session.commit()
        session.refresh(db_participant)
        return db_participant


@app.delete("/participants/{participant_id}")
def delete_participant(participant_id: int):
    with Session(engine) as session:
        db_participant = session.get(Participant, participant_id)
        if not db_participant:
            raise HTTPException(404, "مسافر یافت نشد")
        session.delete(db_participant)
        session.commit()
        return {"ok": True}


# ---------------------------------------------------------------------------
# مدیریت پرداخت‌ها (ادمین)
# ---------------------------------------------------------------------------
VALID_PAYMENT_STATUSES = {"pending_review", "confirmed", "rejected"}


@app.get("/payments")
def get_payments(status: Optional[str] = None):
    if status is not None and status not in VALID_PAYMENT_STATUSES:
        raise HTTPException(400, "وضعیت نامعتبر. مقادیر مجاز: pending_review, confirmed, rejected")

    with Session(engine) as session:
        query = select(Payment)
        if status:
            query = query.where(Payment.status == status)

        payments = session.exec(query).all()

        # افزودن اطلاعات مرتبط Trip و Participant برای نمایش بهتر (بدون تغییر مدل‌ها)
        result = []
        for p in payments:
            trip = session.get(Trip, p.trip_id)
            participant = session.get(Participant, p.participant_id)
            result.append({
                "id": p.id,
                "participant_id": p.participant_id,
                "trip_id": p.trip_id,
                "telegram_user_id": p.telegram_user_id,
                "payment_type": p.payment_type,
                "expected_amount": p.expected_amount,
                "receipt_file_id": p.receipt_file_id,
                "receipt_file_unique_id": p.receipt_file_unique_id,
                "receipt_local_path": p.receipt_local_path,
                "status": p.status,
                "created_at": p.created_at,
                "reviewed_at": p.reviewed_at,
                "review_note": p.review_note,
                "trip": {
                    "id": trip.id if trip else None,
                    "title": trip.title if trip else None,
                    "price": trip.price if trip else None,
                } if trip else None,
                "participant": {
                    "id": participant.id if participant else None,
                    "full_name": participant.full_name if participant else None,
                    "national_id": participant.national_id if participant else None,
                    "phone_number": participant.phone_number if participant else None,
                } if participant else None,
            })
        return result


@app.post("/payments/{payment_id}/confirm")
async def confirm_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(404, "پرداخت یافت نشد")

        if payment.status != "pending_review":
            raise HTTPException(400, "فقط پرداخت‌های در انتظار بررسی قابل تأیید هستند")

        try:
            transition_status(payment, "confirmed")
        except ValueError as e:
            raise HTTPException(400, str(e))

        payment.reviewed_at = datetime.now().isoformat()
        session.add(payment)
        session.commit()
        session.refresh(payment)
            # ارسال پیام تأیید فیش به کاربر تلگرام
    if telegram_app is not None and payment.telegram_user_id:
        try:
            if payment.payment_type == "deposit":
                message_text = (
                    "✅ بیعانه شما با موفقیت تأیید شد.\n\n"
                    "💰 مبلغ بیعانه دریافت و ثبت شد.\n\n"
                    "برای نهایی شدن ثبت‌نام، شما تا یک هفته قبل از سفر "
                    "فرصت دارید مبلغ باقی‌مانده را تکمیل کنید."
                )
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "💵 پرداخت مابقی هزینه",
                                callback_data=f"complete_payment:{payment.participant_id}",
                            ),
                        ],
                    ]
                )
            else:
                message_text = (
                    "✅ پرداخت شما با موفقیت تأیید شد.\n\n"
                    "ثبت‌نام شما در سیستم ابرهام نهایی شد."
                )
                reply_markup = None

            await telegram_app.bot.send_message(
                chat_id=payment.telegram_user_id,
                text=message_text,
                reply_markup=reply_markup,
            )
        except Exception as e:
            logger.error(f"⚠️ خطا در ارسال پیام تأیید پرداخت: {e}")
        return payment


@app.post("/payments/{payment_id}/reject")
def reject_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(404, "پرداخت یافت نشد")

        if payment.status != "pending_review":
            raise HTTPException(400, "فقط پرداخت‌های در انتظار بررسی قابل رد شدن هستند")

        try:
            transition_status(payment, "rejected")
        except ValueError as e:
            raise HTTPException(400, str(e))

        payment.reviewed_at = datetime.now().isoformat()
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment


@app.get("/receipts/{filename}")
def get_receipt(filename: str):
    # جلوگیری از Path Traversal — فقط فایل‌های داخل پوشه receipts/ سرو می‌شوند
    receipts_dir = os.path.abspath("receipts")
    # ساخت مسیر کامل داخل receipts و resolve امن
    full_path = os.path.join("receipts", filename)
    safe_path = os.path.abspath(get_receipt_path(full_path))

    # بررسی اینکه مسیر resolve شده داخل receipts_dir باشد
    if not safe_path.startswith(receipts_dir + os.sep):
        raise HTTPException(400, "نام فایل نامعتبر است")

    if not os.path.exists(safe_path):
        raise HTTPException(404, "فیش یافت نشد")

    return FileResponse(safe_path)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

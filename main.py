import os
import logging
import traceback
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

import bcrypt
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import Session, select, delete
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# Import local models, helpers, and migration script
from models import Trip, Participant, Payment, engine
from migration import run_migrations
from bot import start_bot

# تنظیمات لاگر
logger = logging.getLogger(__name__)

# متغیر سراسری ربات تلگرام (اگر در جای دیگر مقداردهی می‌شود)
telegram_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    try:
        run_migrations()
        print("[MIGRATION SUCCESS] مایگریشن‌ها با موفقیت اجرا شدند.")
    except Exception as e:
        print(f"[MIGRATION ERROR] خطا در اجرای مایگریشن استارت‌آپ: {e}")
        traceback.print_exc()
    # Start Telegram bot after migrations (whether success or failure)
    telegram_app = await start_bot()
    yield
    # Shutdown Telegram bot
    if telegram_app is not None:
        try:
            await telegram_app.updater.stop()
        except Exception:
            pass
        try:
            await telegram_app.shutdown()
        except Exception:
            pass


app = FastAPI(lifespan=lifespan)

SESSION_SECRET = os.getenv("SESSION_SECRET", "super-secret-key-change-in-prod")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=True,
    same_site="lax",
    max_age=86400
)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required but not set")


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.strip().encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def verify_admin_session(request: Request):
    if not request.session.get("admin_authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required"
        )
    return True


def mark_completed_trips():
    pass

def get_confirmed_total(participant_id: int, trip_id: int, session: Session) -> float:
    payments = session.exec(
        select(Payment).where(
            Payment.participant_id == participant_id,
            Payment.trip_id == trip_id,
            Payment.status == "confirmed"
        )
    ).all()
    return sum(p.expected_amount for p in payments if p.expected_amount)

def has_pending(participant_id: int, trip_id: int, session: Session) -> bool:
    payment = session.exec(
        select(Payment).where(
            Payment.participant_id == participant_id,
            Payment.trip_id == trip_id,
            Payment.status == "pending_review"
        )
    ).first()
    return payment is not None

def is_fully_paid(participant_id: int, trip_id: int, trip_price: float, session: Session) -> bool:
    return get_confirmed_total(participant_id, trip_id, session) >= trip_price

def transition_status(payment: Payment, new_status: str):
    payment.status = new_status

def get_receipt_path(path: str) -> str:
    return path


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username != ADMIN_USERNAME or not verify_password(password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    request.session["admin_authenticated"] = True
    return JSONResponse({"success": True})


@app.post("/logout")
async def logout(request: Request):
    request.session.pop("admin_authenticated", None)
    return JSONResponse({"success": True})


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
    return HTMLResponse("<h1>فایل index.html یافت نشد!</h1>")


@app.get("/trips", response_model=List[Trip], dependencies=[Depends(verify_admin_session)])
@app.get("/trips/", response_model=List[Trip], dependencies=[Depends(verify_admin_session)])
def get_trips():
    mark_completed_trips()
    with Session(engine) as session:
        return session.exec(select(Trip)).all()


@app.post("/trips", response_model=Trip, dependencies=[Depends(verify_admin_session)])
@app.post("/trips/", response_model=Trip, dependencies=[Depends(verify_admin_session)])
def create_trip(trip: Trip):
    trip.id = None
    with Session(engine) as session:
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return trip


@app.put("/trips/{trip_id}", response_model=Trip, dependencies=[Depends(verify_admin_session)])
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


@app.delete("/trips/{trip_id}", dependencies=[Depends(verify_admin_session)])
def delete_trip(trip_id: int):
    with Session(engine) as session:
        db_trip = session.get(Trip, trip_id)
        if not db_trip:
            raise HTTPException(404, "تور یافت نشد")

        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()
        for p in participants:
            session.delete(p)

        session.delete(db_trip)
        session.commit()
        return {"ok": True}


@app.get("/participants", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
@app.get("/participants/", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()


# ✅ تغییر ۳: بهره‌گیری مستقیم از مقدار ذخیره‌شده paid_amount
@app.get("/trips/{trip_id}/participants", dependencies=[Depends(verify_admin_session)])
def get_trip_participants(trip_id: int):
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            raise HTTPException(404, "تور یافت نشد")

        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()

        result = []
        for participant in participants:
            confirmed_total = participant.paid_amount or 0.0
            remaining_amount = max(
                round(trip.price - confirmed_total, 2),
                0.0,
            )
            has_pending_flag = has_pending(
                participant.id,
                trip_id,
                session,
            )
            fully_paid = confirmed_total >= trip.price

            if has_pending_flag:
                status_text = "فیش در انتظار بررسی"
            elif fully_paid:
                status_text = "پرداخت کامل تایید شده"
            elif confirmed_total > 0:
                status_text = "بیعانه تایید شده"
            else:
                status_text = "پرداخت نشده"

            result.append({
                "id": participant.id,
                "full_name": participant.full_name,
                "national_id": participant.national_id,
                "phone_number": participant.phone_number,
                "confirmed_amount": confirmed_total,
                "remaining_amount": remaining_amount,
                "has_pending": has_pending_flag,
                "is_fully_paid": fully_paid,
                "payment_status": status_text,
            })

        return result


# ✅ تغییر ۴: محاسبه مجموع دریافتی‌ها بر اساس paid_amount
@app.get("/trips/{trip_id}/total_received", dependencies=[Depends(verify_admin_session)])
def get_trip_total_received(trip_id: int):
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            raise HTTPException(404, "تور یافت نشد")

        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()

        total_received = sum(participant.paid_amount or 0.0 for participant in participants)

        return {
            "trip_id": trip_id,
            "total_received": round(total_received, 2),
            "currency": "تومان"
        }


@app.post("/participants", response_model=Participant, dependencies=[Depends(verify_admin_session)])
@app.post("/participants/", response_model=Participant, dependencies=[Depends(verify_admin_session)])
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


@app.put("/participants/{participant_id}", response_model=Participant, dependencies=[Depends(verify_admin_session)])
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


@app.delete("/participants/{participant_id}", dependencies=[Depends(verify_admin_session)])
def delete_participant(participant_id: int):
    with Session(engine) as session:
        db_participant = session.get(Participant, participant_id)
        if not db_participant:
            raise HTTPException(404, "مسافر یافت نشد")

        session.exec(
            delete(Payment).where(Payment.participant_id == participant_id)
        )

        session.delete(db_participant)
        session.commit()

        return {"ok": True}


VALID_PAYMENT_STATUSES = {"pending_review", "confirmed", "rejected"}


@app.get("/payments", dependencies=[Depends(verify_admin_session)])
def get_payments(status: Optional[str] = None):
    if status is not None and status not in VALID_PAYMENT_STATUSES:
        raise HTTPException(400, "وضعیت نامعتبر. مقادیر مجاز: pending_review, confirmed, rejected")

    with Session(engine) as session:
        query = select(Payment)
        if status:
            query = query.where(Payment.status == status)

        payments = session.exec(query).all()

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


# ✅ تغییر ۱: به‌روزرسانی participant.paid_amount و status هنگام تأیید پرداخت + ارسال پیام تلگرام
@app.post("/payments/{payment_id}/confirm", dependencies=[Depends(verify_admin_session)])
async def confirm_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(404, "پرداخت یافت نشد")

        if payment.status != "pending_review":
            raise HTTPException(400, "فقط پرداخت‌های در انتظار بررسی قابل تأیید هستند")

        participant = session.get(Participant, payment.participant_id)
        if not participant:
            raise HTTPException(404, "شرکت‌کننده یافت نشد")

        old_amount = participant.paid_amount or 0.0
        pay_amount = payment.expected_amount or 0.0

        if payment.payment_type == "full":
            participant.paid_amount = pay_amount
            participant.payment_status = "پرداخت کامل"
        elif payment.payment_type == "deposit":
            participant.paid_amount = old_amount + pay_amount
            participant.payment_status = "پرداخت بیعانه"

        try:
            transition_status(payment, "confirmed")
        except ValueError as e:
            raise HTTPException(400, str(e))

        payment.reviewed_at = datetime.now().isoformat()
        session.add(payment)
        session.add(participant)
        session.commit()
        session.refresh(payment)

        logger.info(f"💰 Payment {payment_id} confirmed. Participant paid_amount: {participant.paid_amount}")

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


# ✅ تغییر ۲: بازگردانی مبلغ participant.paid_amount و بروزرسانی وضعیت هنگام رد پرداخت
@app.post("/payments/{payment_id}/reject", dependencies=[Depends(verify_admin_session)])
def reject_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(404, "پرداخت یافت نشد")

        if payment.status != "pending_review":
            raise HTTPException(400, "فقط پرداخت‌های در انتظار بررسی قابل رد شدن هستند")

        participant = session.get(Participant, payment.participant_id)
        if participant:
            pay_amount = payment.expected_amount or 0.0
            if payment.payment_type == "full":
                participant.paid_amount = 0.0
                participant.payment_status = "پرداخت نشده"
            elif payment.payment_type == "deposit":
                participant.paid_amount = max(0.0, (participant.paid_amount or 0.0) - pay_amount)
                if participant.paid_amount == 0.0:
                    participant.payment_status = "پرداخت نشده"
            session.add(participant)

        try:
            transition_status(payment, "rejected")
        except ValueError as e:
            raise HTTPException(400, str(e))

        payment.reviewed_at = datetime.now().isoformat()
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment


@app.get("/receipts/{filename}", dependencies=[Depends(verify_admin_session)])
def get_receipt(filename: str):
    receipts_dir = os.path.abspath("receipts")
    full_path = os.path.join("receipts", filename)
    safe_path = os.path.abspath(get_receipt_path(full_path))

    if not safe_path.startswith(receipts_dir + os.sep):
        raise HTTPException(400, "نام فایل نامعتبر است")

    if not os.path.exists(safe_path):
        raise HTTPException(404, "فیش یافت نشد")

    return FileResponse(safe_path)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
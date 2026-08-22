import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

import bcrypt
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import Session, select, delete

# Import local models, helpers, and migration script
from models import Trip, Participant, Payment, engine
from migration import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # اجرای مایگریشن‌های دیتابیس در زمان استارت‌آپ سرور
    try:
        run_migrations()
    except Exception as e:
        print(f"Migration error on startup: {e}")
    yield


app = FastAPI(lifespan=lifespan)

SESSION_SECRET = os.getenv("SESSION_SECRET", "super-secret-key-change-in-prod")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=True,
    same_site="lax",
    max_age=86400
)

# Admin Authentication Configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required but not set")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against the hashed version."""
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.strip().encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def verify_admin_session(request: Request):
    """Verify admin session authentication."""
    if not request.session.get("admin_authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required"
        )
    return True


# ---------------------------------------------------------------------------
# احراز هویت (Login / Logout)
# ---------------------------------------------------------------------------
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Admin login endpoint."""
    if username != ADMIN_USERNAME or not verify_password(password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    request.session["admin_authenticated"] = True
    return JSONResponse({"success": True})


@app.post("/logout")
async def logout(request: Request):
    """Admin logout endpoint."""
    request.session.pop("admin_authenticated", None)
    return JSONResponse({"success": True})

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
    return HTMLResponse("<h1>فایل index.html یافت نشد!</h1>")


# ---------------------------------------------------------------------------
# CRUD تورها
# ---------------------------------------------------------------------------
@app.get("/trips", response_model=List[Trip], dependencies=[Depends(verify_admin_session)])
@app.get("/trips/", response_model=List[Trip], dependencies=[Depends(verify_admin_session)])
def get_trips():
    mark_completed_trips()
    with Session(engine) as session:
        return session.exec(select(Trip)).all()


@app.post("/trips", response_model=Trip, dependencies=[Depends(verify_admin_session)])
@app.post("/trips/", response_model=Trip, dependencies=[Depends(verify_admin_session)])
def create_trip(trip: Trip, _: bool = Depends(verify_admin_api_key)):
    trip.id = None
    with Session(engine) as session:
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return trip


@app.put("/trips/{trip_id}", response_model=Trip, dependencies=[Depends(verify_admin_session)])
def update_trip(trip_id: int, trip: Trip, _: bool = Depends(verify_admin_api_key)):
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
def delete_trip(trip_id: int, _: bool = Depends(verify_admin_api_key)):
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


# ---------------------------------------------------------------------------
# CRUD مسافران
# ---------------------------------------------------------------------------
@app.get("/participants", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
@app.get("/participants/", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()


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
            confirmed_total = get_confirmed_total(
                participant.id,
                trip_id,
                session,
            )
            remaining_amount = max(
                round(trip.price - confirmed_total, 2),
                0.0,
            )
            has_pending_flag = has_pending(
                participant.id,
                trip_id,
                session,
            )
            fully_paid = is_fully_paid(
                participant.id,
                trip_id,
                trip.price,
                session,
            )

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


@app.get("/trips/{trip_id}/total_received", dependencies=[Depends(verify_admin_session)])
def get_trip_total_received(trip_id: int):
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            raise HTTPException(404, "تور یافت نشد")

        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()

        total_received = 0.0
        for participant in participants:
            confirmed_total = get_confirmed_total(
                participant.id,
                trip_id,
                session,
            )
            total_received += confirmed_total

        return {
            "trip_id": trip_id,
            "total_received": round(total_received, 2),
            "currency": "تومان"
        }


@app.post("/participants", response_model=Participant, dependencies=[Depends(verify_admin_session)])
@app.post("/participants/", response_model=Participant, dependencies=[Depends(verify_admin_session)])
def create_participant(participant: Participant, _: bool = Depends(verify_admin_api_key)):
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
def update_participant(participant_id: int, participant: Participant, _: bool = Depends(verify_admin_api_key)):
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
def delete_participant(participant_id: int, _: bool = Depends(verify_admin_api_key)):
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


# ---------------------------------------------------------------------------
# مدیریت پرداخت‌ها (ادمین)
# ---------------------------------------------------------------------------
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


@app.post("/payments/{payment_id}/confirm", dependencies=[Depends(verify_admin_session)])
async def confirm_payment(payment_id: int, _: bool = Depends(verify_admin_api_key)):
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


@app.post("/payments/{payment_id}/reject", dependencies=[Depends(verify_admin_session)])
def reject_payment(payment_id: int, _: bool = Depends(verify_admin_api_key)):
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
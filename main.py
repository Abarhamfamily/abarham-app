import os
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Header, Depends, Request, Form
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from migration import run_migrations
from fastapi.responses import HTMLResponse, FileResponse, Response, JSONResponse
from sqlmodel import Session, select, delete
import bcrypt

from models import engine, create_db_and_tables, Trip, Participant, Payment
from payment import (
    transition_status,
    get_receipt_path,
    get_confirmed_total,
    is_fully_paid,
    has_pending,
)
from bot import start_bot
from reminders import run_reminder_loop, mark_completed_trips
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("abarham")

# Admin API Authentication
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
if ADMIN_API_KEY is None:
    raise RuntimeError("ADMIN_API_KEY environment variable is required but not set")

def verify_admin_api_key(x_admin_api_key: str = Header(None)):
    """
    Minimal admin authentication dependency.
    Protects admin-sensitive endpoints only.
    """
    if not x_admin_api_key or x_admin_api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required"
        )
    return True

# نگه‌داری رفرنس به اپ تلگرام و تسک یادآوری برای shutdown تمیز
telegram_app = None
reminder_task = None



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
        # شروع Scheduler یادآوری
        global reminder_task
        reminder_task = asyncio.create_task(
            run_reminder_loop(telegram_app.bot)
        )
        logger.info("🔄 Scheduler یادآوری فعال شد.")
    except Exception as e:
        telegram_app = None
        logger.error(f"⚠️ اجرای ربات تلگرام با خطا مواجه شد: {e}")

    yield

    # خاموش کردن Scheduler یادآوری
    if reminder_task is not None:
        reminder_task.cancel()
        logger.info("🔄 Scheduler یادآوری متوقف شد.")

    # خاموش کردن تمیز ربات
    if telegram_app is not None:
        try:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()
        except Exception as e:
            logger.error(f"⚠️ خطا هنگام خاموش کردن ربات: {e}")


app = FastAPI(lifespan=lifespan)

# Session Middleware Configuration
SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET environment variable is required but not set")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=True,
    same_site="lax",
    max_age=86400
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin Authentication Configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required but not set")

# Password hashing configuration
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes and generate salt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against the hashed version."""
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.strip().encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)



def verify_admin_session(request: Request):
    """
    Verify admin session authentication.
    """
    if not request.session.get("admin_authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required"
        )
    return True


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Admin login endpoint.
    """
    print(f"[DEBUG LOGIN] Input Username: '{username}'")
    print(f"[DEBUG LOGIN] Expected Username: '{ADMIN_USERNAME}'")
    print(f"[DEBUG LOGIN] Received Password Length: {len(password)}")
    print(f"[DEBUG LOGIN] Hashed Password in Env exists: {bool(ADMIN_PASSWORD_HASH)}")
    print(f"[DEBUG BCRYPT] Hash in env starts with: '{ADMIN_PASSWORD_HASH[:10] if ADMIN_PASSWORD_HASH else 'NONE'}'")
    print(f"[DEBUG BCRYPT] Hash total length: {len(ADMIN_PASSWORD_HASH) if ADMIN_PASSWORD_HASH else 0}")
    
    if username != ADMIN_USERNAME or not verify_password(password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    request.session["admin_authenticated"] = True
    
    # Set secure session cookie
    response = JSONResponse({"success": True})
    response.set_cookie(
        key="admin_authenticated",
        value="true",
        httponly=True,
        samesite="none" if request.url.scheme == "https" else "lax",
        secure=True if request.url.scheme == "https" else False,
        max_age=86400
    )
@app.get("/generate-hash")
async def generate_hash():
    """
    Temporary endpoint to generate bcrypt hash for 'Geo5588Cli'.
    Use this to set the ADMIN_PASSWORD environment variable.
    """
    password = "Geo5588Cli"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return {"hash": hashed.decode('utf-8')}
    return response

@app.post("/logout")
async def logout(request: Request):
    """
    Admin logout endpoint.
    """
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
    # علامت‌گذاری خودکار سفرهای تاریخ‌گذشته (مقاوم در برابر عدم اجرای Scheduler)
    mark_completed_trips()
    with Session(engine) as session:
        return session.exec(select(Trip)).all()


@app.post("/trips", response_model=Trip, dependencies=[Depends(verify_admin_session)])
@app.post("/trips/", response_model=Trip, dependencies=[Depends(verify_admin_session)])
def create_trip(trip: Trip, _: bool = Depends(verify_admin_api_key)):
    trip.id = None  # جلوگیری از تزریق id توسط کلاینت
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
@app.get("/participants", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
@app.get("/participants/", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()


@app.get("/trips/{trip_id}/participants", dependencies=[Depends(verify_admin_session)])
def get_trip_participants(trip_id: int):
    """دریافت شرکت‌کنندگان یک تور + اطلاعات واقعی پرداخت از جدول Payment."""
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            raise HTTPException(404, "تور یافت نشد")

        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()

        result = []
        for participant in participants:
            # مبلغ واقعی تأییدشده از جدول Payment
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

            # وضعیت واقعی پرداخت
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
    """محاسبه جمع دریافتی کل یک تور (مجموع مبالغ تأییدشده همه شرکت‌کنندگان)."""
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
            raise HTTPException(404, "????? ???? ???")

        # حذف تمام فیش‌های پرداخت این مسافر.
        # از حذف انبوه (bulk delete) استفاده می‌کنیم تا دستور SQL بلافاصله اجرا شود
        # و ردیف‌های Payment پیش از حذف خود Participant حذف شوند.
        # (در PostgreSQL ترتیب session.delete مشخص نیست؛ بدون این کار
        #  حذف Parent پیش از Child رخ می‌دهد و با خطای FOREIGN KEY متوقف می‌شود.)
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

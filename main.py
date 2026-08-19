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

from pydantic import BaseModel, Field as PydanticField

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

# Admin session authentication
def verify_admin_session(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="Admin not authenticated")
    return True

def get_session():
    with Session(engine) as session:
        yield session
# Keep reference to telegram app and reminder task for clean shutdown
telegram_app = None
reminder_task = None
logger = logging.getLogger("abarham")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute database migrations
    run_migrations()

    # Create database tables if needed
    create_db_and_tables()

    # Start Telegram bot in background
    global telegram_app
    try:
        telegram_app = await start_bot()
        logger.info("🤖 Bot and web server started.")
        # Start reminder scheduler
        global reminder_task
        reminder_task = asyncio.create_task(
            run_reminder_loop(telegram_app.bot)
        )
        logger.info("🔄 Reminder scheduler started.")
    except Exception as e:
        telegram_app = None
        logger.error(f"⚠️ Telegram bot startup failed: {e}")

    yield

    # Stop reminder scheduler
    if reminder_task is not None:
        reminder_task.cancel()
        logger.info("🔄 Reminder scheduler stopped.")

    # Clean shutdown of Telegram bot
    if telegram_app is not None:
        try:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()
        except Exception as e:
            logger.error(f"⚠️ Error shutting down Telegram bot: {e}")
app = FastAPI(lifespan=lifespan)
# Session Middleware Configuration
SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET environment variable is required but not set")

https_only = os.getenv("IS_PROD", "false").lower() == "true"

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=https_only,
    same_site="lax",
    max_age=86400
)
# CORS Middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Pydantic models for validation
class TripBase(BaseModel):
    title: str
    destination: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    price: float = 0.0
    capacity: int = 0
    telegram_group_link: Optional[str] = None
    status: str = "active"

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    price: Optional[float] = None
    capacity: Optional[int] = None
    telegram_group_link: Optional[str] = None
    status: Optional[str] = None

class ParticipantBase(BaseModel):
    full_name: str
    national_id: str
    phone_number: str
    trip_id: int
    telegram_user_id: Optional[int] = None
    payment_status: str = "پرداخت بیعانه"
    paid_amount: float = 0.0

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantUpdate(BaseModel):
    full_name: Optional[str] = None
    national_id: Optional[str] = None
    phone_number: Optional[str] = None
    trip_id: Optional[int] = None
    telegram_user_id: Optional[int] = None
    payment_status: Optional[str] = None
    paid_amount: Optional[float] = None
# Login/logout endpoints
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    expected_username = os.getenv("ADMIN_USERNAME", "admin")
    expected_password = os.getenv("ADMIN_PASSWORD", "admin")
    if username == expected_username and password == expected_password:
        request.session.clear()
        request.session["admin"] = True
        return JSONResponse({"success": True})
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse({"success": True})
# ---------------------------------------------------------------------------
# ÙØ§ÛŒÙ„â€ŒÙ‡Ø§ÛŒ Ø§Ø³ØªØ§ØªÛŒÚ© / PWA
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
    # Fallback manifest content
    manifest_content = {
        "name": "سامانه مدیریت تور ابرهم",
        "short_name": "ابرهم",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#00a693",
        "icons": [
            {
                "src": "logo.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "logo.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JSONResponse(content=manifest_content)


@app.get("/health")
def health_check():
    return {"status": "ok"}
@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png", media_type="image/png")
    raise HTTPException(404, "Ù„ÙˆÚ¯Ùˆ ÛŒØ§ÙØª Ù†Ø´Ø¯")


@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>ÙØ§ÛŒÙ„ index.html ÛŒØ§ÙØª Ù†Ø´Ø¯!</h1>")
# ---------------------------------------------------------------------------
# CRUD ØªÙˆØ±Ù‡Ø§
# ---------------------------------------------------------------------------
@app.get("/trips", response_model=List[Trip], dependencies=[Depends(verify_admin_session)])
@app.get("/trips/", response_model=List[Trip], dependencies=[Depends(verify_admin_session)])
def get_trips():
    # Mark completed trips via scheduler
    mark_completed_trips()
    with Session(engine) as session:
        return session.exec(select(Trip)).all()

@app.get("/trips/{trip_id}/total_received")
def get_trip_total_received(trip_id: int, session: Session = Depends(get_session)):
    # محاسبه مجموع paid_amount مسافران تأییدشده این تور
    payments = session.exec(select(Payment).where(Payment.trip_id == trip_id, Payment.status == "confirmed")).all()
    total = sum(p.expected_amount for p in payments)
    return {"total_received": total}
@app.post("/trips", response_model=Trip, dependencies=[Depends(verify_admin_session)])

def create_trip(trip: TripCreate):
    db_trip = Trip.from_orm(trip)
    db_trip.id = None  # Ensure ID is None for new record
    with Session(engine) as session:
        session.add(db_trip)
        session.commit()
        session.refresh(db_trip)
        return db_trip

@app.put("/trips/{trip_id}", response_model=Trip, dependencies=[Depends(verify_admin_session)])
def update_trip(trip_id: int, trip: TripUpdate):
    with Session(engine) as session:
        db_trip = session.get(Trip, trip_id)
        if not db_trip:
            raise HTTPException(404, "ØªÙˆØ± ÛŒØ§ÙØª Ù†Ø´Ø¯")
        trip_data = trip.dict(exclude_unset=True, exclude={"id"})
        for key, value in trip_data.items():
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
            raise HTTPException(404, "ØªÙˆØ± ÛŒØ§ÙØª Ù†Ø´Ø¯")
        # Delete related participants
        participants = session.exec(
            select(Participant).where(Participant.trip_id == trip_id)
        ).all()
        for p in participants:
            session.delete(p)
        session.delete(db_trip)
        session.commit()
        return {"ok": True}
# ---------------------------------------------------------------------------
# CRUD Ù…Ø³Ø§ÙØ±Ø§Ù†
# ---------------------------------------------------------------------------
@app.get("/participants", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
@app.get("/participants/", response_model=List[Participant], dependencies=[Depends(verify_admin_session)])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()

@app.post("/participants", response_model=Participant, dependencies=[Depends(verify_admin_session)])

def create_participant(participant: ParticipantCreate):
    db_participant = Participant.from_orm(participant)
    db_participant.id = None
    with Session(engine) as session:
        session.add(db_participant)
        session.commit()
        session.refresh(db_participant)
        return db_participant

@app.put("/participants/{participant_id}", response_model=Participant, dependencies=[Depends(verify_admin_session)])
def update_participant(participant_id: int, participant: ParticipantUpdate):
    with Session(engine) as session:
        db_participant = session.get(Participant, participant_id)
        if not db_participant:
            raise HTTPException(404, "Ù…Ø³Ø§ÙØ± ÛŒØ§ÙØª Ù†Ø´Ø¯")
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
            raise HTTPException(404, "????? ???? ???")
        # Delete related payments
        session.exec(
            delete(Payment).where(Payment.participant_id == participant_id)
        )
        session.delete(db_participant)
        session.commit()
        return {"ok": True}
# ---------------------------------------------------------------------------
# Ù…Ø¯ÛŒØ±ÛŒØª Ù¾Ø±Ø¯Ø§Ø®Øªâ€ŒÙ‡Ø§ (Ø§Ø¯Ù…ÛŒÙ†)
# ---------------------------------------------------------------------------
VALID_PAYMENT_STATUSES = {"pending_review", "confirmed", "rejected"}

@app.get("/payments", dependencies=[Depends(verify_admin_session)])
def get_payments(status: Optional[str] = None):
    if status is not None and status not in VALID_PAYMENT_STATUSES:
        raise HTTPException(400, "ÙˆØ¶Ø¹ÛŒØª Ù†Ø§Ù…Ø¹ØªØ¨Ø±. Ù…Ù‚Ø§Ø¯ÛŒØ± Ù…Ø¬Ø§Ø²: pending_review, confirmed, rejected")

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
@app.post("/payments", dependencies=[Depends(verify_admin_session)])
def create_payment(payment: Payment):
    with Session(engine) as session:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

@app.put("/payments/{payment_id}", dependencies=[Depends(verify_admin_session)])
def update_payment(payment_id: int, payment: Payment):
    with Session(engine) as session:
        db_payment = session.get(Payment, payment_id)
        if not db_payment:
            raise HTTPException(404, "پرداخت یافت نشد")
        data = payment.dict(exclude_unset=True, exclude={"id"})
        for key, value in data.items():
            setattr(db_payment, key, value)
        session.add(db_payment)
        session.commit()
        session.refresh(db_payment)
        return db_payment
@app.post("/payments/{payment_id}/confirm", dependencies=[Depends(verify_admin_session)])
def confirm_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(404, "پرداخت یافت نشد")
        if payment.status != "pending_review":
            raise HTTPException(400, "فقط پرداخت‑های در انتظار بررسی قابل تأیید هستند")
        try:
            transition_status(payment, "confirmed")
        except ValueError as e:
            raise HTTPException(400, str(e))
        payment.reviewed_at = datetime.now().isoformat()
        session.add(payment)
        session.commit()
        session.refresh(payment)
        # Send confirmation message to Telegram user
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
                import asyncio
                asyncio.create_task(
                    telegram_app.bot.send_message(
                        chat_id=payment.telegram_user_id,
                        text=message_text,
                        reply_markup=reply_markup,
                    )
                )
            except Exception as e:
                logger.error(f"⚠️ خطا در ارسال پیام تأیید پرداخت: {e}")
        return payment
@app.post("/payments/{payment_id}/reject", dependencies=[Depends(verify_admin_session)])
def reject_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(404, "پرداخت یافت نشد")
        if payment.status != "pending_review":
            raise HTTPException(400, "فقط پرداخت‑های در انتظار بررسی قابل رد شدن هستند")
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
    # Prevent path traversal — only serve files inside receipts/
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

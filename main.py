import os
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response
from sqlmodel import Session, select

from models import engine, create_db_and_tables, Trip, Participant
from bot import start_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("abarham")

# نگه‌داری رفرنس به اپ تلگرام برای shutdown تمیز
telegram_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ساخت جدول‌های دیتابیس
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

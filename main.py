import os
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response
from sqlmodel import Field, SQLModel, create_engine, Session, select

# وارد کردن مدل‌ها و دیتابیس از models.py
from models import engine, SQLModel, Trip, Participant
from bot import start_bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ساخت جدول‌های دیتابیس
    SQLModel.metadata.create_all(engine)
    
    # اجرای ربات در پس‌زمینه
    bot_task = asyncio.create_task(start_bot())
    print("🤖 وب‌سرور و ربات تلگرام فعال شدند.")
    yield
    bot_task.cancel()

app = FastAPI(lifespan=lifespan)

# ... مابقی اندپوئینت‌های FastAPI شما ...

sqlite_file_name = "quick_abarham.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/sw.js")
def get_sw():
    if os.path.exists("sw.js"):
        return FileResponse("sw.js", headers={"Cache-Control": "no-cache"})
    return Response(content="self.registration.unregister();", media_type="application/javascript")

@app.get("/manifest.json")
def get_manifest():
    if os.path.exists("manifest.json"):
        return FileResponse("manifest.json")
    return {}
@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png", media_type="image/png")
    return {}

@app.get("/sw.js")
def get_sw():
    if os.path.exists("sw.js"):
        return FileResponse("sw.js", media_type="application/javascript")
    return {}

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return "<h1>فایل index.html یافت نشد!</h1>"

@app.get("/trips", response_model=List[Trip])
@app.get("/trips/", response_model=List[Trip])
def get_trips():
    with Session(engine) as session:
        return session.exec(select(Trip)).all()

@app.post("/trips", response_model=Trip)
@app.post("/trips/", response_model=Trip)
def create_trip(trip: Trip):
    with Session(engine) as session:
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return trip

@app.get("/participants", response_model=List[Participant])
@app.get("/participants/", response_model=List[Participant])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()

@app.post("/participants", response_model=Participant)
@app.post("/participants/", response_model=Participant)
def create_participant(participant: Participant):
    with Session(engine) as session:
        session.add(participant)
        session.commit()
        session.refresh(participant)
        return participant
    import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
# نام فایل یا تابع اصلی ربات خود را فراخوانی کنید
# فرض بر این است که داخل bot.py یک تابع اصلی به اسم run_bot یا main دارید
from bot import start_bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    # هنگام روشن شدن سرور، ربات هم در پس‌زمینه اجرا می‌شود
    bot_task = asyncio.create_task(start_telegram_bot())
    yield
    # هنگام خاموش شدن سرور، اجرای ربات متوقف می‌شود
    bot_task.cancel()

app = FastAPI(lifespan=lifespan)

# ... مابقی کدهای قبلی main.py شما
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import start_bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    # شروع ربات تلگرام در پس‌زمینه
    bot_task = asyncio.create_task(start_bot())
    print("🤖 ربات تلگرام در پس‌زمینه FastAPI فعال شد.")
    yield
    # هنگام خاموش شدن سرور
    bot_task.cancel()

app = FastAPI(lifespan=lifespan)

# ... مابقی کدهای قبلی main.py ...
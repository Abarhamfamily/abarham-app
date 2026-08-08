import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, create_engine, Session, select

# --------------------------------------------------
# ۱. ساختار دیتابیس (Models)
# --------------------------------------------------
class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: str
    date: str
    price: float

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int
    full_name: str
    national_id: str
    phone: str

# --------------------------------------------------
# ۲. تنظیمات دیتابیس SQLite
# --------------------------------------------------
sqlite_file_name = "quick_abarham.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

# --------------------------------------------------
# ۳. ساخت اپلیکیشن FastAPI و رویداد Startup
# --------------------------------------------------
app = FastAPI(title="Abarham Tourism App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # ساخت خودکار جدول‌ها هنگام روشن شدن سرور
    SQLModel.metadata.create_all(engine)

# --------------------------------------------------
# ۴. سرویس فایل‌های استاتیک و HTML
# --------------------------------------------------
@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "Abarham API is running!"}

# --------------------------------------------------
# ۵. APIهای مدیریت تورها (Trips)
# --------------------------------------------------
@app.get("/trips", response_model=List[Trip])
def get_trips(session: Session = Depends(get_session)):
    trips = session.exec(select(Trip)).all()
    return trips

@app.post("/trips", response_model=Trip)
def create_trip(trip: Trip, session: Session = Depends(get_session)):
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

# --------------------------------------------------
# ۶. APIهای مدیریت مسافران (Participants)
# --------------------------------------------------
@app.get("/participants", response_model=List[Participant])
def get_participants(trip_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(Participant)
    if trip_id is not None:
        statement = statement.where(Participant.trip_id == trip_id)
    participants = session.exec(statement).all()
    return participants

@app.post("/participants", response_model=Participant)
def create_participant(participant: Participant, session: Session = Depends(get_session)):
    # بررسی وجود تور مرتبط
    trip = session.get(Trip, participant.trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="تور مورد نظر یافت نشد.")
    
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import main as run_bot  # وارد کردن تابع اصلی ربات

@asynccontextmanager
async def lifespan(app: FastAPI):
    # هنگام روشن شدن برنامه، ربات هم در پس‌زمینه روشن می‌شود
    asyncio.create_task(asyncio.to_thread(run_bot))
    yield

# مقداردهی اولیه FastAPI با استفاده از lifespan
app = FastAPI(lifespan=lifespan)

# ... (بقیه مسیرها و آدرس‌های قبلی شما در main.py سر جای خود باقی می‌مانند)
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import main as run_bot  # اتصال به ربات

@asynccontextmanager
async def lifespan(app: FastAPI):
    # اجرای ربات به صورت async پس از بالا آمدن سرور
    asyncio.create_task(asyncio.to_thread(run_bot))
    yield

# افزودن lifespan به FastAPI
app = FastAPI(title="Abarham App", lifespan=lifespan)
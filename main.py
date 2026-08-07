import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, create_engine, Session, select

# ----------------------------------------------------
# ۱. ساختار دیتابیس (Models)
# ----------------------------------------------------
class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: str
    date: str
    price: float

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    full_name: str
    national_id: str
    phone: str
    paid_amount: float
    is_approved: bool = False

# ----------------------------------------------------
# ۲. تنظیمات دیتابیس SQLite
# ----------------------------------------------------
sqlite_file_name = "quick_abarham.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# ----------------------------------------------------
# ۳. ساخت اپلیکیشن FastAPI و تنظیمات CORS
# ----------------------------------------------------
app = FastAPI(title="Abarham App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ----------------------------------------------------
# ۴. مسیرهای مربوط به API (سفرها و مسافران)
# ----------------------------------------------------
@app.get("/trips/", response_model=List[Trip])
def read_trips(session: Session = Depends(get_session)):
    return session.exec(select(Trip)).all()

@app.post("/trips/", response_model=Trip)
def create_trip(trip: Trip, session: Session = Depends(get_session)):
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

@app.get("/participants/", response_model=List[Participant])
def read_participants(trip_id: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(Participant)
    if trip_id:
        query = query.where(Participant.trip_id == trip_id)
    return session.exec(query).all()

@app.post("/participants/", response_model=Participant)
def create_participant(participant: Participant, session: Session = Depends(get_session)):
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant

@app.put("/participants/{participant_id}", response_model=Participant)
def update_participant(participant_id: int, updated_p: Participant, session: Session = Depends(get_session)):
    db_p = session.get(Participant, participant_id)
    if not db_p:
        raise HTTPException(status_code=404, detail="مسافر یافت نشد")
    p_data = updated_p.dict(exclude_unset=True)
    for key, value in p_data.items():
        setattr(db_p, key, value)
    session.add(db_p)
    session.commit()
    session.refresh(db_p)
    return db_p

@app.delete("/participants/{participant_id}")
def delete_participant(participant_id: int, session: Session = Depends(get_session)):
    db_p = session.get(Participant, participant_id)
    if not db_p:
        raise HTTPException(status_code=404, detail="مسافر یافت نشد")
    session.delete(db_p)
    session.commit()
    return {"ok": True}

# ----------------------------------------------------
# ۵. سرو فایل‌های فرانت‌اند (index.html, js, css)
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
def read_root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# اتصال سایر فایل‌های فرانت (مثل sw.js و manifest.json)
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")
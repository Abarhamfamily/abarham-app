import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import Optional, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: str
    date: str
    price: float

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    national_id: str
    phone: str
    payment_status: str
    paid_amount: float
    trip_id: int = Field(foreign_key="trip.id")

sqlite_url = "sqlite:///quick_abarham.db"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="سیستم مدیریت ابرهام")

# --- تنظیمات CORS ---
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

# سرو فایل‌های PWA
@app.get("/")
def read_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/manifest.json")
def read_manifest():
    return FileResponse(os.path.join(BASE_DIR, "manifest.json"))

@app.get("/sw.js")
def read_sw():
    return FileResponse(os.path.join(BASE_DIR, "sw.js"), media_type="application/javascript")

@app.get("/logo.png")
def read_logo():
    return FileResponse(os.path.join(BASE_DIR, "logo.png"))

# --- APIهای تورها ---
@app.get("/trips/", response_model=List[Trip])
def get_trips(session: Session = Depends(get_session)):
    return session.exec(select(Trip)).all()

@app.post("/trips/", response_model=Trip)
def create_trip(trip: Trip, session: Session = Depends(get_session)):
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

@app.put("/trips/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, updated_trip: Trip, session: Session = Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="تور پیدا نشد")
    db_trip.title = updated_trip.title
    db_trip.destination = updated_trip.destination
    db_trip.date = updated_trip.date
    db_trip.price = updated_trip.price
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="تور پیدا نشد")
    participants = session.exec(select(Participant).where(Participant.trip_id == trip_id)).all()
    for p in participants:
        session.delete(p)
    session.delete(db_trip)
    session.commit()
    return {"message": "حذف شد"}

# --- APIهای مسافران ---
@app.get("/participants/", response_model=List[Participant])
def get_participants(session: Session = Depends(get_session)):
    return session.exec(select(Participant)).all()

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
        raise HTTPException(status_code=404, detail="مسافر پیدا نشد")
    db_p.full_name = updated_p.full_name
    db_p.national_id = updated_p.national_id
    db_p.phone = updated_p.phone
    db_p.payment_status = updated_p.payment_status
    db_p.paid_amount = updated_p.paid_amount
    db_p.trip_id = updated_p.trip_id
    session.add(db_p)
    session.commit()
    session.refresh(db_p)
    return db_p

@app.delete("/participants/{participant_id}")
def delete_participant(participant_id: int, session: Session = Depends(get_session)):
    db_p = session.get(Participant, participant_id)
    if not db_p:
        raise HTTPException(status_code=404, detail="مسافر پیدا نشد")
    session.delete(db_p)
    session.commit()
    return {"message": "حذف شد"}
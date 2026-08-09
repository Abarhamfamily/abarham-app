import os
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response
from sqlmodel import Field, SQLModel, create_engine, Session, select

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: Optional[str] = None
    date: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    national_id: str
    phone_number: str
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id")

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
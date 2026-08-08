import os
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlmodel import Field, SQLModel, create_engine, Session, select

# ۱. مدل‌های دیتابیس
class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    national_id: str
    phone_number: str
    trip_id: int = Field(foreign_key="trip.id")

# ۲. ساخت دیتابیس
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

# ۳. خنثی‌سازی کامل Service Worker قبلی
@app.get("/sw.js")
def get_sw():
    return Response(content="self.registration.unregister();", media_type="application/javascript")

@app.get("/manifest.json")
def get_manifest():
    return {}

# ۴. صفحه اصلی سایت بدون وابستگی به فایل خارجی
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>طبیعت‌گردی اَبَرهام</title>
        <style>
            body { font-family: Tahoma, sans-serif; background-color: #f4f7f6; text-align: center; padding: 50px 20px; color: #333; }
            .card { background: white; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #006A4E; }
            .btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #006A4E; color: white; text-decoration: none; border-radius: 6px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🏕 سامانه طبیعت‌گردی اَبَرهام</h1>
            <p>سیستم با موفقیت آنلاین شد و به دیتابیس متصل است.</p>
            <a href="/docs" class="btn">مشاهده مستندات API (Swagger)</a>
        </div>
    </body>
    </html>
    """

# ۵. مسیرهای دریافت داده
@app.get("/trips", response_model=List[Trip])
def get_trips():
    with Session(engine) as session:
        return session.exec(select(Trip)).all()

@app.get("/participants", response_model=List[Participant])
def get_participants():
    with Session(engine) as session:
        return session.exec(select(Participant)).all()
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.exceptions import AppError
from .api.v1 import auth, trips, registrations, payments, wallet, notifications, users
from .api.v1.admin import router as admin_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(UPLOAD_DIR / "profile_images").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(trips.router, prefix="/api/v1/trips", tags=["trips"])
app.include_router(registrations.router, prefix="/api/v1/registrations", tags=["registrations"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["wallet"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Abarham App API", "version": settings.APP_VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}



# Abarham App

اپلیکیشن کاربری ابرهام برای مسافران — سیستمی کاملاً مستقل از `abarham_quick`
(بدون اشتراک کد، مدل یا دیتابیس).

این پروژه اسکلت **فاز ۱** طبق سند معماری است. منطق کسب‌وکار پیچیده‌تر
(ثبت‌نام گروهی/ظرفیت، پرداخت، کیف پول) به‌صورت TODO با ارجاع دقیق به فاز و
بخش مربوطه در کد علامت‌گذاری شده تا در فازهای بعدی تکمیل شود.

## توسعه محلی (بدون Docker)

### بک‌اند

```bash
cd backend
python -m venv venv
source venv/bin/activate   # ویندوز: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
# در صورت نیاز مقادیر .env را ویرایش کنید (پیش‌فرض: SQLite محلی)

# اجرای مایگریشن‌ها (پس از اولین commit مدل‌ها، یک ریویژن اولیه بسازید):
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

uvicorn src.main:app --reload
# مستندات API: http://localhost:8000/api/docs
```

### فرانت‌اند

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
# http://localhost:5173
```

### اجرای تست‌ها

```bash
cd backend
pytest
```

## توسعه با Docker (فاز ۱، اختیاری)

```bash
docker compose up --build
```

- بک‌اند: http://localhost:8000
- فرانت‌اند: http://localhost:5173
- دیتابیس PostgreSQL: پورت 5432

## ساختار پروژه

```
abarham-app/
├── backend/
│   ├── src/
│   │   ├── api/v1/      # روترهای FastAPI (auth, trips, registrations, payments, wallet, notifications)
│   │   ├── core/        # config, database, security, deps, exceptions
│   │   ├── domain/      # dataclass های دامنه، مستقل از ORM
│   │   ├── models/      # مدل‌های SQLAlchemy
│   │   ├── schemas/     # مدل‌های Pydantic برای request/response
│   │   ├── services/    # (خالی — منطق کسب‌وکار فازهای بعدی)
│   │   └── utils/
│   ├── migrations/      # Alembic
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/         # کلاینت‌های axios
│       ├── components/
│       ├── pages/
│       ├── store/       # zustand
│       └── types/
├── docker-compose.yml
└── ARCHITECTURE.md
```

## وضعیت فعلی endpoint ها

| Endpoint | وضعیت |
|---|---|
| `POST /api/v1/auth/register` | ✅ کارکردی (کاربر غیرفعال می‌سازد) |
| `POST /api/v1/auth/login` | ✅ کارکردی |
| `POST /api/v1/auth/verify-otp` | ⏳ Phase 2 (پیاده‌سازی OTP واقعی) |
| `GET /api/v1/trips*` | ✅ کاملاً کارکردی |
| `GET /api/v1/registrations/my`, `/{id}` | ✅ کارکردی |
| `POST /api/v1/registrations` | ⏳ Phase 4 (قفل خوش‌بینانه + waitlist) |
| `GET /api/v1/wallet`, `/transactions` | ✅ کارکردی |
| `POST /api/v1/wallet/deposit`, `/withdraw` | ⏳ Phase 5 |
| `GET /api/v1/payments/{id}` | ✅ کارکردی |
| `POST /api/v1/payments*` | ⏳ Phase 6 (idempotency) |
| `GET/PUT /api/v1/notifications*` | ✅ کارکردی |

جزئیات کامل هر فاز در `ARCHITECTURE.md` است.

## معماری

برای جزئیات کامل تصمیم‌های معماری، طرح دیتابیس، و قوانین کسب‌وکار حیاتی
(Payment Isolation، Optimistic Locking، Idempotency) به `ARCHITECTURE.md`
مراجعه کنید.

## لایسنس

Proprietary

# راهنمای یکپارچه‌سازی Admin Panel با پروژه‌ی موجود

این پکیج **هیچ فایل موجودی از پروژه‌ی `abarham-app` را تغییر نداده**. همه‌چیز
فایل‌های کاملاً جدید هستند که باید کپی و طبق مراحل زیر به پروژه‌ی اصلی وصل
شوند.

هر مرحله واقعاً روی یک کپی از پروژه‌ی شما اجرا و تست شده (نصب dependency،
اجرای migration، بالا آوردن سرور، لاگین ادمین، ساخت تور، تأیید پرداخت،
تعدیل کیف‌پول، و بررسی جداسازی کامل توکن ادمین از توکن کاربر). فقط کافی است
همین مراحل را تکرار کنید.

## پیش‌نیاز

- migration فعلی پروژه‌ی شما باید دقیقاً روی `ef9dc035097e` باشد (طبق
  چیزی که خودتان گفتید). اگر migration جدیدتری بعد از آن اضافه کرده‌اید،
  فایل migration این پکیج (`a1b2c3d4e5f6_add_admins_table.py`) را طوری
  ویرایش کنید که `down_revision` به جدیدترین revision شما اشاره کند، نه
  به `ef9dc035097e`.

## مرحله ۱ — کپی فایل‌های بک‌اند

محتوای پوشه‌ی `backend-addon/` را — **با همان ساختار پوشه‌ای** — داخل
`backend/` پروژه‌ی اصلی کپی کنید. یعنی:

```
backend-addon/src/models/admin.py              → backend/src/models/admin.py
backend-addon/src/core/admin_security.py        → backend/src/core/admin_security.py
backend-addon/src/schemas/admin_*.py            → backend/src/schemas/admin_*.py  (۸ فایل)
backend-addon/src/api/v1/admin/                 → backend/src/api/v1/admin/       (کل پوشه)
backend-addon/migrations/versions/a1b2c3d4e5f6_add_admins_table.py
                                                 → backend/migrations/versions/
backend-addon/scripts/                          → backend/scripts/  (کل پوشه)
backend-addon/tests/admin/                      → backend/tests/admin/  (کل پوشه)
```

هیچ‌کدام از این فایل‌ها با فایل موجودی هم‌نام نیستند، پس هیچ‌چیزی
overwrite نمی‌شود.

## مرحله ۲ — افزودن روتر ادمین به `main.py`

فایل `backend/src/main.py` را باز کنید. دقیقاً همان الگویی که برای
روترهای دیگر (`auth`, `trips`, ...) استفاده شده را برای admin هم تکرار
کنید:

**در بخش import ها**، این خط را اضافه کنید:
```python
from .api.v1.admin import router as admin_router
```

**در بخش `app.include_router(...)`**، این خط را اضافه کنید:
```python
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
```

مثال کامل (فقط خطوط جدید نشان داده شده‌اند، بقیه‌ی فایل دست‌نخورده
می‌ماند):

```python
from .api.v1 import auth, trips, registrations, payments, wallet, notifications
from .api.v1.admin import router as admin_router   # <-- خط جدید

# ...

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(trips.router, prefix="/api/v1/trips", tags=["trips"])
app.include_router(registrations.router, prefix="/api/v1/registrations", tags=["registrations"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["wallet"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])   # <-- خط جدید
```

## مرحله ۳ — بررسی `requirements.txt`

هیچ dependency جدیدی لازم نیست. Admin Panel از همان کتابخانه‌هایی استفاده
می‌کند که پروژه‌ی فعلی از قبل دارد: `python-jose`, `passlib[bcrypt]`,
`bcrypt==4.0.1`, `sqlalchemy`, `pydantic`. اگر با `pip freeze` این‌ها را
دارید، نیازی به نصب چیز جدیدی نیست.

## مرحله ۴ — اجرای Migration

```bash
cd backend
alembic upgrade head
```

باید خروجی مشابه این را ببینید:
```
Running upgrade ef9dc035097e -> a1b2c3d4e5f6, add admins table
```

این migration **فقط جدول `admins` را اضافه می‌کند** و هیچ جدول موجودی را
لمس نمی‌کند (تست شده — کل داده‌های User App دست‌نخورده می‌ماند).

## مرحله ۵ — ساخت اولین ادمین

هیچ endpoint عمومی برای ساخت ادمین وجود ندارد (عمداً — برای امنیت). از
اسکریپت CLI استفاده کنید:

```bash
cd backend
python3 -m scripts.create_admin \
  --username admin \
  --password "یک-رمز-قوی-اینجا" \
  --full-name "نام مدیر" \
  --role super_admin
```

## مرحله ۶ — اجرای سرور بک‌اند

```bash
uvicorn src.main:app --reload
```

مستندات API کامل (شامل همه‌ی endpoint های `/api/v1/admin/*`) در
`http://localhost:8000/api/docs` قابل مشاهده است.

## مرحله ۷ — راه‌اندازی فرانت‌اند Admin Panel

پوشه‌ی `admin-frontend/` این پکیج یک پروژه‌ی React مستقل و کامل است —
**نیازی به کپی داخل پروژه‌ی frontend فعلی نیست**؛ می‌تواند به‌صورت یک
سرویس کاملاً جدا کنار User App اجرا شود (مثلاً `frontend/` برای کاربران و
`admin-frontend/` برای ادمین‌ها، دو پروژه‌ی مجزا کنار هم).

```bash
cd admin-frontend
npm install
cp .env.example .env
npm run dev
# http://localhost:5174
```

با نام کاربری/رمزی که در مرحله‌ی ۵ ساختید وارد شوید.

## مرحله ۸ (اختیاری) — اجرای تست‌ها

```bash
cd backend
pytest tests/admin -v
```

باید ۱۵ تست پاس شود (احراز هویت، جداسازی توکن، CRUD تورها، تأیید/رد
پرداخت، تعدیل کیف‌پول).

---

## چرا این معماری؟ (خلاصه‌ی تصمیم‌های طراحی)

| تصمیم | دلیل |
|---|---|
| جدول `Admin` کاملاً جدا از `User` | خواسته‌ی صریح شما: «Admin Panel باید کاملاً از User App جدا باشد» |
| نوع توکن JWT جدا (`admin_access` به‌جای `access`) | حتی با یک `SECRET_KEY` مشترک، توکن ادمین در endpoint های کاربر و برعکس رد می‌شود (تست شده با ۴ سناریوی کراس‌توکن) |
| بدون endpoint عمومی ثبت‌نام ادمین | جلوگیری از ساخت ادمین توسط کاربران عادی؛ فقط از طریق CLI روی سرور |
| فرانت‌اند در پروژه‌ی React جدا (نه داخل `frontend/` فعلی) | خواسته‌ی صریح شما: «User App فعلی نباید تغییر کند» و «routing، state آن باعث تداخل نشود» |
| پورت پیش‌فرض متفاوت (5174 در برابر 5173) | اجرای هم‌زمان هر دو اپ در توسعه‌ی محلی بدون تداخل |
| localStorage key متفاوت (`abarham-admin-auth`) | حتی اگر هر دو اپ روی یک دامنه سرو شوند، session ها با هم قاطی نمی‌شوند |
| چک ظرفیت حذف تور در سطح اپلیکیشن، نه فقط DB constraint | SQLite (دیتابیس Development) به‌صورت پیش‌فرض foreign key را enforce نمی‌کند؛ این باگ واقعی در حین تست پیدا و رفع شد |

## وضعیت endpoint های Admin Panel

| بخش | Endpoint ها | وضعیت |
|---|---|---|
| Auth | login, refresh, logout, me, change-password | ✅ کامل و تست‌شده |
| Dashboard | آمار کلی (کاربران، تورها، ثبت‌نام‌ها، پرداخت‌ها، کیف‌پول) | ✅ کامل |
| Users | لیست، جست‌وجو، جزئیات، فعال/غیرفعال کردن | ✅ کامل |
| Trips | CRUD کامل (با اعتبارسنجی ظرفیت و جلوگیری از حذف تور دارای ثبت‌نام) | ✅ کامل |
| Registrations | لیست، فیلتر، جزئیات، تغییر وضعیت دستی | ✅ کامل |
| Payments | لیست، تأیید (به‌روزرسانی خودکار `deposit_paid`/وضعیت ثبت‌نام)، رد | ✅ کامل |
| Wallet | لیست کیف‌پول‌ها، تاریخچه‌ی تراکنش، تعدیل موجودی (با جلوگیری از موجودی منفی) | ✅ کامل |
| Notifications | لیست، ارسال به یک کاربر یا همه‌ی کاربران فعال | ✅ کامل |

نکته: منطق تغییر وضعیت ثبت‌نام توسط ادمین، **ظرفیت باقی‌مانده‌ی تور
(`remaining_capacity`) را خودکار تغییر نمی‌دهد** — چون در User App فعلی
هنوز هیچ مکانیزمی برای کاهش خودکار این فیلد وجود ندارد (endpoint
`POST /registrations` هنوز stub است، طبق TODO موجود در پروژه). وقتی آن
بخش در فازهای بعدی پیاده‌سازی شد، این نکته باید در Admin Panel هم بازبینی
شود.

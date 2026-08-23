# Abarham App — Architecture Reference

این فایل خلاصه‌ی تصمیم‌های معماری حیاتی است. نسخه‌ی کامل و مفصل (شامل تمام
جدول‌ها، API contract کامل، و pseudocode سرویس‌ها) همان سندی است که مبنای
ساخت این اسکلت قرار گرفت؛ اگر آن سند را جداگانه نگه می‌دارید، این فایل را
لینک بدهید یا محتوای کامل را جایگزین این خلاصه کنید.

## قوانین کسب‌وکار حیاتی (هرگز نقض نشوند)

1. **Payment Isolation** — هر `Payment` باید `registration_id` داشته باشد.
   هرگز پرداختی بدون context ثبت‌نام ایجاد نشود.
2. **Capacity Control** — از قفل خوش‌بینانه (`Trip.version`) برای جلوگیری از
   overbooking استفاده شود:
   ```sql
   UPDATE trips
   SET remaining_capacity = remaining_capacity - 1, version = version + 1
   WHERE id = :trip_id AND remaining_capacity > 0 AND version = :current_version
   ```
   اگر ۰ ردیف تغییر کرد → ظرفیت پر است یا race condition رخ داده →
   کاربر به Waitlist اضافه شود.
3. **Idempotency** — همه‌ی عملیات پرداخت/واریز باید `idempotency_key`
   داشته باشند و پیش از ساخت رکورد جدید، وجود کلید تکراری چک شود.
4. **Wallet Transactions** — موجودی کیف پول هرگز مستقیم تغییر نکند؛ همیشه
   از طریق رکورد `Transaction` انجام شود.

## فازهای توسعه

| فاز | موضوع | وضعیت در این اسکلت |
|---|---|---|
| 0 | معماری | ✅ کامل |
| 1 | اسکلت پروژه | ✅ کامل (همین ریپازیتوری) |
| 2 | احراز هویت (OTP واقعی) | ⏳ TODO در `api/v1/auth.py` |
| 3 | تورها | ✅ کامل (read-only) |
| 4 | ثبت‌نام (ظرفیت، Waitlist) | ⏳ TODO در `api/v1/registrations.py` |
| 5 | کیف پول (واریز/برداشت با قفل) | ⏳ TODO در `api/v1/wallet.py` |
| 6 | پرداخت (idempotency، رسید) | ⏳ TODO در `api/v1/payments.py` |
| 7 | فرانت‌اند کامل | ⏳ صفحات پایه ساخته شده، منطق ناقص |
| 8 | تست و سخت‌سازی | ⏳ |

## چرا Repository Pattern کامل استفاده نشد؟

طبق تصمیم اولیه‌ی معماری: در این مرحله انتزاع زیاد فایده‌ی فوری ندارد.
دسترسی به دیتابیس مستقیماً در روترها (از طریق SQLAlchemy AsyncSession) انجام
می‌شود. اگر پیچیدگی منطق کسب‌وکار در فازهای بعدی بالا رفت، می‌توان لایه‌ی
Service را طبق نمودار زیر اضافه کرد و سپس در صورت نیاز به Repository ارتقا
داد:

```
API Layer (FastAPI routes)
   → Service Layer (RegistrationService, PaymentService, WalletService, ...)
      → Data Access (DAO functions ساده)
         → Database (SQLAlchemy Models)
```

## Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + Alembic + Pydantic v2 + JWT (python-jose) + bcrypt
- **Frontend:** React 18 + TypeScript + Vite + React Router + React Query + Zustand + React Hook Form + Zod
- **Database:** SQLite (dev) / PostgreSQL 15+ (prod)
- **Infra:** Docker Compose (اختیاری، فاز ۱)

## نکات پیاده‌سازی حیاتی برای فازهای باقی‌مانده

```python
# Payment Isolation
# ALWAYS enforce payment → registration scope
# NEVER allow payment without registration_id
# ALWAYS validate payment amount against registration

# Capacity Management
# Use optimistic locking on Trip
# Update query must check version and remaining_capacity
# If update affects 0 rows → add to waitlist

# Wallet Balance
# ALWAYS use transactions for balance changes
# NEVER update balance directly
# ALWAYS validate balance before withdrawal

# Idempotency
# Use idempotency_key for payments and deposits
# Check before creating new records
# Return existing record if duplicate
```

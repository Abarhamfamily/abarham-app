# Abarham App — Admin Panel (پکیج مستقل)

این پکیج پنل مدیریت پروژه‌ی Abarham App است: کاملاً جدا از User App، آماده
برای جایگذاری در پروژه‌ی اصلی توسط خودتان.

**مهم:** برای راه‌اندازی، حتماً و دقیقاً `INTEGRATION.md` را دنبال کنید.
تمام مراحل آن (کپی فایل‌ها، افزودن دو خط به `main.py`، اجرای migration،
ساخت ادمین، اجرای سرور و تست‌ها) واقعاً روی یک کپی از پروژه‌ی شما اجرا و
تأیید شده‌اند.

## محتویات پکیج

```
abarham-admin-panel/
├── INTEGRATION.md          ← از همین‌جا شروع کنید
├── README.md               ← همین فایل
├── backend-addon/          ← فایل‌های جدید برای کپی داخل backend/ پروژه‌ی اصلی
│   ├── src/models/admin.py
│   ├── src/core/admin_security.py
│   ├── src/schemas/admin_*.py
│   ├── src/api/v1/admin/
│   ├── migrations/versions/a1b2c3d4e5f6_add_admins_table.py
│   ├── scripts/create_admin.py
│   └── tests/admin/
└── admin-frontend/          ← اپلیکیشن React مستقل پنل مدیریت
    ├── src/
    ├── package.json
    └── vite.config.ts
```

## خلاصه‌ی خیلی سریع

```bash
# ۱. کپی فایل‌های backend-addon داخل backend/ پروژه‌ی اصلی (طبق INTEGRATION.md مرحله ۱)

# ۲. افزودن دو خط به backend/src/main.py (طبق INTEGRATION.md مرحله ۲)

# ۳. اجرای migration
cd backend && alembic upgrade head

# ۴. ساخت اولین ادمین
python3 -m scripts.create_admin --username admin --password "رمز-قوی" --full-name "نام مدیر" --role super_admin

# ۵. اجرای بک‌اند (همان دستور همیشگی پروژه)
uvicorn src.main:app --reload

# ۶. اجرای فرانت‌اند ادمین (در ترمینال جدا)
cd admin-frontend
npm install
cp .env.example .env
npm run dev
# http://localhost:5174
```

## آنچه تضمین شده

- ✅ هیچ فایل موجود پروژه تغییر نکرده (فقط شما دو خط به `main.py` اضافه می‌کنید)
- ✅ `admins` جدولی کاملاً جدا از `users` است؛ هیچ داده‌ی کاربری لمس نمی‌شود
- ✅ توکن‌های JWT ادمین و کاربر کاملاً مجزا هستند (تست شده: توکن ادمین روی
  endpoint های کاربر رد می‌شود و برعکس)
- ✅ فرانت‌اند ادمین یک پروژه‌ی React کاملاً جدا با state، routing، و
  localStorage مستقل از User App است
- ✅ همه‌چیز — migration، اسکریپت ساخت ادمین، سرور بک‌اند، build فرانت‌اند،
  و ۲۰ تست خودکار — روی یک کپی واقعی از پروژه‌ی شما اجرا و تأیید شده است

جزئیات کامل معماری، دلایل تصمیم‌ها، و جدول وضعیت endpoint ها در
`INTEGRATION.md` است.

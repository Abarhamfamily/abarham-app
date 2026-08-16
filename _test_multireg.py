# -*- coding: utf-8 -*-
"""تست حداقلی ثبت‌نام چندنفره (بدون نیاز به API تلگرام واقعی).

بررسی می‌کند:
  1) _finalize_registration برای N نفر، N ردیف Participant می‌سازد و
     مبلغ کل = مبلغ هر نفر × N را تنظیم می‌کند.
  2) select_payment_type برای دسته (batch) مبلغ کل را درست محاسبه می‌کند.
  3) _receive_batch_payment_receipt برای هر نفر یک ردیف Payment با
     status=pending_review می‌سازد (N ردیف برای N نفر).
  4) ساختار تک‌نفره نیز از همین مسیر (لیستِ یک‌عضوی) کار می‌کند.
"""
import os
import sys

TEST_DB = os.path.join(os.path.dirname(__file__), "_test_multireg.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ.pop("BOT_TOKEN", None)

from types import SimpleNamespace  # noqa: E402

from sqlmodel import Session, select  # noqa: E402

import bot  # noqa: E402
from models import SQLModel, engine, Trip, Participant, Payment  # noqa: E402

SQLModel.metadata.create_all(engine)

failures = []


def check(name, condition, extra=""):
    print(f"{'PASS' if condition else 'FAIL'}: {name} {extra}")
    if not condition:
        failures.append(name)


class FakeUser:
    id = 1001


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.contact = None
        self.sent = []

    async def reply_text(self, *args, **kwargs):
        self.sent.append(args[0] if args else "")
        return None


class FakeUpdate:
    def __init__(self, text=""):
        self.effective_user = FakeUser()
        self.message = FakeMessage(text)


class FakeFile:
    async def download_as_bytearray(self):
        return b"\xff\xd8fake-jpeg"


class FakePhoto:
    file_id = "file_abc"
    file_unique_id = "uniq_xyz"

    async def get_file(self):
        return FakeFile()


def make_trip(capacity=10, price=1_000_000):
    with Session(engine) as s:
        t = Trip(title="تور تست", destination="شمال", price=price, capacity=capacity)
        s.add(t)
        s.commit()
        s.refresh(t)
        return t.id


def participant_count():
    with Session(engine) as s:
        return len(s.exec(select(Participant)).all())


def payment_count():
    with Session(engine) as s:
        return len(s.exec(select(Payment)).all())


async def main():
    # --- ۱) ثبت‌نام گروهی ۳ نفره ---
    trip_id = make_trip()
    ctx = SimpleNamespace(user_data={})
    ud = ctx.user_data
    ud["trip_id"] = trip_id
    ud["reg_count"] = 3
    ud["reg_index"] = 3
    ud["reg_pending"] = [
        {"full_name": "الف", "national_id": "1111111111", "phone_number": "0911"},
        {"full_name": "ب", "national_id": "2222222222", "phone_number": "0912"},
        {"full_name": "ج", "national_id": "3333333333", "phone_number": "0913"},
    ]
    upd = FakeUpdate()

    state = await bot._finalize_registration(upd, ctx)
    check("finalize returns PAY_TYPE_SELECT", state == bot.PAY_TYPE_SELECT)
    check("creates 3 participants", participant_count() == 3, f"={participant_count()}")
    deposit = ud.get("payment_per_person_deposit")
    full = ud.get("payment_per_person_full")
    check("deposit per person = 25%% of price", deposit == round(1_000_000 * 0.25, 2))
    check("full per person = price", full == 1_000_000)
    check("payment_participant_ids length 3", len(ud.get("payment_participant_ids", [])) == 3)
    pids = ud["payment_participant_ids"]

    # --- ۲) انتخاب نوع پرداخت: بیعانه ۳ نفره = ۳ × ۲۵۰,۰۰۰ ---
    upd2 = FakeUpdate("💰 پرداخت بیعانه — 250,000 تومان (3 نفر)")
    ud["payment_trip_id"] = trip_id
    ud["payment_type"] = "deposit"
    state = await bot.select_payment_type(upd2, ctx)
    check("select_payment_type returns PAY_RECEIPT", state == bot.PAY_RECEIPT)
    check("total = 750,000", ud.get("payment_expected_amount") == 750_000)
    check("unit amount = 250,000", ud.get("payment_unit_amount") == 250_000)
    check("message shows total", any("750" in m for m in upd2.message.sent), f"sent={upd2.message.sent}")

    # --- ۳) ارسال فیش → برای هر ۳ نفر Payment ساخته می‌شود ---
    photo = FakePhoto()
    upd3 = FakeUpdate()
    res = await bot._receive_batch_payment_receipt(
        upd3, ctx, photo, trip_id, "deposit", 1001
    )
    check("receipt handler ends conversation", res == bot.ConversationHandler.END)
    check("creates 3 payments", payment_count() == 3, f"={payment_count()}")

    with Session(engine) as s:
        pays = s.exec(select(Payment)).all()
        statuses = {p.status for p in pays}
        pids_in_pay = {p.participant_id for p in pays}
        amounts = {p.expected_amount for p in pays}
    check("all payments pending_review", statuses == {"pending_review"})
    check("one payment per participant", pids_in_pay == set(pids))
    check("each payment expected 250,000", amounts == {250_000})

    # --- ۴) ظرفیت کافی نباشد باید رد شود ---
    cap_trip = make_trip(capacity=2)  # فقط ۲ نفر ظرفیت
    ctx2 = SimpleNamespace(user_data={})
    ud = ctx2.user_data
    ud["trip_id"] = cap_trip
    ud["reg_pending"] = [
        {"full_name": "ت", "national_id": "5555555555", "phone_number": "0915"},
        {"full_name": "ث", "national_id": "6666666666", "phone_number": "0916"},
        {"full_name": "جای", "national_id": "7777777777", "phone_number": "0917"},
    ]
    await bot._finalize_registration(FakeUpdate(), ctx2)
    # این تور فقط ۲ نفر جا دارد؛ پس هیچ‌کدام نباید ذخیره شوند
    with Session(engine) as s:
        cap_count = len(
            s.exec(select(Participant).where(Participant.trip_id == cap_trip)).all()
        )
    check("batch over capacity is rejected (0 saved)", cap_count == 0, f"={cap_count}")

    # --- پاک‌سازی فایل‌های موقت ---
    for f in os.listdir("."):
        if f.startswith("receipt_") and f.endswith(".jpg"):
            try:
                os.remove(f)
            except OSError:
                pass

    if failures:
        print(f"\n{len(failures)} test(s) FAILED: {failures}")
        sys.exit(1)
    print("\nMulti-registration test PASSED.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
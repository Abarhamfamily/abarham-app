import os
import logging
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
from sqlmodel import Session, select

from models import engine, Participant, Trip, Payment
from payment import (
    calculate_deposit,
    calculate_full_amount,
    get_confirmed_total,
    is_fully_paid,
    has_pending,
    save_receipt,
)

logger = logging.getLogger("abarham.bot")


# ---------------------------------------------------------------------------
# وضعیت‌های Conversation
# ---------------------------------------------------------------------------

TRIP_SELECT, COUNT, NAME, NATIONAL_ID, PHONE = range(5)

PAY_TRIP_SELECT, PAY_TYPE_SELECT, PAY_RECEIPT = range(5, 8)


# ---------------------------------------------------------------------------
# اطلاعات حساب/کارت مقصد
# ---------------------------------------------------------------------------

PAYMENT_ACCOUNT_INFO = (
    "شماره کارت: 9884-7056-8619-6219\n"
    "به نام: [منفرد نحفی]\n"
    "بانک: [سامان]"
)


# ===========================================================================
# ثبت‌نام
# ===========================================================================

async def start_registration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # پاک‌سازی اطلاعات ثبت‌نام قبلی (در صورت وجود)
    for key in ["reg_count", "reg_pending", "reg_current", "reg_index"]:
        context.user_data.pop(key, None)

    await update.message.reply_text(
        "👋 به ابرهام خوش آمدید!\n\n"
        "شما می‌توانید از اینجا برای تورهای فعال ثبت‌نام کرده و پرداخت را انجام دهید."
    )

    with Session(engine) as session:
        trips = session.exec(
            select(Trip).where(Trip.status == "active")
        ).all()

    if not trips:
        await update.message.reply_text(
            "❌ در حال حاضر هیچ توری برای ثبت‌نام فعال نیست."
        )
        return ConversationHandler.END

    context.user_data["trips_map"] = {
        f"{t.title} (کد {t.id})": t.id
        for t in trips
    }

    keyboard = [
        [button]
        for button in context.user_data["trips_map"].keys()
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        resize_keyboard=True,
    )

    await update.message.reply_text(
        "لطفاً توری که می‌خواهید در آن ثبت‌نام کنید را انتخاب کنید:",
        reply_markup=reply_markup,
    )

    return TRIP_SELECT


async def select_trip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    selected_option = update.message.text

    trips_map = context.user_data.get("trips_map", {})

    if selected_option not in trips_map:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های کیبورد را انتخاب کنید:"
        )
        return TRIP_SELECT

    context.user_data["trip_id"] = trips_map[selected_option]
    context.user_data["selected_trip_title"] = selected_option

    await update.message.reply_text(
        "چند نفر می‌خواهید برای این تور ثبت‌نام کنید؟\n\n"
        "مثلاً برای ۲ نفر عدد ۲ را ارسال کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return COUNT


async def get_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    raw = update.message.text.strip()

    if not raw.isdigit():
        await update.message.reply_text(
            "لطفاً تعداد نفرات را به‌صورت عدد وارد کنید (مثلاً ۲):"
        )
        return COUNT

    count = int(raw)

    if count < 1:
        await update.message.reply_text(
            "تعداد نفرات باید حداقل ۱ باشد. لطفاً دوباره وارد کنید:"
        )
        return COUNT

    if count > 10:
        await update.message.reply_text(
            "برای ثبت‌نام بیشتر از ۱۰ نفر، لطفاً با پشتیبانی تماس بگیرید.\n"
            "حداکثر ۱۰ نفر در یک بار ثبت‌نام امکان‌پذیر است."
        )
        return COUNT

    trip_id = context.user_data.get("trip_id")

    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if trip and trip.capacity:
            current_count = len(
                session.exec(
                    select(Participant).where(Participant.trip_id == trip_id)
                ).all()
            )
            available = trip.capacity - current_count
            if count > available:
                await update.message.reply_text(
                    f"❌ ظرفیت این تور کافی نیست؛ فقط {available} نفر دیگر "
                    "ظرفیت باقی مانده است."
                )
                return COUNT

    context.user_data["reg_count"] = count
    context.user_data["reg_pending"] = []
    context.user_data["reg_current"] = {}
    context.user_data["reg_index"] = 0

    await update.message.reply_text(
        f"تعداد {count} نفر برای ثبت‌نام انتخاب شد.\n\n"
        "لطفاً نام و نام خانوادگی نفر ۱ را وارد کنید:",
        reply_markup=ReplyKeyboardRemove(),
    )

    return NAME


async def get_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    full_name = update.message.text.strip()

    if len(full_name) < 3:
        await update.message.reply_text(
            "لطفاً نام و نام خانوادگی معتبر وارد کنید:"
        )
        return NAME

    context.user_data.setdefault("reg_current", {})["full_name"] = full_name

    person_label = context.user_data.get("reg_index", 0) + 1

    await update.message.reply_text(
        f"کد ملی {person_label} را وارد کنید:"
    )

    return NATIONAL_ID


async def get_national_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    national_id = update.message.text.strip()

    if not national_id.isdigit() or len(national_id) != 10:
        await update.message.reply_text(
            "کد ملی باید یک عدد ۱۰ رقمی باشد. لطفاً دوباره وارد کنید:"
        )
        return NATIONAL_ID

    trip_id = context.user_data.get("trip_id")

    # جلوگیری از ثبت کد ملی تکراری در همان دسته (چندنفره)
    reg_pending = context.user_data.get("reg_pending", [])
    if any(r.get("national_id") == national_id for r in reg_pending):
        await update.message.reply_text(
            "❌ این کد ملی قبلاً در همین لیست ثبت‌نام وارد شده است."
        )
        return NATIONAL_ID

    # جلوگیری از ثبت‌نام تکراری نسبت به دیتابیس
    with Session(engine) as session:
        existing = session.exec(
            select(Participant).where(
                Participant.national_id == national_id,
                Participant.trip_id == trip_id,
            )
        ).first()

    if existing:
        await update.message.reply_text(
            "❌ این کد ملی قبلاً برای این تور ثبت‌نام شده است.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    context.user_data.setdefault("reg_current", {})["national_id"] = national_id

    person_label = context.user_data.get("reg_index", 0) + 1

    phone_keyboard = [
        [
            KeyboardButton(
                "📱 ارسال شماره تماس من",
                request_contact=True,
            )
        ]
    ]

    reply_markup = ReplyKeyboardMarkup(
        phone_keyboard,
        one_time_keyboard=True,
        resize_keyboard=True,
    )

    await update.message.reply_text(
        f"شماره تماس نفر {person_label} را وارد کنید "
        "یا از دکمه زیر جهت ارسال سریع استفاده کنید:",
        reply_markup=reply_markup,
    )

    return PHONE


# ===========================================================================
# دریافت شماره تماس و تکمیل ثبت‌نام
# ===========================================================================

async def get_phone_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = (
        update.message.contact.phone_number
        if update.message.contact
        else update.message.text.strip()
    )

    if not phone_number:
        await update.message.reply_text("لطفاً شماره تماس خود را وارد کنید:")
        return PHONE

    reg_current = context.user_data.setdefault("reg_current", {})
    reg_current["phone_number"] = phone_number

    reg_pending = context.user_data.setdefault("reg_pending", [])
    reg_pending.append(reg_current)

    reg_count = context.user_data.get("reg_count", 1)
    new_index = context.user_data.get("reg_index", 0) + 1
    context.user_data["reg_index"] = new_index

    if new_index < reg_count:
        # هنوز نفرات دیگری باقی مانده‌اند → دریافت اطلاعات نفر بعد
        context.user_data["reg_current"] = {}
        next_label = new_index + 1

        await update.message.reply_text(
            f"✅ اطلاعات نفر {new_index} از {reg_count} ثبت شد.\n\n"
            f"لطفاً نام و نام خانوادگی نفر {next_label} را وارد کنید:",
            reply_markup=ReplyKeyboardRemove(),
        )

        return NAME

    # همه‌ی نفرات جمع‌آوری شدند → ثبت نهایی و ورود به مرحله پرداخت
    return await _finalize_registration(update, context)


async def _finalize_registration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    reg_pending = context.user_data.get("reg_pending", [])
    telegram_user_id = update.effective_user.id
    trip_id = context.user_data.get("trip_id")

    try:
        with Session(engine) as session:
            trip = session.get(Trip, trip_id)

            if not trip:
                await update.message.reply_text(
                    "❌ این تور دیگر موجود نیست.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END

            trip_price = trip.price
            trip_title = trip.title

            # ظرفیت تور برای کل تعداد نفرات
            if trip.capacity:
                current_count = len(
                    session.exec(
                        select(Participant).where(
                            Participant.trip_id == trip_id
                        )
                    ).all()
                )

                if current_count + len(reg_pending) > trip.capacity:
                    await update.message.reply_text(
                        "❌ ظرفیت این تور برای این تعداد نفر تکمیل شده است.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return ConversationHandler.END

            # جلوگیری از ثبت‌نام تکراری در دیتابیس
            for reg in reg_pending:
                existing = session.exec(
                    select(Participant).where(
                        Participant.national_id == reg["national_id"],
                        Participant.trip_id == trip_id
                    )
                ).first()

                if existing:
                    await update.message.reply_text(
                        f"❌ کد ملی {reg['national_id']} قبلاً برای این تور "
                        "ثبت‌نام شده است.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return ConversationHandler.END

            # ساخت شرکت‌کننده‌ها
            participant_ids = []
            for reg in reg_pending:
                new_participant = Participant(
                    full_name=reg["full_name"],
                    national_id=reg["national_id"],
                    phone_number=reg["phone_number"],
                    trip_id=trip_id,
                    telegram_user_id=telegram_user_id
                )
                session.add(new_participant)
                session.flush()
                participant_ids.append(new_participant.id)

            session.commit()

        count = len(participant_ids)

        context.user_data["payment_trip_id"] = trip_id
        context.user_data["payment_participant_ids"] = participant_ids
        context.user_data["payment_participant_id"] = participant_ids[0]
        context.user_data["payment_per_person_deposit"] = calculate_deposit(
            trip_price
        )
        context.user_data["payment_per_person_full"] = calculate_full_amount(
            trip_price, 0
        )

        # مبلغ کل = مبلغِ هر نفر × تعداد نفرات
        deposit_total = round(
            context.user_data["payment_per_person_deposit"] * count, 2
        )
        full_total = round(
            context.user_data["payment_per_person_full"] * count, 2
        )

        people_suffix = f" ({count} نفر)" if count > 1 else ""
        keyboard = [
            [f"💰 پرداخت بیعانه — {deposit_total:,.0f} تومان{people_suffix}"],
            [f"💵 پرداخت کامل — {full_total:,.0f} تومان{people_suffix}"],
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        )

        summary = "\n".join(
            f"• {reg['full_name']} — {reg['national_id']}"
            for reg in reg_pending
        )

        await update.message.reply_text(
            "✅ اطلاعات شما با موفقیت دریافت شد\n\n"
            f"🏕 تور: {trip_title}\n"
            f"👥 تعداد نفرات: {count}\n"
            f"{summary or ''}\n\n"
            "💳 حالا نوع پرداخت را انتخاب کنید:",
            reply_markup=reply_markup
        )

        # از PHONE مستقیماً وارد مرحله انتخاب پرداخت می‌شود.
        return PAY_TYPE_SELECT

    except Exception as e:
        logger.error(
            f"خطا در ثبت‌نام مسافر: {e}",
            exc_info=True
        )

        await update.message.reply_text(
            "❌ خطایی در ذخیره اطلاعات رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

# ===========================================================================
# پرداخت تور برای کاربران ثبت‌نام‌شده قبلی
# ===========================================================================

async def start_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    telegram_user_id = update.effective_user.id

    with Session(engine) as session:

        participants = session.exec(
            select(Participant).where(
                Participant.telegram_user_id == telegram_user_id
            )
        ).all()

        if not participants:
            await update.message.reply_text(
                "❌ شما در هیچ توری ثبت‌نام نکرده‌اید."
            )
            return ConversationHandler.END

        trips_map = {}

        for participant in participants:
            trip = session.get(
                Trip,
                participant.trip_id
            )

            # سفرهای برگزارشده در /pay نمایش داده نشوند
            if trip and trip.status == "active":
                trips_map[
                    f"🏕 {trip.title} (کد {trip.id})"
                ] = {
                    "trip_id": trip.id,
                    "participant_id": participant.id,
                }

        if not trips_map:
            await update.message.reply_text(
                "❌ شما در هیچ توری ثبت‌نام نکرده‌اید."
            )
            return ConversationHandler.END

        context.user_data["payment_trips_map"] = trips_map

        keyboard = [
            [button]
            for button in trips_map.keys()
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        )

        await update.message.reply_text(
            "لطفاً توری که می‌خواهید پرداخت آن را انجام دهید انتخاب کنید:",
            reply_markup=reply_markup,
        )

        return PAY_TRIP_SELECT


# ===========================================================================
# انتخاب تور برای پرداخت
# ===========================================================================

async def select_payment_trip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    selected_option = update.message.text

    trips_map = context.user_data.get(
        "payment_trips_map",
        {}
    )

    if selected_option not in trips_map:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های کیبورد را انتخاب کنید:"
        )
        return PAY_TRIP_SELECT

    payment_info = trips_map[selected_option]
    trip_id = payment_info["trip_id"]
    participant_id = payment_info["participant_id"]

    context.user_data["payment_trip_id"] = trip_id
    context.user_data["payment_participant_id"] = participant_id

    with Session(engine) as session:

        participant = session.get(
            Participant,
            participant_id,
        )

        if not participant:
            await update.message.reply_text(
                "❌ ثبت‌نام شما برای این تور یافت نشد."
            )
            return ConversationHandler.END

        # ---------------------------------------------------------------
        # pending
        # ---------------------------------------------------------------

        if has_pending(
            participant.id,
            trip_id,
            session,
        ):
            await update.message.reply_text(
                "فیش پرداخت شما در حال بررسی است.\n"
                "پس از تعیین وضعیت، می‌توانید پرداخت بعدی را ثبت کنید.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # ---------------------------------------------------------------
        # پیدا کردن تور
        # ---------------------------------------------------------------

        trip = session.get(
            Trip,
            trip_id,
        )

        if not trip:
            await update.message.reply_text(
                "❌ این تور دیگر موجود نیست.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

        if trip.status == "completed":
            await update.message.reply_text(
                "❌ این سفر برگزار شده و امکان پرداخت برای آن وجود ندارد.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

        # ---------------------------------------------------------------
        # مجموع پرداخت‌های تأییدشده
        # ---------------------------------------------------------------

        confirmed_total = get_confirmed_total(
            participant.id,
            trip_id,
            session,
        )

        # ---------------------------------------------------------------
        # بررسی پرداخت کامل
        # ---------------------------------------------------------------

        if is_fully_paid(
            participant.id,
            trip_id,
            trip.price,
            session,
        ):
            await update.message.reply_text(
                "💳 هزینه این تور به‌طور کامل پرداخت شده است.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # ---------------------------------------------------------------
        # محاسبه مبلغ‌ها
        # ---------------------------------------------------------------

        deposit_amount = calculate_deposit(
            trip.price
        )

        full_amount = calculate_full_amount(
            trip.price,
            confirmed_total,
        )

        # ---------------------------------------------------------------
        # ساخت کیبورد انتخاب نوع پرداخت
        # ---------------------------------------------------------------

        if confirmed_total > 0:
            # کاربر قبلاً پرداخت تأییدشدهای دارد (مثلاً بیعانه تأییدشده)
            # ولی کل مبلغ تور را نپرداخته است.
            # فقط گزینه "پرداخت کامل" (مبلغ باقی‌مانده) نمایش داده می‌شود.
            keyboard = [
                [
                    f"💵 پرداخت کامل — "
                    f"{full_amount:,.0f} تومان"
                ],
            ]
        else:
            # هیچ پرداخت تأییدشدهای وجود ندارد؛ هر دو گزینه نمایش داده می‌شود.
            keyboard = [
                [
                    f"💰 پرداخت بیعانه — "
                    f"{deposit_amount:,.0f} تومان"
                ],
                [
                    f"💵 پرداخت کامل — "
                    f"{full_amount:,.0f} تومان"
                ],
            ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        )

        await update.message.reply_text(
            "لطفاً نوع پرداخت را انتخاب کنید:",
            reply_markup=reply_markup,
        )

        return PAY_TYPE_SELECT


# ===========================================================================
# انتخاب نوع پرداخت
# ===========================================================================

async def select_payment_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    selected_option = update.message.text

    if "پرداخت بیعانه" in selected_option:
        payment_type = "deposit"

    elif "پرداخت کامل" in selected_option:
        payment_type = "full"

    else:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های پرداخت را انتخاب کنید:"
        )

        return PAY_TYPE_SELECT

    context.user_data["payment_type"] = payment_type

    trip_id = context.user_data.get(
        "payment_trip_id"
    )

    participant_id = context.user_data.get(
        "payment_participant_id"
    )

    participant_ids = context.user_data.get(
        "payment_participant_ids"
    )

    if participant_ids:
        # مسیر ثبت‌نام (تک‌نفره یا چندنفره): مبلغ هر نفر × تعداد نفرات
        count = len(participant_ids)

        with Session(engine) as session:

            trip = session.get(
                Trip,
                trip_id,
            )

            if not trip:
                await update.message.reply_text(
                    "❌ این تور دیگر موجود نیست.",
                    reply_markup=ReplyKeyboardRemove(),
                )

                return ConversationHandler.END

            if payment_type == "deposit":
                per_person = context.user_data.get(
                    "payment_per_person_deposit"
                )

            else:
                per_person = context.user_data.get(
                    "payment_per_person_full"
                )

        amount = round(per_person * count, 2)

        # مبلغِ «هر نفر» برای ساخت ردیف‌های جداگانه Payment
        context.user_data["payment_unit_amount"] = per_person

        context.user_data[
            "payment_expected_amount"
        ] = amount

    else:
        # مسیر تک‌نفره (پرداخت برای کاربر ثبت‌نام‌شده قبلی)
        with Session(engine) as session:

            trip = session.get(
                Trip,
                trip_id,
            )

            if not trip:
                await update.message.reply_text(
                    "❌ این تور دیگر موجود نیست.",
                    reply_markup=ReplyKeyboardRemove(),
                )

                return ConversationHandler.END

            confirmed_total = get_confirmed_total(
                participant_id,
                trip_id,
                session,
            )

            # ---------------------------------------------------
            # محاسبه مبلغ از Backend
            # ---------------------------------------------------

            if payment_type == "deposit":
                amount = calculate_deposit(
                    trip.price
                )

            else:
                amount = calculate_full_amount(
                    trip.price,
                    confirmed_total,
                )

            context.user_data[
                "payment_expected_amount"
            ] = amount

        await update.message.reply_text(
            f"💳 مبلغ قابل پرداخت:\n\n"
            f"{amount:,.0f} تومان\n\n"
            f"لطفاً مبلغ بالا را به حساب/کارت زیر واریز کنید:\n\n"
            f"{PAYMENT_ACCOUNT_INFO}\n\n"
            "پس از واریز، لطفاً تصویر فیش واریزی را ارسال کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return PAY_RECEIPT

    await update.message.reply_text(
        f"💳 مبلغ قابل پرداخت:\n\n"
        f"{amount:,.0f} تومان\n\n"
        f"لطفاً مبلغ بالا را به حساب/کارت زیر واریز کنید:\n\n"
        f"{PAYMENT_ACCOUNT_INFO}\n\n"
        "پس از واریز، لطفاً تصویر فیش واریزی را ارسال کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PAY_RECEIPT


async def complete_payment_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """ورود مستقیم به تکمیل پرداخت از طریق دکمه‌ی اینلاین (پس از تأیید بیعانه)."""
    query = update.callback_query
    await query.answer()

    try:
        participant_id = int(query.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await query.message.reply_text(
            "❌ لینک پرداخت نامعتبر است."
        )
        return ConversationHandler.END

    telegram_user_id = update.effective_user.id

    with Session(engine) as session:

        participant = session.get(
            Participant,
            participant_id,
        )

        if not participant:
            await query.message.reply_text(
                "❌ ثبت‌نام شما یافت نشد."
            )
            return ConversationHandler.END

        if participant.telegram_user_id != telegram_user_id:
            await query.message.reply_text(
                "❌ این لینک پرداخت متعلق به شما نیست."
            )
            return ConversationHandler.END

        trip = session.get(
            Trip,
            participant.trip_id,
        )

        if not trip:
            await query.message.reply_text(
                "❌ این تور دیگر موجود نیست."
            )
            return ConversationHandler.END

        # ---------------------------------------------------------------
        # بررسی وضعیت پرداخت
        # ---------------------------------------------------------------

        if is_fully_paid(
            participant.id,
            trip.id,
            trip.price,
            session,
        ):
            await query.message.reply_text(
                "💳 هزینه این تور به‌طور کامل پرداخت شده است."
            )
            return ConversationHandler.END

        if has_pending(
            participant.id,
            trip.id,
            session,
        ):
            await query.message.reply_text(
                "فیش پرداخت شما در حال بررسی است. "
                "پس از تعیین وضعیت، می‌توانید پرداخت بعدی را ثبت کنید."
            )
            return ConversationHandler.END

        confirmed_total = get_confirmed_total(
            participant.id,
            trip.id,
            session,
        )

        amount = calculate_full_amount(
            trip.price,
            confirmed_total,
        )

        trip_id = trip.id

    # ---------------------------------------------------------------
    # مقداردهی context و ورود مستقیم به مرحله‌ی فیش (پرداخت کامل)
    # ---------------------------------------------------------------

    context.user_data["payment_trip_id"] = trip_id
    context.user_data["payment_participant_id"] = participant_id
    context.user_data["payment_type"] = "full"
    context.user_data["payment_expected_amount"] = amount

    await query.message.reply_text(
        f"💳 مبلغ قابل پرداخت:\n\n"
        f"{amount:,.0f} تومان\n\n"
        f"لطفاً مبلغ بالا را به حساب/کارت زیر واریز کنید:\n\n"
        f"{PAYMENT_ACCOUNT_INFO}\n\n"
        "پس از واریز، لطفاً تصویر فیش واریزی را ارسال کنید."
    )

    return PAY_RECEIPT


# ===========================================================================
# دریافت فیش پرداخت
# ===========================================================================

async def receive_payment_receipt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # فقط عکس پذیرفته می‌شود
    photo = update.message.photo[-1]

    trip_id = context.user_data.get(
        "payment_trip_id"
    )

    participant_id = context.user_data.get(
        "payment_participant_id"
    )

    payment_type = context.user_data.get(
        "payment_type"
    )

    telegram_user_id = update.effective_user.id

    # -----------------------------------------------------------------------
    # پرداخت چندنفره (ثبت‌نام گروهی)
    # برای هر نفر یک ردیف Payment ساخته می‌شود.
    # مسیر تک‌نفره (فردِ قبلاً ثبت‌نام‌شده) در پایین کاملاً دست‌نخورده می‌ماند.
    # -----------------------------------------------------------------------

    if context.user_data.get("payment_participant_ids"):
        return await _receive_batch_payment_receipt(
            update,
            context,
            photo,
            trip_id,
            payment_type,
            telegram_user_id,
        )

    # -----------------------------------------------------------------------
    # Validationهای Backend
    # -----------------------------------------------------------------------

    with Session(engine) as session:

        participant = session.exec(
            select(Participant).where(
                Participant.telegram_user_id == telegram_user_id,
                Participant.trip_id == trip_id,
            )
        ).first()

        if not participant:
            await update.message.reply_text(
                "❌ ثبت‌نام شما برای این تور یافت نشد.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # -------------------------------------------------------------------
        # بررسی pending
        # -------------------------------------------------------------------

        if has_pending(
            participant.id,
            trip_id,
            session,
        ):
            await update.message.reply_text(
                "فیش پرداخت شما در حال بررسی است.\n"
                "پس از تعیین وضعیت، می‌توانید پرداخت بعدی را ثبت کنید.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # -------------------------------------------------------------------
        # بررسی تور
        # -------------------------------------------------------------------

        trip = session.get(
            Trip,
            trip_id,
        )

        if not trip:
            await update.message.reply_text(
                "❌ این تور دیگر موجود نیست.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # -------------------------------------------------------------------
        # بررسی پرداخت کامل
        # -------------------------------------------------------------------

        if is_fully_paid(
            participant.id,
            trip_id,
            trip.price,
            session,
        ):
            await update.message.reply_text(
                "💳 هزینه این تور به‌طور کامل پرداخت شده است.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # -------------------------------------------------------------------
        # بررسی نوع پرداخت
        # -------------------------------------------------------------------

        if payment_type not in (
            "deposit",
            "full",
        ):
            await update.message.reply_text(
                "❌ نوع پرداخت نامعتبر است.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END

        # -------------------------------------------------------------------
        # محاسبه مبلغ
        # -------------------------------------------------------------------

        confirmed_total = get_confirmed_total(
            participant.id,
            trip_id,
            session,
        )

        if payment_type == "deposit":
            expected_amount = calculate_deposit(
                trip.price
            )

        else:
            expected_amount = calculate_full_amount(
                trip.price,
                confirmed_total,
            )

    # -----------------------------------------------------------------------
    # دانلود فایل تلگرام
    # -----------------------------------------------------------------------

    try:
        file = await photo.get_file()

        file_bytes = await file.download_as_bytearray()

        file_id = photo.file_id
        file_unique_id = photo.file_unique_id

    except Exception as e:
        logger.error(
            f"خطا در دانلود فیش: {e}",
            exc_info=True,
        )

        await update.message.reply_text(
            "❌ خطایی در دریافت فیش رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    # -----------------------------------------------------------------------
    # ذخیره فایل
    # -----------------------------------------------------------------------

    receipt_local_path = None

    try:
        receipt_local_path = save_receipt(
            bytes(file_bytes),
            "jpg",
        )

    except Exception as e:
        logger.error(
            f"خطا در ذخیره فایل فیش: {e}",
            exc_info=True,
        )

        await update.message.reply_text(
            "❌ خطایی در ذخیره فیش رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    # -----------------------------------------------------------------------
    # ساخت Payment
    # -----------------------------------------------------------------------

    try:
        with Session(engine) as session:

            new_payment = Payment(
                participant_id=participant_id,
                trip_id=trip_id,
                telegram_user_id=telegram_user_id,
                payment_type=payment_type,
                expected_amount=expected_amount,
                receipt_file_id=file_id,
                receipt_file_unique_id=file_unique_id,
                receipt_local_path=receipt_local_path,
                status="pending_review",
                created_at=datetime.now().isoformat(),
            )

            session.add(new_payment)
            session.commit()

    except Exception as e:
        logger.error(
            f"خطا در ساخت Payment: {e}",
            exc_info=True,
        )

        # حذف فایل orphan
        if receipt_local_path:
            try:
                if os.path.exists(receipt_local_path):
                    os.remove(receipt_local_path)

            except Exception as cleanup_e:
                logger.error(
                    f"خطا در حذف فایل orphan: {cleanup_e}"
                )

        await update.message.reply_text(
            "❌ خطایی در ثبت پرداخت رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    # -----------------------------------------------------------------------
    # موفقیت
    # -----------------------------------------------------------------------

    await update.message.reply_text(
        "✅ فیش شما دریافت شد و در انتظار بررسی است.",
        reply_markup=ReplyKeyboardRemove(),
    )

    # پاک کردن اطلاعات موقت پرداخت
    for key in [
        "payment_trips_map",
        "payment_trip_id",
        "payment_participant_id",
        "payment_type",
        "payment_expected_amount",
    ]:
        context.user_data.pop(
            key,
            None,
        )

    return ConversationHandler.END


# ===========================================================================
# دریافت فیش پرداخت — حالت چندنفره
# ===========================================================================

async def _receive_batch_payment_receipt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo,
    trip_id,
    payment_type,
    telegram_user_id,
):
    """برای هر نفر از ثبت‌نام گروهی یک ردیف Payment (pending_review) می‌سازد.

    از همین مسیر، ثبت‌نام تک‌نفره نیز عبور می‌کند (لیستِ یک‌عضوی)؛ در نتیجه
    رفتار تک‌نفره هم دقیقاً حفظ می‌شود و مسیرِ «پرداخت کاربر قبلی» دست نمی‌خورد.
    """
    participant_ids = context.user_data.get("payment_participant_ids", [])
    expected_amount = context.user_data.get("payment_unit_amount")

    if not participant_ids or expected_amount is None:
        await update.message.reply_text(
            "❌ اطلاعات پرداخت ناقص است. لطفاً دوباره تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    # بررسی وجود تور
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)

        if not trip:
            await update.message.reply_text(
                "❌ این تور دیگر موجود نیست.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

    # -------------------------------------------------------------------
    # دانلود فایل تلگرام
    # -------------------------------------------------------------------

    try:
        file = await photo.get_file()

        file_bytes = await file.download_as_bytearray()

        file_id = photo.file_id
        file_unique_id = photo.file_unique_id

    except Exception as e:
        logger.error(
            f"خطا در دانلود فیش: {e}",
            exc_info=True,
        )

        await update.message.reply_text(
            "❌ خطایی در دریافت فیش رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    # -----------------------------------------------------------------------
    # ذخیره فایل
    # -----------------------------------------------------------------------

    receipt_local_path = None

    try:
        receipt_local_path = save_receipt(
            bytes(file_bytes),
            "jpg",
        )

    except Exception as e:
        logger.error(
            f"خطا در ذخیره فایل فیش: {e}",
            exc_info=True,
        )

        await update.message.reply_text(
            "❌ خطایی در ذخیره فیش رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    # -----------------------------------------------------------------------
    # ساخت یک Payment برای هر نفر
    # -----------------------------------------------------------------------

    try:
        with Session(engine) as session:

            for pid in participant_ids:
                new_payment = Payment(
                    participant_id=pid,
                    trip_id=trip_id,
                    telegram_user_id=telegram_user_id,
                    payment_type=payment_type,
                    expected_amount=expected_amount,
                    receipt_file_id=file_id,
                    receipt_file_unique_id=file_unique_id,
                    receipt_local_path=receipt_local_path,
                    status="pending_review",
                    created_at=datetime.now().isoformat(),
                )

                session.add(new_payment)

            session.commit()

    except Exception as e:
        logger.error(
            f"خطا در ساخت Payment: {e}",
            exc_info=True,
        )

        # حذف فایل orphan
        if receipt_local_path:
            try:
                if os.path.exists(receipt_local_path):
                    os.remove(receipt_local_path)

            except Exception as cleanup_e:
                logger.error(
                    f"خطا در حذف فایل orphan: {cleanup_e}"
                )

        await update.message.reply_text(
            "❌ خطایی در ثبت پرداخت رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    # -----------------------------------------------------------------------
    # موفقیت
    # -----------------------------------------------------------------------

    count = len(participant_ids)

    await update.message.reply_text(
        f"✅ فیش شما دریافت شد و در انتظار بررسی است.\n"
        f"({count} نفر از پرداخت شما تحت بررسی قرار گرفتند.)",
        reply_markup=ReplyKeyboardRemove(),
    )

    # پاک کردن اطلاعات موقت پرداخت و ثبت‌نام چندنفره
    for key in [
        "payment_trips_map",
        "payment_trip_id",
        "payment_participant_id",
        "payment_participant_ids",
        "payment_type",
        "payment_expected_amount",
        "payment_unit_amount",
        "payment_per_person_deposit",
        "payment_per_person_full",
        "reg_count",
        "reg_pending",
        "reg_current",
        "reg_index",
    ]:
        context.user_data.pop(
            key,
            None,
        )

    return ConversationHandler.END


# ===========================================================================
# لغو پرداخت
# ===========================================================================

async def cancel_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "فرآیند پرداخت لغو شد.",
        reply_markup=ReplyKeyboardRemove(),
    )

    for key in [
        "payment_trips_map",
        "payment_trip_id",
        "payment_participant_id",
        "payment_type",
        "payment_expected_amount",
    ]:
        context.user_data.pop(
            key,
            None,
        )

    return ConversationHandler.END


# ===========================================================================
# ساخت Application ربات
# ===========================================================================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "فرآیند ثبت‌نام لغو شد.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "فرآیند پرداخت لغو شد.",
        reply_markup=ReplyKeyboardRemove()
    )

    for key in [
        "payment_trips_map",
        "payment_trip_id",
        "payment_participant_id",
        "payment_type",
        "payment_expected_amount",
    ]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

def build_bot_app():

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "متغیر محیطی BOT_TOKEN تنظیم نشده است. "
            "توکن ربات را در تنظیمات محیطی سرور قرار دهید "
            "(هرگز در کد ننویسید)."
        )

    app = ApplicationBuilder().token(token).build()

    # -----------------------------------------------------------------------
    # ثبت‌نام + پرداخت بلافاصله بعد از ثبت‌نام
    #
    # نکته مهم:
    # PAY_TYPE_SELECT و PAY_RECEIPT عمداً در همین ConversationHandler
    # قرار گرفته‌اند.
    # -----------------------------------------------------------------------

    registration_conv_handler = ConversationHandler(

        entry_points=[
            CommandHandler(
                "start",
                start_registration,
            ),
            CommandHandler(
                "register",
                start_registration,
            ),
        ],

        states={

            TRIP_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_trip,
                )
            ],

            COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_count,
                )
            ],

            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name,
                )
            ],

            NATIONAL_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_national_id,
                )
            ],

            PHONE: [
                MessageHandler(
                    filters.CONTACT,
                    get_phone_and_save,
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_phone_and_save,
                ),
            ],

            # ---------------------------------------------------------------
            # این دو state مشکل اصلی قبلی بودند
            # ---------------------------------------------------------------

            PAY_TYPE_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_payment_type,
                )
            ],

            PAY_RECEIPT: [
                MessageHandler(
                    filters.PHOTO,
                    receive_payment_receipt,
                )
            ],
        },

        fallbacks=[
            CommandHandler(
                "cancel",
                cancel,
            ),
            CommandHandler(
                "cancel_payment",
                cancel_payment,
            ),
        ],

        allow_reentry=True,
    )

    # -----------------------------------------------------------------------
    # پرداخت برای کاربری که قبلاً ثبت‌نام کرده
    # -----------------------------------------------------------------------

    payment_conv_handler = ConversationHandler(

        entry_points=[
            CommandHandler(
                "pay",
                start_payment,
            ),
            CallbackQueryHandler(
                complete_payment_callback,
                pattern=r"^complete_payment:\d+$",
            ),
        ],

        states={

            PAY_TRIP_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_payment_trip,
                )
            ],

            PAY_TYPE_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_payment_type,
                )
            ],

            PAY_RECEIPT: [
                MessageHandler(
                    filters.PHOTO,
                    receive_payment_receipt,
                )
            ],
        },

        fallbacks=[
            CommandHandler(
                "cancel",
                cancel_payment,
            )
        ],
    )

    # -----------------------------------------------------------------------
    # ترتیب مهم است
    # -----------------------------------------------------------------------

    app.add_handler(
        registration_conv_handler
    )

    app.add_handler(
        payment_conv_handler
    )

    return app


# ===========================================================================
# اجرای ربات همزمان با FastAPI
# ===========================================================================

async def start_bot():

    telegram_app = build_bot_app()

    await telegram_app.initialize()

    await telegram_app.start()

    await telegram_app.updater.start_polling()

    return telegram_app
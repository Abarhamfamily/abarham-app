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

TRIP_SELECT, NAME, NATIONAL_ID, PHONE = range(4)

PAY_TRIP_SELECT, PAY_TYPE_SELECT, PAY_RECEIPT = range(4, 7)


# ---------------------------------------------------------------------------
# اطلاعات حساب/کارت مقصد
# ---------------------------------------------------------------------------

PAYMENT_ACCOUNT_INFO = (
    "شماره کارت: 0000-0000-0000-0000\n"
    "به نام: [نام گیرنده]\n"
    "بانک: [نام بانک]"
)


# ===========================================================================
# ثبت‌نام
# ===========================================================================

async def start_registration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    with Session(engine) as session:
        trips = session.exec(select(Trip)).all()

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
        "لطفاً نام و نام خانوادگی خود را وارد کنید:",
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

    context.user_data["full_name"] = full_name

    await update.message.reply_text(
        "لطفاً کد ملی خود را وارد کنید:"
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

    # جلوگیری از ثبت‌نام تکراری
    with Session(engine) as session:
        existing = session.exec(
            select(Participant).where(
                Participant.national_id == national_id,
                Participant.trip_id == trip_id,
            )
        ).first()

    if existing:
        await update.message.reply_text(
            "❌ شما قبلاً با این کد ملی برای این تور ثبت‌نام کرده‌اید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    context.user_data["national_id"] = national_id

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
        "لطفاً شماره تماس خود را وارد کنید یا از دکمه زیر جهت ارسال سریع استفاده کنید:",
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

    context.user_data["phone_number"] = phone_number

    trip_id = context.user_data.get("trip_id")

    try:
        # ---------------------------------------------------------
        # بررسی و ذخیره اطلاعات در دیتابیس
        # ---------------------------------------------------------
        with Session(engine) as session:
            trip = session.get(Trip, trip_id)

            if not trip:
                await update.message.reply_text(
                    "❌ این تور دیگر موجود نیست.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END

            # مهم:
            # اطلاعات موردنیاز تور را قبل از بسته‌شدن Session
            # در متغیرهای معمولی ذخیره می‌کنیم.
            trip_price = trip.price
            trip_title = trip.title

            # -----------------------------------------------------
            # بررسی ظرفیت تور
            # -----------------------------------------------------
            if trip.capacity:
                current_count = len(
                    session.exec(
                        select(Participant).where(
                            Participant.trip_id == trip_id
                        )
                    ).all()
                )

                if current_count >= trip.capacity:
                    await update.message.reply_text(
                        "❌ ظرفیت این تور تکمیل شده است.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return ConversationHandler.END

            # -----------------------------------------------------
            # جلوگیری از ثبت‌نام تکراری
            # -----------------------------------------------------
            existing = session.exec(
                select(Participant).where(
                    Participant.national_id == context.user_data["national_id"],
                    Participant.trip_id == trip_id
                )
            ).first()

            if existing:
                await update.message.reply_text(
                    "❌ شما قبلاً برای این تور ثبت‌نام کرده‌اید.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END

            # -----------------------------------------------------
            # ساخت شرکت‌کننده
            # -----------------------------------------------------
            new_participant = Participant(
                full_name=context.user_data["full_name"],
                national_id=context.user_data["national_id"],
                phone_number=context.user_data["phone_number"],
                trip_id=trip_id,
                telegram_user_id=update.effective_user.id
            )

            session.add(new_participant)
            session.commit()
            session.refresh(new_participant)

            # ذخیره شناسه شرکت‌کننده
            participant_id = new_participant.id

        # ---------------------------------------------------------
        # از اینجا Session بسته شده است.
        # بنابراین فقط از متغیرهای معمولی استفاده می‌کنیم.
        # ---------------------------------------------------------

        context.user_data["payment_trip_id"] = trip_id
        context.user_data["payment_participant_id"] = participant_id

        # ---------------------------------------------------------
        # محاسبه مبلغ پرداخت
        # ---------------------------------------------------------

        deposit_amount = calculate_deposit(trip_price)

        # در این مرحله هنوز هیچ پرداخت تأییدشده‌ای وجود ندارد.
        full_amount = calculate_full_amount(
            trip_price,
            0
        )

        # ---------------------------------------------------------
        # ساخت کیبورد انتخاب نوع پرداخت
        # ---------------------------------------------------------

        keyboard = [
            [f"💰 پرداخت بیعانه — {deposit_amount:,.0f} تومان"],
            [f"💵 پرداخت کامل — {full_amount:,.0f} تومان"],
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )

        # ---------------------------------------------------------
        # اعلام ثبت‌نام و ورود مستقیم به مرحله پرداخت
        # ---------------------------------------------------------

        await update.message.reply_text(
            "✅ اطلاعات شما با موفقیت دریافت شد\n\n"
            f"🏕 تور: {trip_title}\n"
            f"👤 نام: {context.user_data['full_name']}\n"
            f"🆔 کد ملی: {context.user_data['national_id']}\n"
            f"📞 شماره تماس: {context.user_data['phone_number']}\n\n"
            "💳 حالا نوع پرداخت را انتخاب کنید:",
            reply_markup=reply_markup
        )

        # بسیار مهم:
        # Conversation اصلی از PHONE مستقیماً
        # وارد مرحله انتخاب پرداخت می‌شود.
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

            if trip:
                trips_map[
                    f"🏕 {trip.title} (کد {trip.id})"
                ] = trip.id

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

    trip_id = trips_map[selected_option]
    telegram_user_id = update.effective_user.id

    with Session(engine) as session:

        participant = session.exec(
            select(Participant).where(
                Participant.telegram_user_id == telegram_user_id,
                Participant.trip_id == trip_id,
            )
        ).first()

        if not participant:
            await update.message.reply_text(
                "❌ ثبت‌نام شما برای این تور یافت نشد."
            )
            return ConversationHandler.END

        context.user_data["payment_trip_id"] = trip_id
        context.user_data["payment_participant_id"] = participant.id

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

        # ---------------------------------------------------------------
        # محاسبه مبلغ از Backend
        # ---------------------------------------------------------------

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
            )
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
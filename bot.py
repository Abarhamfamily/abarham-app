import logging
import os
import uuid

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from sqlmodel import Session, select

from models import Participant, Payment, Trip, engine
from payment import (
    calculate_deposit,
    get_confirmed_total,
    has_pending,
    is_fully_paid,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conversation States
# ---------------------------------------------------------------------------
(
    TRIP_SELECT,
    NUM_PARTICIPANTS,
    NAME,
    NATIONAL_ID,
    PHONE,
    VEHICLE_CHOICE,
    AVAILABLE_SEATS,
    PAY_TYPE_SELECT,
    PAY_RECEIPT,
) = range(9)

PAY_TRIP_SELECT, PAY_PARTICIPANT_SELECT, PAY_RECEIPT_ONLY = range(9, 12)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def get_active_trips():
    with Session(engine) as session:
        return session.exec(
            select(Trip).where(Trip.status == "active")
        ).all()

# ---------------------------------------------------------------------------
# Bot Commands & Handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"سلام {user.first_name} عزیز! 👋\n"
        "به سیستم ثبت‌نام و مدیریت تورهای **ابرهام** خوش آمدید.\n\n"
        "جهت ثبت‌نام در تورها از دستور /register و جهت تکمیل پرداخت از /pay استفاده کنید."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ عملیات لغو شد. می‌توانید مجدداً از دستورات ربات استفاده کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# ---------------------------------------------------------------------------
# Registration Flow (Group & Single Integrated)
# ---------------------------------------------------------------------------
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    trips = get_active_trips()
    if not trips:
        await update.message.reply_text("در حال حاضر هیچ تور فعالی برای ثبت‌نام وجود ندارد.")
        return ConversationHandler.END

    keyboard = []
    for trip in trips:
        keyboard.append([InlineKeyboardButton(f"🌲 {trip.title} ({trip.price:,.0f} تومان)", callback_data=f"trip:{trip.id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً تور مورد نظر خود را برای ثبت‌نام انتخاب کنید:", reply_markup=reply_markup)
    return TRIP_SELECT

async def trip_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    trip_id = int(query.data.split(":")[1])
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            await query.edit_message_text("تور مورد نظر یافت نشد.")
            return ConversationHandler.END
        
        context.user_data["trip_id"] = trip.id
        context.user_data["trip_price"] = trip.price
        context.user_data["transportation_type"] = trip.transportation_type
        context.user_data["participants"] = []
        context.user_data["group_id"] = str(uuid.uuid4())

    keyboard = [
        [InlineKeyboardButton("۱ نفر (تک‌نفره)", callback_data="num:1")],
        [InlineKeyboardButton("۲ نفر", callback_data="num:2"), InlineKeyboardButton("۳ نفر", callback_data="num:3")],
        [InlineKeyboardButton("۴ نفر", callback_data="num:4"), InlineKeyboardButton("۵ نفر", callback_data="num:5")],
    ]
    await query.edit_message_text("تعداد افراد جهت ثبت‌نام را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return NUM_PARTICIPANTS

async def num_participants_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    count = int(query.data.split(":")[1])
    context.user_data["total_count"] = count
    context.user_data["current_index"] = 1

    await query.edit_message_text(f"ثبت‌نام برای {count} نفر.\n\nلطفاً **نام و نام خانوادگی** نفر اول را وارد کنید:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text("نام وارد شده بسیار کوتاه است. لطفاً نام و نام خانوادگی کامل را وارد کنید:")
        return NAME

    current_p = {"full_name": name}
    context.user_data["temp_participant"] = current_p
    
    idx = context.user_data["current_index"]
    await update.message.reply_text(f"لطفاً **کد ملی** نفر {idx} را وارد کنید:")
    return NATIONAL_ID

async def get_national_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    national_id = update.message.text.strip()
    if not national_id.isdigit() or len(national_id) != 10:
        await update.message.reply_text("کد ملی باید یک عدد ۱۰ رقمی باشد. لطفاً مجدداً وارد کنید:")
        return NATIONAL_ID

    context.user_data["temp_participant"]["national_id"] = national_id
    idx = context.user_data["current_index"]
    
    await update.message.reply_text(f"لطفاً **شماره همراه** نفر {idx} را وارد کنید:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not phone.startswith("09") or len(phone) != 11:
        await update.message.reply_text("شماره همراه نامعتبر است. نمونه صحیح: 09123456789")
        return PHONE

    temp_p = context.user_data.pop("temp_participant")
    temp_p["phone_number"] = phone
    
    context.user_data["participants"].append(temp_p)

    current_idx = context.user_data["current_index"]
    total_count = context.user_data["total_count"]

    if current_idx < total_count:
        context.user_data["current_index"] += 1
        next_idx = context.user_data["current_index"]
        await update.message.reply_text(f"اطلاعات نفر {current_idx} ثبت شد.\n\nحال لطفاً **نام و نام خانوادگی** نفر {next_idx} را وارد کنید:")
        return NAME

    if context.user_data["transportation_type"] == "personal_vehicle":
        reply_keyboard = [["🚗 ماشین شخصی خودم"], ["🚙 ماشین یکی از اعضای ابرهام"]]
        await update.message.reply_text(
            "وضعیت خودروی خود را برای سفر مشخص کنید:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return VEHICLE_CHOICE
    else:
        return await proceed_to_payment_selection(update, context)

async def get_vehicle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if "شخصی" in choice:
        context.user_data["vehicle_choice"] = "personal"
        await update.message.reply_text("چند صندلی خالی برای همراهی سایر اعضا دارید؟ (اگر صندلی خالی ندارید 0 بفرستید)", reply_markup=ReplyKeyboardRemove())
        return AVAILABLE_SEATS
    else:
        context.user_data["vehicle_choice"] = "abraham_member"
        context.user_data["available_seats"] = 0
        return await proceed_to_payment_selection(update, context)

async def get_available_seats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("لطفاً یک عدد معتبر وارد کنید:")
        return AVAILABLE_SEATS

    context.user_data["available_seats"] = int(text)
    return await proceed_to_payment_selection(update, context)

async def proceed_to_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trip_id = context.user_data["trip_id"]
    trip_price = context.user_data["trip_price"]
    participants_data = context.user_data["participants"]
    group_id = context.user_data["group_id"]
    
    saved_participants = []
    
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        
        for idx, p_data in enumerate(participants_data):
            p = Participant(
                full_name=p_data["full_name"],
                national_id=p_data["national_id"],
                phone_number=p_data["phone_number"],
                trip_id=trip_id,
                telegram_user_id=update.effective_user.id if idx == 0 else None,
                vehicle_choice=context.user_data.get("vehicle_choice"),
                available_seats=context.user_data.get("available_seats", 0),
                group_id=group_id,
            )
            session.add(p)
            session.commit()
            session.refresh(p)
            saved_participants.append(p)

    context.user_data["main_participant_id"] = saved_participants[0].id
    
    total_group_price = trip_price * len(saved_participants)
    deposit_amount = calculate_deposit(total_group_price)

    keyboard = [
        [InlineKeyboardButton(f"💳 پرداخت بیعانه ({deposit_amount:,.0f} تومان)", callback_data="paytype:deposit")],
        [InlineKeyboardButton(f"💰 پرداخت کامل ({total_group_price:,.0f} تومان)", callback_data="paytype:full")],
    ]
    
    msg = (
        f"✅ اطلاعات {len(saved_participants)} نفر با موفقیت ثبت شد.\n\n"
        f"مبلغ کل تور برای این گروه: {total_group_price:,.0f} تومان\n"
        "لطفاً نوع پرداخت خود را انتخاب کنید:"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        
    return PAY_TYPE_SELECT

async def pay_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pay_type = query.data.split(":")[1]
    context.user_data["pay_type"] = pay_type
    
    trip_price = context.user_data["trip_price"]
    count = len(context.user_data["participants"])
    total_price = trip_price * count

    expected_amount = calculate_deposit(total_price) if pay_type == "deposit" else total_price
    context.user_data["expected_amount"] = expected_amount

    msg = (
        f"مبلغ قابل پرداخت: **{expected_amount:,.0f} تومان**\n\n"
        "لطفاً مبلغ فوق را واریز کرده و تصویر فیش واریزی را ارسال کنید."
    )
    await query.edit_message_text(msg, parse_mode="Markdown")
    return PAY_RECEIPT

async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً تصویر فیش را به صورت عکس (Photo) ارسال کنید:")
        return PAY_RECEIPT

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    os.makedirs("receipts", exist_ok=True)
    local_path = f"receipts/{photo.file_unique_id}.jpg"
    await file.download_to_drive(local_path)

    main_p_id = context.user_data["main_participant_id"]
    trip_id = context.user_data["trip_id"]

    with Session(engine) as session:
        payment = Payment(
            participant_id=main_p_id,
            trip_id=trip_id,
            telegram_user_id=update.effective_user.id,
            payment_type=context.user_data["pay_type"],
            expected_amount=context.user_data["expected_amount"],
            receipt_file_id=photo.file_id,
            receipt_file_unique_id=photo.file_unique_id,
            receipt_local_path=local_path,
            status="pending_review",
        )
        session.add(payment)
        session.commit()

    await update.message.reply_text(
        "🧾 فیش شما با موفقیت ثبت شد و در انتظار بررسی توسط مدیریت است.\n"
        "نتیجه پس از بررسی از همین طریق به شما اطلاع داده خواهد شد."
    )
    context.user_data.clear()
    return ConversationHandler.END

# ---------------------------------------------------------------------------
# Payment Flow (/pay)
# ---------------------------------------------------------------------------
async def start_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    trips = get_active_trips()
    if not trips:
        await update.message.reply_text("در حال حاضر هیچ تور فعالی یافت نشد.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(f"🌲 {t.title}", callback_data=f"paytrip:{t.id}")] for t in trips]
    await update.message.reply_text("لطفاً توری که در آن ثبت‌نام کرده‌اید را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PAY_TRIP_SELECT

async def pay_trip_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    trip_id = int(query.data.split(":")[1])
    tg_user_id = update.effective_user.id

    with Session(engine) as session:
        # پیدا کردن ثبت‌نامی که این کاربر نماینده/ثبت‌کننده آن بوده است
        participants = session.exec(
            select(Participant).where(
                Participant.trip_id == trip_id,
                Participant.telegram_user_id == tg_user_id
            )
        ).all()

        if not participants:
            await query.edit_message_text("هیچ ثبت‌نامی به نام شما برای این تور یافت نشد.")
            return ConversationHandler.END

        # اگر چند گروه داشت انتخاب کند، در غیر این صورت همان اولی
        p = participants[0]
        
        # محاسبه کل بدهی گروه بر اساس group_id
        group_members = session.exec(
            select(Participant).where(Participant.group_id == p.group_id)
        ).all() if p.group_id else [p]
        
        trip = session.get(Trip, trip_id)
        total_group_price = trip.price * len(group_members)
        
        confirmed_paid = get_confirmed_total(p.id)
        remaining = total_group_price - confirmed_paid

        if remaining <= 0:
            await query.edit_message_text("✅ تمام هزینه‌های تور برای شما و گروهتان کاملاً تسویه شده است.")
            return ConversationHandler.END

        if has_pending(p.id):
            await query.edit_message_text("⏳ شما یک فیش در انتظار بررسی دارید. لطفاً تا زمان تعیین تکلیف آن صبر کنید.")
            return ConversationHandler.END

        context.user_data["main_participant_id"] = p.id
        context.user_data["trip_id"] = trip_id
        context.user_data["pay_type"] = "remaining"
        context.user_data["expected_amount"] = remaining

        await query.edit_message_text(
            f"مبلغ باقی‌مانده جهت تسویه گروه ({len(group_members)} نفر): **{remaining:,.0f} تومان**\n\n"
            "لطفاً مبلغ فوق را واریز کرده و تصویر فیش را ارسال کنید:",
            parse_mode="Markdown"
        )
        return PAY_RECEIPT_ONLY

# ---------------------------------------------------------------------------
# Bot Application Builder
# ---------------------------------------------------------------------------
def build_bot_app() -> Application:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")

    app = Application.builder().token(bot_token).build()

    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("register", start_registration)],
        states={
            TRIP_SELECT: [CallbackQueryHandler(trip_selected, pattern="^trip:")],
            NUM_PARTICIPANTS: [CallbackQueryHandler(num_participants_selected, pattern="^num:")],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            NATIONAL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_national_id)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            VEHICLE_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vehicle_choice)],
            AVAILABLE_SEATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_available_seats)],
            PAY_TYPE_SELECT: [CallbackQueryHandler(pay_type_selected, pattern="^paytype:")],
            PAY_RECEIPT: [MessageHandler(filters.PHOTO, receipt_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    pay_handler = ConversationHandler(
        entry_points=[CommandHandler("pay", start_pay)],
        states={
            PAY_TRIP_SELECT: [CallbackQueryHandler(pay_trip_selected, pattern="^paytrip:")],
            PAY_RECEIPT_ONLY: [MessageHandler(filters.PHOTO, receipt_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(reg_handler)
    app.add_handler(pay_handler)

    return app

async def start_bot():
    telegram_app = build_bot_app()
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    return telegram_app
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
        f"Ø³Ù„Ø§Ù… {user.first_name} Ø¹Ø²ÛŒØ²! ðŸ‘‹\n"
        "Ø¨Ù‡ Ø³ÛŒØ³ØªÙ… Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ùˆ Ù…Ø¯ÛŒØ±ÛŒØª ØªÙˆØ±Ù‡Ø§ÛŒ **Ø§Ø¨Ø±Ù‡Ø§Ù…** Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒØ¯.\n\n"
        "Ø¬Ù‡Øª Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ø¯Ø± ØªÙˆØ±Ù‡Ø§ Ø§Ø² Ø¯Ø³ØªÙˆØ± /register Ùˆ Ø¬Ù‡Øª ØªÚ©Ù…ÛŒÙ„ Ù¾Ø±Ø¯Ø§Ø®Øª Ø§Ø² /pay Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "âŒ Ø¹Ù…Ù„ÛŒØ§Øª Ù„ØºÙˆ Ø´Ø¯. Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ù…Ø¬Ø¯Ø¯Ø§Ù‹ Ø§Ø² Ø¯Ø³ØªÙˆØ±Ø§Øª Ø±Ø¨Ø§Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.",
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
        await update.message.reply_text("Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø± Ù‡ÛŒÚ† ØªÙˆØ± ÙØ¹Ø§Ù„ÛŒ Ø¨Ø±Ø§ÛŒ Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø±Ø¯.")
        return ConversationHandler.END

    keyboard = []
    for trip in trips:
        keyboard.append([InlineKeyboardButton(f"ðŸŒ² {trip.title} ({trip.price:,.0f} ØªÙˆÙ…Ø§Ù†)", callback_data=f"trip:{trip.id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ù„Ø·ÙØ§Ù‹ ØªÙˆØ± Ù…ÙˆØ±Ø¯ Ù†Ø¸Ø± Ø®ÙˆØ¯ Ø±Ø§ Ø¨Ø±Ø§ÛŒ Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:", reply_markup=reply_markup)
    return TRIP_SELECT

async def trip_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    trip_id = int(query.data.split(":")[1])
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            await query.edit_message_text("ØªÙˆØ± Ù…ÙˆØ±Ø¯ Ù†Ø¸Ø± ÛŒØ§ÙØª Ù†Ø´Ø¯.")
            return ConversationHandler.END
        
        context.user_data["trip_id"] = trip.id
        context.user_data["trip_price"] = trip.price
        context.user_data["transportation_type"] = trip.transportation_type
        context.user_data["participants"] = []
        context.user_data["group_id"] = str(uuid.uuid4())

    keyboard = [
        [InlineKeyboardButton("Û± Ù†ÙØ± (ØªÚ©â€ŒÙ†ÙØ±Ù‡)", callback_data="num:1")],
        [InlineKeyboardButton("Û² Ù†ÙØ±", callback_data="num:2"), InlineKeyboardButton("Û³ Ù†ÙØ±", callback_data="num:3")],
        [InlineKeyboardButton("Û´ Ù†ÙØ±", callback_data="num:4"), InlineKeyboardButton("Ûµ Ù†ÙØ±", callback_data="num:5")],
    ]
    await query.edit_message_text("ØªØ¹Ø¯Ø§Ø¯ Ø§ÙØ±Ø§Ø¯ Ø¬Ù‡Øª Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:", reply_markup=InlineKeyboardMarkup(keyboard))
    return NUM_PARTICIPANTS

async def num_participants_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    count = int(query.data.split(":")[1])
    context.user_data["total_count"] = count
    context.user_data["current_index"] = 1

    await query.edit_message_text(f"Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ø¨Ø±Ø§ÛŒ {count} Ù†ÙØ±.\n\nÙ„Ø·ÙØ§Ù‹ **Ù†Ø§Ù… Ùˆ Ù†Ø§Ù… Ø®Ø§Ù†ÙˆØ§Ø¯Ú¯ÛŒ** Ù†ÙØ± Ø§ÙˆÙ„ Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text("Ù†Ø§Ù… ÙˆØ§Ø±Ø¯ Ø´Ø¯Ù‡ Ø¨Ø³ÛŒØ§Ø± Ú©ÙˆØªØ§Ù‡ Ø§Ø³Øª. Ù„Ø·ÙØ§Ù‹ Ù†Ø§Ù… Ùˆ Ù†Ø§Ù… Ø®Ø§Ù†ÙˆØ§Ø¯Ú¯ÛŒ Ú©Ø§Ù…Ù„ Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
        return NAME

    current_p = {"full_name": name}
    context.user_data["temp_participant"] = current_p
    
    idx = context.user_data["current_index"]
    await update.message.reply_text(f"Ù„Ø·ÙØ§Ù‹ **Ú©Ø¯ Ù…Ù„ÛŒ** Ù†ÙØ± {idx} Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
    return NATIONAL_ID

async def get_national_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    national_id = update.message.text.strip()
    if not national_id.isdigit() or len(national_id) != 10:
        await update.message.reply_text("Ú©Ø¯ Ù…Ù„ÛŒ Ø¨Ø§ÛŒØ¯ ÛŒÚ© Ø¹Ø¯Ø¯ Û±Û° Ø±Ù‚Ù…ÛŒ Ø¨Ø§Ø´Ø¯. Ù„Ø·ÙØ§Ù‹ Ù…Ø¬Ø¯Ø¯Ø§Ù‹ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
        return NATIONAL_ID

    context.user_data["temp_participant"]["national_id"] = national_id
    idx = context.user_data["current_index"]
    
    await update.message.reply_text(f"Ù„Ø·ÙØ§Ù‹ **Ø´Ù…Ø§Ø±Ù‡ Ù‡Ù…Ø±Ø§Ù‡** Ù†ÙØ± {idx} Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not phone.startswith("09") or len(phone) != 11:
        await update.message.reply_text("Ø´Ù…Ø§Ø±Ù‡ Ù‡Ù…Ø±Ø§Ù‡ Ù†Ø§Ù…Ø¹ØªØ¨Ø± Ø§Ø³Øª. Ù†Ù…ÙˆÙ†Ù‡ ØµØ­ÛŒØ­: 09123456789")
        return PHONE

    temp_p = context.user_data.pop("temp_participant")
    temp_p["phone_number"] = phone
    
    context.user_data["participants"].append(temp_p)

    current_idx = context.user_data["current_index"]
    total_count = context.user_data["total_count"]

    if current_idx < total_count:
        context.user_data["current_index"] += 1
        next_idx = context.user_data["current_index"]
        await update.message.reply_text(f"Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ù†ÙØ± {current_idx} Ø«Ø¨Øª Ø´Ø¯.\n\nØ­Ø§Ù„ Ù„Ø·ÙØ§Ù‹ **Ù†Ø§Ù… Ùˆ Ù†Ø§Ù… Ø®Ø§Ù†ÙˆØ§Ø¯Ú¯ÛŒ** Ù†ÙØ± {next_idx} Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
        return NAME

    if context.user_data["transportation_type"] == "personal_vehicle":
        reply_keyboard = [["ðŸš— Ù…Ø§Ø´ÛŒÙ† Ø´Ø®ØµÛŒ Ø®ÙˆØ¯Ù…"], ["ðŸš™ Ù…Ø§Ø´ÛŒÙ† ÛŒÚ©ÛŒ Ø§Ø² Ø§Ø¹Ø¶Ø§ÛŒ Ø§Ø¨Ø±Ù‡Ø§Ù…"]]
        await update.message.reply_text(
            "ÙˆØ¶Ø¹ÛŒØª Ø®ÙˆØ¯Ø±ÙˆÛŒ Ø®ÙˆØ¯ Ø±Ø§ Ø¨Ø±Ø§ÛŒ Ø³ÙØ± Ù…Ø´Ø®Øµ Ú©Ù†ÛŒØ¯:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return VEHICLE_CHOICE
    else:
        return await proceed_to_payment_selection(update, context)

async def get_vehicle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if "Ø´Ø®ØµÛŒ" in choice:
        context.user_data["vehicle_choice"] = "personal"
        await update.message.reply_text("Ú†Ù†Ø¯ ØµÙ†Ø¯Ù„ÛŒ Ø®Ø§Ù„ÛŒ Ø¨Ø±Ø§ÛŒ Ù‡Ù…Ø±Ø§Ù‡ÛŒ Ø³Ø§ÛŒØ± Ø§Ø¹Ø¶Ø§ Ø¯Ø§Ø±ÛŒØ¯ØŸ (Ø§Ú¯Ø± ØµÙ†Ø¯Ù„ÛŒ Ø®Ø§Ù„ÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯ 0 Ø¨ÙØ±Ø³ØªÛŒØ¯)", reply_markup=ReplyKeyboardRemove())
        return AVAILABLE_SEATS
    else:
        context.user_data["vehicle_choice"] = "abraham_member"
        context.user_data["available_seats"] = 0
        return await proceed_to_payment_selection(update, context)

async def get_available_seats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Ù„Ø·ÙØ§Ù‹ ÛŒÚ© Ø¹Ø¯Ø¯ Ù…Ø¹ØªØ¨Ø± ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯:")
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
        [InlineKeyboardButton(f"ðŸ’³ Ù¾Ø±Ø¯Ø§Ø®Øª Ø¨ÛŒØ¹Ø§Ù†Ù‡ ({deposit_amount:,.0f} ØªÙˆÙ…Ø§Ù†)", callback_data="paytype:deposit")],
        [InlineKeyboardButton(f"ðŸ’° Ù¾Ø±Ø¯Ø§Ø®Øª Ú©Ø§Ù…Ù„ ({total_group_price:,.0f} ØªÙˆÙ…Ø§Ù†)", callback_data="paytype:full")],
    ]
    
    msg = (
        f"âœ… Ø§Ø·Ù„Ø§Ø¹Ø§Øª {len(saved_participants)} Ù†ÙØ± Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø«Ø¨Øª Ø´Ø¯.\n\n"
        f"Ù…Ø¨Ù„Øº Ú©Ù„ ØªÙˆØ± Ø¨Ø±Ø§ÛŒ Ø§ÛŒÙ† Ú¯Ø±ÙˆÙ‡: {total_group_price:,.0f} ØªÙˆÙ…Ø§Ù†\n"
        "Ù„Ø·ÙØ§Ù‹ Ù†ÙˆØ¹ Ù¾Ø±Ø¯Ø§Ø®Øª Ø®ÙˆØ¯ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:"
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
        f"Ù…Ø¨Ù„Øº Ù‚Ø§Ø¨Ù„ Ù¾Ø±Ø¯Ø§Ø®Øª: **{expected_amount:,.0f} ØªÙˆÙ…Ø§Ù†**\n\n"
        "Ù„Ø·ÙØ§Ù‹ Ù…Ø¨Ù„Øº ÙÙˆÙ‚ Ø±Ø§ ÙˆØ§Ø±ÛŒØ² Ú©Ø±Ø¯Ù‡ Ùˆ ØªØµÙˆÛŒØ± ÙÛŒØ´ ÙˆØ§Ø±ÛŒØ²ÛŒ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯."
    )
    await query.edit_message_text(msg, parse_mode="Markdown")
    return PAY_RECEIPT

async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Ù„Ø·ÙØ§Ù‹ ØªØµÙˆÛŒØ± ÙÛŒØ´ Ø±Ø§ Ø¨Ù‡ ØµÙˆØ±Øª Ø¹Ú©Ø³ (Photo) Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯:")
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
        "ðŸ§¾ ÙÛŒØ´ Ø´Ù…Ø§ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø«Ø¨Øª Ø´Ø¯ Ùˆ Ø¯Ø± Ø§Ù†ØªØ¸Ø§Ø± Ø¨Ø±Ø±Ø³ÛŒ ØªÙˆØ³Ø· Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ø³Øª.\n"
        "Ù†ØªÛŒØ¬Ù‡ Ù¾Ø³ Ø§Ø² Ø¨Ø±Ø±Ø³ÛŒ Ø§Ø² Ù‡Ù…ÛŒÙ† Ø·Ø±ÛŒÙ‚ Ø¨Ù‡ Ø´Ù…Ø§ Ø§Ø·Ù„Ø§Ø¹ Ø¯Ø§Ø¯Ù‡ Ø®ÙˆØ§Ù‡Ø¯ Ø´Ø¯."
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
        await update.message.reply_text("Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø± Ù‡ÛŒÚ† ØªÙˆØ± ÙØ¹Ø§Ù„ÛŒ ÛŒØ§ÙØª Ù†Ø´Ø¯.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(f"ðŸŒ² {t.title}", callback_data=f"paytrip:{t.id}")] for t in trips]
    await update.message.reply_text("Ù„Ø·ÙØ§Ù‹ ØªÙˆØ±ÛŒ Ú©Ù‡ Ø¯Ø± Ø¢Ù† Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ú©Ø±Ø¯Ù‡â€ŒØ§ÛŒØ¯ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PAY_TRIP_SELECT

async def pay_trip_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    trip_id = int(query.data.split(":")[1])
    tg_user_id = update.effective_user.id

    with Session(engine) as session:
        # Ù¾ÛŒØ¯Ø§ Ú©Ø±Ø¯Ù† Ø«Ø¨Øªâ€ŒÙ†Ø§Ù…ÛŒ Ú©Ù‡ Ø§ÛŒÙ† Ú©Ø§Ø±Ø¨Ø± Ù†Ù…Ø§ÛŒÙ†Ø¯Ù‡/Ø«Ø¨Øªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø¢Ù† Ø¨ÙˆØ¯Ù‡ Ø§Ø³Øª
        participants = session.exec(
            select(Participant).where(
                Participant.trip_id == trip_id,
                Participant.telegram_user_id == tg_user_id
            )
        ).all()

        if not participants:
            await query.edit_message_text("Ù‡ÛŒÚ† Ø«Ø¨Øªâ€ŒÙ†Ø§Ù…ÛŒ Ø¨Ù‡ Ù†Ø§Ù… Ø´Ù…Ø§ Ø¨Ø±Ø§ÛŒ Ø§ÛŒÙ† ØªÙˆØ± ÛŒØ§ÙØª Ù†Ø´Ø¯.")
            return ConversationHandler.END

        # Ø§Ú¯Ø± Ú†Ù†Ø¯ Ú¯Ø±ÙˆÙ‡ Ø¯Ø§Ø´Øª Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†Ø¯ØŒ Ø¯Ø± ØºÛŒØ± Ø§ÛŒÙ† ØµÙˆØ±Øª Ù‡Ù…ÙˆÙ† Ø§ÙˆÙ„ÛŒ
        p = participants[0]
        
        # Ù…Ø­Ø§Ø³Ø¨Ù‡ Ú©Ù„ Ø¨Ø¯Ù‡ÛŒ Ú¯Ø±ÙˆÙ‡ Ø¨Ø± Ø§Ø³Ø§Ø³ group_id
        group_members = session.exec(
            select(Participant).where(Participant.group_id == p.group_id)
        ).all() if p.group_id else [p]
        
        trip = session.get(Trip, trip_id)
        total_group_price = trip.price * len(group_members)
        
        confirmed_paid = get_confirmed_total(p.id)
        remaining = total_group_price - confirmed_paid

        if remaining <= 0:
            await query.edit_message_text("âœ… ØªÙ…Ø§Ù… Ù‡Ø²ÛŒÙ†Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙˆØ± Ø¨Ø±Ø§ÛŒ Ø´Ù…Ø§ Ùˆ Ú¯Ø±ÙˆÙ‡ØªØ§Ù† Ú©Ø§Ù…Ù„Ø§Ù‹ ØªØ³ÙˆÛŒÙ‡ Ø´Ø¯Ù‡ Ø§Ø³Øª.")
            return ConversationHandler.END

        if has_pending(p.id):
            await query.edit_message_text("â³ Ø´Ù…Ø§ ÛŒÚ© ÙÛŒØ´ Ø¯Ø± Ø§Ù†ØªØ¸Ø§Ø± Ø¨Ø±Ø±Ø³ÛŒ Ø¯Ø§Ø±ÛŒØ¯. Ù„Ø·ÙØ§Ù‹ ØªØ§ Ø²Ù…Ø§Ù† ØªØ¹ÛŒÛŒÙ† ØªÚ©Ù„ÛŒÙ Ø¢Ù† ØµØ¨Ø± Ú©Ù†ÛŒØ¯.")
            return ConversationHandler.END

        context.user_data["main_participant_id"] = p.id
        context.user_data["trip_id"] = trip_id
        context.user_data["pay_type"] = "remaining"
        context.user_data["expected_amount"] = remaining

        await query.edit_message_text(
            f"Ù…Ø¨Ù„Øº Ø¨Ø§Ù‚ÛŒâ€ŒÙ…Ø§Ù†Ø¯Ù‡ Ø¬Ù‡Øª ØªØ³ÙˆÛŒÙ‡ Ú¯Ø±ÙˆÙ‡ ({len(group_members)} Ù†ÙØ±): **{remaining:,.0f} ØªÙˆÙ…Ø§Ù†**\n\n"
            "Ù„Ø·ÙØ§Ù‹ Ù…Ø¨Ù„Øº ÙÙˆÙ‚ Ø±Ø§ ÙˆØ§Ø±ÛŒØ² Ú©Ø±Ø¯Ù‡ Ùˆ ØªØµÙˆÛŒØ± ÙÛŒØ´ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯:",
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
            await update.message.reply_text(
                f"✅ ثبت نام شما با موفقیت انجام شد.\\n\\n"
                f"🏷️ سفر: {trip.title}\\n"
                f"👤 نام: {full_name}\\n"
                f"📞 کد ملی: {national_id}\\n"
                f"📱 شماره تماس: {phone_number}\\n"
                f"🚗 انتخاب وسیله نقلیه: {"ماشین شخصی" if vehicle_choice == "own" else "ماشین دیگر"}\\n\\n"
                f"💷 لطفاً نوع پرداخت را انتخاب کنید:"
                reply_markup=reply_markup
            )

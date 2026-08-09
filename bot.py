import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, 
    MessageHandler, ConversationHandler, filters
)
from sqlmodel import Session, select
from main import engine, Participant, Trip

TRIP_SELECT, NAME, NATIONAL_ID, PHONE = range(4)

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session(engine) as session:
        trips = session.exec(select(Trip)).all()
        
        if not trips:
            await update.message.reply_text("❌ در حال حاضر هیچ توری برای ثبت‌نام فعال نیست.")
            return ConversationHandler.END
        
        context.user_data['trips_map'] = {f"{t.title} (کد {t.id})": t.id for t in trips}
        keyboard = [[button] for button in context.user_data['trips_map'].keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "لطفاً توری که می‌خواهید در آن ثبت‌نام کنید را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return TRIP_SELECT

async def select_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_option = update.message.text
    trips_map = context.user_data.get('trips_map', {})
    
    if selected_option not in trips_map:
        await update.message.reply_text("لطفاً یکی از گزینه‌های کیبورد را انتخاب کنید:")
        return TRIP_SELECT
    
    context.user_data['trip_id'] = trips_map[selected_option]
    context.user_data['selected_trip_title'] = selected_option
    
    await update.message.reply_text(
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text.strip()
    if len(full_name) < 3:
        await update.message.reply_text("لطفاً نام و نام خانوادگی معتبر وارد کنید:")
        return NAME
        
    context.user_data['full_name'] = full_name
    await update.message.reply_text("لطفاً **کد ملی** خود را وارد کنید:")
    return NATIONAL_ID

async def get_national_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    national_id = update.message.text.strip()
    if not national_id.isdigit() or len(national_id) != 10:
        await update.message.reply_text("کد ملی باید یک عدد ۱۰ رقمی باشد. لطفاً دوباره وارد کنید:")
        return NATIONAL_ID
        
    context.user_data['national_id'] = national_id
    phone_keyboard = [[KeyboardButton("📱 ارسال شماره تماس من", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(phone_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "لطفاً **شماره تماس** خود را وارد کنید یا از دکمه زیر جهت ارسال سریع استفاده کنید:",
        reply_markup=reply_markup
    )
    return PHONE

async def get_phone_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    context.user_data['phone_number'] = phone_number
    
    try:
        with Session(engine) as session:
            new_participant = Participant(
                full_name=context.user_data['full_name'],
                national_id=context.user_data['national_id'],
                phone_number=context.user_data['phone_number'],
                trip_id=context.user_data['trip_id']
            )
            session.add(new_participant)
            session.commit()
            
        await update.message.reply_text(
            f"✅ **ثبت‌نام شما با موفقیت انجام شد!**\n\n"
            f"🏕 **تور:** {context.user_data['selected_trip_title']}\n"
            f"👤 **نام:** {context.user_data['full_name']}\n"
            f"🆔 **کد ملی:** {context.user_data['national_id']}\n"
            f"📞 **شماره تماس:** {context.user_data['phone_number']}",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ خطایی در ذخیره اطلاعات رخ داد. لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardRemove()
        )
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند ثبت‌نام لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def build_bot_app():
    token = os.getenv("BOT_TOKEN", "8595655776:AAFlEH8DOxM8pZXdZaoPXjMwPzsYneY7_R8")
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_registration), CommandHandler('register', start_registration)],
        states={
            TRIP_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_trip)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            NATIONAL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_national_id)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone_and_save),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_and_save)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    return app

# تابع اجرای همزمان با FastAPI
async def start_bot():
    telegram_app = build_bot_app()
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
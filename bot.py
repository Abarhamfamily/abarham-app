import os
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# تعریف مراحل گفتگو (Conversation States)
FULL_NAME, NATIONAL_ID, PHONE, SELECT_TRIP = range(4)

# آدرس API برنامه روی Render
API_BASE_URL = "https://abarham-app.onrender.com"
TOKEN = "8595655776:AAFlEH8DOxM8pZXdZaoPXjMwPzsYneY7_R8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به سامانه ثبت‌نام تورهای طبیعت‌گردی ابرهام خوش آمدید. 🌲\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return FULL_NAME

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text.strip()
    await update.message.reply_text("لطفاً **کد ملی** ۱۰ رقمی خود را وارد کنید:")
    return NATIONAL_ID

async def get_national_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['national_id'] = update.message.text.strip()
    await update.message.reply_text("لطفاً **شماره موبایل** خود را وارد کنید:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()

    # دریافت لیست تورهای فعال از API برنامه
    try:
        response = requests.get(f"{API_BASE_URL}/trips")
        trips = response.json()
    except Exception:
        await update.message.reply_text("❌ خطا در برقراری ارتباط با سرور. لطفاً بعداً تلاش کنید.")
        return ConversationHandler.END

    if not trips:
        await update.message.reply_text("⚠️ در حال حاضر هیچ توری برای ثبت‌نام فعال نیست.")
        return ConversationHandler.END

    # ذخیره لیست تورها در حافظه موقت ربات
    context.user_data['available_trips'] = trips

    # ساخت کیبورد انتخابی از عناوین تورها
    keyboard = [[trip['title']] for trip in trips]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "لطفاً توری که قصد ثبت‌نام در آن را دارید انتخاب کنید:",
        reply_markup=reply_markup
    )
    return SELECT_TRIP

async def select_trip_and_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_title = update.message.text.strip()
    trips = context.user_data.get('available_trips', [])

    # پیدا کردن ID تور انتخابی
    selected_trip = next((t for t in trips if t['title'] == selected_title), None)

    if not selected_trip:
        await update.message.reply_text("❌ تور انتخاب‌شده معتبر نیست. لطفاً مجدداً از دکمه‌ها انتخاب کنید.")
        return SELECT_TRIP

    # آماده‌سازی پکیج داده دقیقاً طبق فیلدهای FastAPI
    payload = {
        "trip_id": selected_trip['id'],
        "full_name": context.user_data['full_name'],
        "national_id": context.user_data['national_id'],
        "phone": context.user_data['phone']
    }

    # ارسال مستقیم اطلاعات به API اپلیکیشن
    try:
        res = requests.post(f"{API_BASE_URL}/participants", json=payload)
        if res.status_code == 200:
            await update.message.reply_text(
                f"✅ ثبت‌نام شما در تور **{selected_title}** با موفقیت انجام شد!\nاطلاعات شما در سامانه ابرهام ثبت گردید.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text("❌ خطایی در ثبت اطلاعات رخ داد. لطفاً با پشتیبانی تماس بگیرید.")
    except Exception:
        await update.message.reply_text("❌ خطای شبکه هنگام ارسال اطلاعات.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند ثبت‌نام لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            NATIONAL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_national_id)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SELECT_TRIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_trip_and_submit)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
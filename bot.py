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

# تعریف مراحل گفتگو (فیلدهای ثبت‌نام)
FULL_NAME, NATIONAL_ID, PHONE, SELECT_TRIP, CONFIRMATION = range(5)

API_BASE_URL = "https://abarham-app.onrender.com"
TOKEN = "8595655776:AAFlEH8DOxM8pZXdZaoPXjMwPzsYneY7_R8"

# مرحله ۱: شروع ثبت‌نام و دریافت نام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به سامانه ثبت‌نام تورهای طبیعت‌گردی اَبَرهام خوش آمدید. 🌲\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return FULL_NAME

# مرحله ۲: دریافت کد ملی
async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text.strip()
    await update.message.reply_text("لطفاً **کد ملی** (۱۰ رقمی) خود را جهت صدور بیمه وارد کنید:")
    return NATIONAL_ID

# مرحله ۳: دریافت شماره تماس
async def get_national_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['national_id'] = update.message.text.strip()
    await update.message.reply_text("لطفاً **شماره موبایل** در دسترس خود را وارد کنید:")
    return PHONE

# مرحله ۴: نمایش لیست تورها و انتخاب
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()

    # دریافت تورهای فعال از API
    try:
        response = requests.get(f"{API_BASE_URL}/trips")
        trips = response.json()
    except Exception:
        await update.message.reply_text("❌ خطا در برقراری ارتباط با سرور.")
        return ConversationHandler.END

    if not trips:
        await update.message.reply_text("⚠️ در حال حاضر هیچ توری برای ثبت‌نام فعال نیست.")
        return ConversationHandler.END

    context.user_data['available_trips'] = trips
    keyboard = [[trip['title']] for trip in trips]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "لطفاً توری که قصد شرکت در آن را دارید انتخاب کنید:",
        reply_markup=reply_markup
    )
    return SELECT_TRIP

# مرحله ۵: پیش‌نمایش و تأیید نهایی
async def select_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_title = update.message.text.strip()
    trips = context.user_data.get('available_trips', [])
    selected_trip = next((t for t in trips if t['title'] == selected_title), None)

    if not selected_trip:
        await update.message.reply_text("❌ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
        return SELECT_TRIP

    context.user_data['selected_trip'] = selected_trip

    summary_text = (
        "📋 **پیش‌نمایش اطلاعات ثبت‌نام:**\n\n"
        f"👤 **نام و نام خانوادگی:** {context.user_data['full_name']}\n"
        f"🆔 **کد ملی:** {context.user_data['national_id']}\n"
        f"📱 **شماره تماس:** {context.user_data['phone']}\n"
        f"🚌 **تور انتخابی:** {selected_trip['title']}\n\n"
        "آیا اطلاعات مورد تأیید است؟"
    )

    confirm_keyboard = [["✅ تأیید و ثبت نهایی"], ["❌ انصراف"]]
    reply_markup = ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(summary_text, parse_mode="Markdown", reply_markup=reply_markup)
    return CONFIRMATION

# مرحله ۶: ارسال نهایی به دیتابیس
async def submit_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text.strip()

    if user_choice == "❌ انصراف":
        await update.message.reply_text("ثبت‌نام لغو شد.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    if user_choice != "✅ تأیید و ثبت نهایی":
        await update.message.reply_text("لطفاً از دکمه‌های پایین انتخاب کنید.")
        return CONFIRMATION

    payload = {
        "trip_id": context.user_data['selected_trip']['id'],
        "full_name": context.user_data['full_name'],
        "national_id": context.user_data['national_id'],
        "phone": context.user_data['phone']
    }

    try:
        res = requests.post(f"{API_BASE_URL}/participants", json=payload)
        if res.status_code in [200, 201]:
            await update.message.reply_text(
                "🎉 **ثبت‌نام شما با موفقیت در سامانه اَبَرهام ثبت شد!**",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text("❌ خطایی در ثبت اطلاعات رخ داد.")
    except Exception:
        await update.message.reply_text("❌ خطای ارتباط با سرور.")

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
            SELECT_TRIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_trip)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
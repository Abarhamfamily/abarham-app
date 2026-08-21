import sys
path = r'c:\Users\Monfared\Desktop\abarham_quick\bot.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
old_block = '''            await update.message.reply_text(
                f"✅ ثبت\u200cنام شما با موفقیت انجام شد.\n
                \n
                "
                f"🏷️ سفر: {trip.title}\n
                \n
                "
                f"👤 نام: {full_name}\n
                \n
                "
                f"📞 کد ملی: {national_id}\n
                \n
                "
                f"📱 شماره تماس: {phone_number}\n
                \n
                "
                f"🚗 انتخاب وسیله نقلیه: {'ماشین شخصی' if vehicle_choice == 'own' else 'ماشین دیگر'}\n
                \n
                "
                f"💷 لطفاً نوع پرداخت را انتخاب کنید:\",
                reply_markup=reply_markup
            )'''
new_block = '''            await update.message.reply_text(
                f"✅ ثبت‌نام شما با موفقیت انجام شد.\n\n"
                f"🏷️ سفر: {trip.title}\n"
                f"👤 نام: {full_name}\n"
                f"📞 کد ملی: {national_id}\n"
                f"📱 شماره تماس: {phone_number}\n"
                f"🚗 انتخاب وسیله نقلیه: {'ماشین شخصی' if vehicle_choice == 'own' else 'ماشین دیگر'}\n\n"
                f"💷 لطفاً نوع پرداخت را انتخاب کنید:\",
                reply_markup=reply_markup
            )'''
new_content = content.replace(old_block, new_block)
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
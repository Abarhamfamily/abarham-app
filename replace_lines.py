import sys
path = r'c:\Users\Monfared\Desktop\abarham_quick\bot.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
# lines are 0-indexed
# Replace lines 445 to 466 inclusive (since line 446 is index 445, line 467 is index 466)
new_lines = lines[:445]
new_lines.append('            await update.message.reply_text(\n')
new_lines.append('                f"✅ ثبت‌نام شما با موفقیت انجام شد.\\n\\n"\n')
new_lines.append('                f"🏷️ سفر: {trip.title}\\n"\n')
new_lines.append('                f"👤 نام: {full_name}\\n"\n')
new_lines.append('                f"📞 کد ملی: {national_id}\\n"\n')
new_lines.append('                f"📱 شماره تماس: {phone_number}\\n"\n')
new_lines.append('                f"🚗 انتخاب وسیله نقلیه: {\\'ماشین شخصی\\' if vehicle_choice == \\'own\\' else \\'ماشین دیگر\\'}\\n\\n"\n')
new_lines.append('                f"💷 لطفاً نوع پرداخت را انتخاب کنید:",\n')
new_lines.append('                reply_markup=reply_markup\n')
new_lines.append('            )\n')
new_lines.extend(lines[467:])  # skip the old lines 445-466
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
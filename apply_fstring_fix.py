import re

file_path = "original_bot.py"
output_path = "temp_bot.py"

# Read original content
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Correct block replacement
correct_block = '''            await update.message.reply_text(
                 f\"✅ ثبت نام شما با موفقیت انجام شد.\\\\n\\\\n\"
                 f\"🏷️ سفر: {trip.title}\\\\n\"
                 f\"👤 نام: {full_name}\\\\n\"
                 f\"📞 کد ملی: {national_id}\\\\n\"
                 f\"📱 شماره تماس: {phone_number}\\\\n\"
                 f\"🚗 انتخاب وسیله نقلیه: {'ماشین شخصی' if vehicle_choice == 'own' else 'ماشین другу'}\\\\n\\\\n\"
                 f\"💷 لطفاً نوع پرداخت را انتخاب کنید:\",
                 reply_markup=reply_markup
             )'''

# Regex to catch the malformed reply_text inside get_vehicle_choice_and_save
pattern = r'await update\\.message\\.reply_text\\(\\s*f\"✅.*?\\n\\s*reply_markup=reply_markup\\s*\\)'

if re.search(pattern, content, flags=re.DOTALL):
    new_content = re.sub(pattern, correct_block, content, flags=re.DOTALL)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("SUCCESS: F-string fix applied.")
else:
    print("WARNING: Pattern not matched via regex. Trying string partition.")
    # We'll not implement the fallback for now.
    exit(1)
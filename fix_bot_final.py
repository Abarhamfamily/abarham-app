import re

file_path = "bot.py"

# Read original content
with open(file_path, "r", encoding="utf-8-sig") as f:
    content = f.read()

# Correct block replacement
correct_block = '''            await update.message.reply_text(
                f"✅ ثبت نام شما با موفقیت انجام شد.\\n\\n"
                f"🏷️ سفر: {trip.title}\\n"
                f"👤 نام: {full_name}\\n"
                f"📞 کد ملی: {national_id}\\n"
                f"📱 شماره تماس: {phone_number}\\n"
                f"🚗 انتخاب وسیله نقلیه: {'ماشین شخصی' if vehicle_choice == 'own' else 'ماشین دیگر'}\\n\\n"
                f"💷 لطفاً نوع پرداخت را انتخاب کنید:",
                reply_markup=reply_markup
            )'''

# Regex to catch the malformed reply_text inside get_vehicle_choice_and_save
pattern = r'await update\.message\.reply_text\(\s*f"✅.*?\n\s*reply_markup=reply_markup\s*\)'

if re.search(pattern, content, flags=re.DOTALL):
    new_content = re.sub(pattern, correct_block, content, flags=re.DOTALL)
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("SUCCESS: Replacement applied.")
else:
    print("WARNING: Pattern not matched via regex. Trying string partition.")
    # Fallback to function block replacement if regex fails
    start_str = 'await update.message.reply_text('
    end_str = 'reply_markup=reply_markup\n            )'
    # Execute precise manual fix on get_vehicle_choice_and_save area
    # Find the function get_vehicle_choice_and_save
    func_start = content.find('async def get_vehicle_choice_and_save(')
    if func_start == -1:
        print("ERROR: Could not find get_vehicle_choice_and_save function")
        exit(1)
    # Find the start of the reply_text block after the function start
    reply_start = content.find(start_str, func_start)
    if reply_start == -1:
        print("ERROR: Could not find await update.message.reply_text(")
        exit(1)
    # Find the end of the reply_text block
    reply_end = content.find(end_str, reply_start)
    if reply_end == -1:
        print("ERROR: Could not find end of reply_text block")
        exit(1)
    # Include the end_str in the replacement
    reply_end += len(end_str)
    # Replace the block
    new_content = content[:reply_start] + correct_block + content[reply_end:]
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("SUCCESS: Replacement applied via fallback.")
import sys

filepath = r'c:\Users\Monfared\Desktop\abarham_quick\bot.py'
# Read the file
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We know the problematic block is around lines 446-467 (1-indexed)
# Convert to 0-indexed: start at 445, end at 466 (inclusive)
start_idx = 445  # line 446
end_idx = 466    # line 467

# Define the replacement block (as list of strings, each ending with newline)
new_block = [
    '            await update.message.reply_text(\n',
    '                f"✅ ثبت نام شما با موفقیت انجام شد.\\n\\n"\n',
    '                f"🏷️ سفر: {trip.title}\\n"\n',
    '                f"👤 نام: {full_name}\\n"\n',
    '                f"📞 کد ملی: {national_id}\\n"\n',
    '                f"📱 شماره تماس: {phone_number}\\n"\n',
    '                f"🚗 انتخاب وسیله نقلیه: {\\'ماشین شخصی\\' if vehicle_choice == \\'own\\' else \\'ماشین دیگر\\'}\\n\\n"\n',
    '                f"💷 لطفاً نوع پرداخت را انتخاب کنید:"\n',
    '                reply_markup=reply_markup\n',
    '            )\n'
]

# Replace the lines
lines[start_idx:end_idx+1] = new_block

# Write back
with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(lines)

print('Replacement done. Now compiling...')

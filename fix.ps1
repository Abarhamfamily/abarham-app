$head = Get-Content -Path 'c:\Users\Monfared\Desktop\abarham_quick\bot.py' -Head 445
$tail = Get-Content -Path 'c:\Users\Monfared\Desktop\abarham_quick\bot.py' -Tail ([Math]::Max(0, (Get-Content -Path 'c:\Users\Monfared\Desktop\abarham_quick\bot.py').Count - 467))
$new = @(
    '            await update.message.reply_text(',
    '                f"✅ ثبت نام شما با موفقیت انجام شد.\\n\\n"',
    '                f"🏷️ سفر: {trip.title}\\n"',
    '                f"👤 نام: {full_name}\\n"',
    '                f"📞 کد ملی: {national_id}\\n"',
    '                f"📱 شماره تماس: {phone_number}\\n"',
    '                f"🚗 انتخاب وسیله نقلیه: {"ماشین شخصی" if vehicle_choice == "own" else "ماشین دیگر"}\\n\\n"',
    '                f"💷 لطفاً نوع پرداخت را انتخاب کنید:"',
    '                reply_markup=reply_markup',
    '            )'
)
$all = $head + $new + $tail
$all | Set-Content -Path 'c:\Users\Monfared\Desktop\abarham_quick\bot.py' -Encoding UTF8

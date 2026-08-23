"""
تست‌های این فایل بر اساس Section J مستند معماری طراحی شده‌اند اما به
RegistrationService، PaymentService و WalletService نیاز دارند که هنوز در
اسکلت فعلی پیاده‌سازی نشده‌اند (به TODOهای src/api/v1/registrations.py،
payments.py و wallet.py مراجعه کنید).

با تکمیل هر سرویس در فازهای بعدی، تست‌های مربوطه را از مستند معماری
(Section J) به این فایل یا فایل‌های مجزا در tests/unit/ منتقل و فعال کنید.
نمونه‌ها:
  - test_register_for_trip_with_capacity
  - test_register_when_full_adds_to_waitlist
  - test_prevent_double_registration
  - test_payment_is_isolated_by_registration
  - test_idempotency_prevents_double_payment
  - test_concurrent_withdrawals_prevent_overdraft
  - test_race_condition_last_seat
"""

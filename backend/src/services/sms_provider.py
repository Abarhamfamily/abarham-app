import logging
import random

logger = logging.getLogger(__name__)


def generate_otp_code() -> str:
    """
    تولید یک کد OTP تصادفی ۶ رقمی.
    """
    return f"{random.randint(0, 999999):06d}"


def send_sms(phone_number: str, message: str) -> bool:
    """
    لایه‌ی انتزاعی برای ارسال پیامک.

    در نسخه‌ی فعلی (mock)، فقط پیام را در لاگ ثبت می‌کند و همیشه True
    برمی‌گرداند.

    در آینده، این تابع باید با یک فراخوانی واقعی به API ارائه‌دهنده‌ی
    SMS (مثلاً کاوه‌نگار) جایگزین شود، بر اساس تنظیمات SMS_PROVIDER در
    core/config.py.
    """
    logger.info("[MOCK SMS] to %s: %s", phone_number, message)
    return True
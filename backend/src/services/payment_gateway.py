import uuid
from decimal import Decimal


def create_payment_request(amount: Decimal, description: str) -> dict:
    """
    لایه‌ی انتزاعی برای شروع یک تراکنش پرداخت.

    در نسخه‌ی فعلی (mock)، یک authority ساختگی تولید می‌کند.
    در آینده، این تابع باید با یک فراخوانی واقعی به API درگاه پرداخت
    (مثلاً زرین‌پال، endpoint: request.json) جایگزین شود که در پاسخ
    یک authority واقعی و لینک پرداخت واقعی برمی‌گرداند.

    Returns:
        dict با کلیدهای authority و payment_url
    """
    authority = f"MOCK-{uuid.uuid4().hex[:16]}"
    return {
        "authority": authority,
        "payment_url": f"https://mock-gateway.local/pay/{authority}",
    }


def verify_payment(authority: str) -> bool:
    """
    لایه‌ی انتزاعی برای تأیید نتیجه‌ی یک تراکنش پرداخت.

    در نسخه‌ی فعلی (mock)، همیشه True برمی‌گرداند مگر این‌که authority
    با پیشوند "MOCK-FAIL" شروع شده باشد (برای امکان تست حالت شکست).

    در آینده، این تابع باید با یک فراخوانی واقعی به API تأیید درگاه
    پرداخت (مثلاً زرین‌پال، endpoint: verify.json) جایگزین شود.

    Returns:
        True اگر پرداخت تأیید شد، False در غیر این صورت.
    """
    if authority.startswith("MOCK-FAIL"):
        return False
    return True

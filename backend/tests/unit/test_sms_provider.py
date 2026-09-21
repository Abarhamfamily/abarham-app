import pytest

from src.services.sms_provider import generate_otp_code, send_sms


def test_generate_otp_code_returns_six_digits():
    """بررسی کند طول کد تولیدشده دقیقاً ۶ کاراکتر است و فقط شامل ارقام است."""
    code = generate_otp_code()

    assert len(code) == 6
    assert code.isdigit()


def test_generate_otp_code_generates_different_codes():
    """تولید ۱۰ کد و بررسی اینکه همه یکسان نیستند."""
    codes = [generate_otp_code() for _ in range(10)]

    assert len(set(codes)) > 1


def test_send_sms_returns_true():
    """send_sms باید همیشه True برگرداند."""
    result = send_sms("+989120000000", "test message")

    assert result is True
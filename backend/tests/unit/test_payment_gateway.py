import pytest
from decimal import Decimal

from src.services.payment_gateway import create_payment_request, verify_payment


def test_create_payment_request_returns_authority_and_url():
    """بررسی کند خروجی create_payment_request شامل کلیدهای authority و payment_url است."""
    amount = Decimal("100000")
    description = "خرید آزمایشی"

    result = create_payment_request(amount=amount, description=description)

    assert "authority" in result
    assert "payment_url" in result
    assert result["authority"].startswith("MOCK-")
    assert result["payment_url"] == f"https://mock-gateway.local/pay/{result['authority']}"


def test_create_payment_request_generates_unique_authority():
    """دو بار فراخوانی کند و مطمئن شود دو authority متفاوت تولید می‌شود."""
    amount = Decimal("50000")
    description = "خرید آزمایشی"

    result1 = create_payment_request(amount=amount, description=description)
    result2 = create_payment_request(amount=amount, description=description)

    assert result1["authority"] != result2["authority"]
    assert result1["payment_url"] != result2["payment_url"]


def test_verify_payment_returns_true_for_normal_authority():
    """verify_payment(\"MOCK-abc123\") باید True برگرداند."""
    result = verify_payment("MOCK-abc123")
    assert result is True


def test_verify_payment_returns_false_for_fail_authority():
    """verify_payment(\"MOCK-FAIL-abc123\") باید False برگرداند."""
    result = verify_payment("MOCK-FAIL-abc123")
    assert result is False

import os
import uuid

from sqlmodel import Session, select, func

from models import engine, Payment, Trip


# ---------------------------------------------------------------------------
# محاسبه مبلغ
# ---------------------------------------------------------------------------
def calculate_deposit(trip_price: float) -> float:
    """بیعانه = ۲۵٪ قیمت کل تور"""
    return round(trip_price * 0.25, 2)


def calculate_full_amount(trip_price: float, confirmed_total: float) -> float:
    """پرداخت کامل = ۱۰۰٪ قیمت یا تسویه باقی‌مانده"""
    if confirmed_total <= 0:
        return trip_price
    return round(trip_price - confirmed_total, 2)


# ---------------------------------------------------------------------------
# کوئری‌های وضعیت پرداخت
# ---------------------------------------------------------------------------
def get_confirmed_total(participant_id: int, trip_id: int, session: Session = None) -> float:
    """جمع مبالغ تأییدشده (فقط status=confirmed)"""
    if session is None:
        with Session(engine) as session:
            return _confirmed_total_query(session, participant_id, trip_id)
    return _confirmed_total_query(session, participant_id, trip_id)


def _confirmed_total_query(session: Session, participant_id: int, trip_id: int) -> float:
    total = session.exec(
        select(func.sum(Payment.expected_amount)).where(
            Payment.participant_id == participant_id,
            Payment.trip_id == trip_id,
            Payment.status == "confirmed",
        )
    ).one()
    return total or 0.0


def is_fully_paid(participant_id: int, trip_id: int, trip_price: float = None, session: Session = None) -> bool:
    """آیا مجموع پرداخت‌های تأییدشده به قیمت تور رسیده است؟"""
    if trip_price is None:
        if session is None:
            with Session(engine) as s:
                trip = s.get(Trip, trip_id)
                if not trip:
                    return False
                trip_price = trip.price
        else:
            trip = session.get(Trip, trip_id)
            if not trip:
                return False
            trip_price = trip.price
    confirmed_total = get_confirmed_total(participant_id, trip_id, session)
    return confirmed_total >= trip_price


def has_pending(participant_id: int, trip_id: int, session: Session = None) -> bool:
    """آیا Payment با status=pending_review برای این participant+trip وجود دارد؟"""
    if session is None:
        with Session(engine) as session:
            return _pending_query(session, participant_id, trip_id)
    return _pending_query(session, participant_id, trip_id)


def _pending_query(session: Session, participant_id: int, trip_id: int) -> bool:
    pending = session.exec(
        select(Payment).where(
            Payment.participant_id == participant_id,
            Payment.trip_id == trip_id,
            Payment.status == "pending_review",
        )
    ).first()
    return pending is not None


# ---------------------------------------------------------------------------
# انتقال وضعیت
# ---------------------------------------------------------------------------
VALID_TRANSITIONS = {
    "pending_review": {"confirmed", "rejected"},
}


def transition_status(payment: Payment, new_status: str) -> Payment:
    """انتقال وضعیت با اعتبارسنجی: فقط pending_review → confirmed/rejected"""
    allowed = VALID_TRANSITIONS.get(payment.status, set())
    if new_status not in allowed:
        raise ValueError(
            f"انتقال وضعیت نامعتبر: {payment.status} → {new_status}"
        )
    payment.status = new_status
    return payment


# ---------------------------------------------------------------------------
# ذخیره/بازیابی فیش
# ---------------------------------------------------------------------------
RECEIPTS_DIR = "receipts"


def save_receipt(file_bytes: bytes, extension: str = "jpg") -> str:
    """ذخیره فیش با نام یکتای UUID و برگرداندن مسیر نسبی"""
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    filename = f"receipt_{uuid.uuid4().hex}.{extension}"
    path = os.path.join(RECEIPTS_DIR, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def get_receipt_path(receipt_local_path: str) -> str:
    """برگرداندن مسیر کامل فایل فیش"""
    return receipt_local_path
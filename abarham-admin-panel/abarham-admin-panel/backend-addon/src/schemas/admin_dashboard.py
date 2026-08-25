from decimal import Decimal

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_trips: int
    published_trips: int
    total_registrations: int
    pending_payment_registrations: int
    confirmed_registrations: int
    pending_payments_count: int
    confirmed_payments_total: Decimal
    total_wallet_balance: Decimal
    unread_notifications: int

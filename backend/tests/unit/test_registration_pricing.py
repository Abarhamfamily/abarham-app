from decimal import Decimal

import pytest

from src.domain.registrations import calculate_registration_price


def test_own_vehicle_price():
    assert calculate_registration_price(
        trip_price=Decimal("1000000"),
        other_vehicle_price=None,
        vehicle_type="own",
        passenger_count=2,
    ) == Decimal("2000000")


def test_other_vehicle_price():
    assert calculate_registration_price(
        trip_price=Decimal("1000000"),
        other_vehicle_price=Decimal("200000"),
        vehicle_type="other",
        passenger_count=2,
    ) == Decimal("2400000")


def test_other_vehicle_without_price_raises():
    with pytest.raises(ValueError):
        calculate_registration_price(
            trip_price=Decimal("1000000"),
            other_vehicle_price=None,
            vehicle_type="other",
            passenger_count=1,
        )


def test_zero_passenger_count_raises():
    with pytest.raises(ValueError):
        calculate_registration_price(
            trip_price=Decimal("1000000"),
            other_vehicle_price=Decimal("200000"),
            vehicle_type="other",
            passenger_count=0,
        )


def test_none_vehicle_type_treated_as_other():
    assert calculate_registration_price(
        trip_price=Decimal("1000000"),
        other_vehicle_price=Decimal("200000"),
        vehicle_type=None,
        passenger_count=2,
    ) == Decimal("2400000")

from decimal import Decimal

import pytest

from sentinelpr_lab import Discount, OrderItem, calculate_total, validate_discount

D = Decimal


def test_total_without_discount():
    items = [OrderItem(D("10.00"), 2), OrderItem(D("5.50"), 1)]
    assert calculate_total(items) == D("25.50")


def test_percentage_discount():
    assert calculate_total([OrderItem(D("100"), 1)], Discount(D("10"))) == D("90.00")


def test_discount_applies_well_above_threshold():
    discount = Discount(D("20"), min_subtotal=D("50"))
    assert calculate_total([OrderItem(D("100"), 1)], discount) == D("80.00")


def test_discount_skipped_below_threshold():
    discount = Discount(D("20"), min_subtotal=D("50"))
    assert calculate_total([OrderItem(D("10"), 1)], discount) == D("10.00")


def test_rounding_half_up():
    assert calculate_total([OrderItem(D("0.125"), 1)]) == D("0.13")


def test_full_discount_is_free():
    assert calculate_total([OrderItem(D("19.99"), 3)], Discount(D("100"))) == D("0.00")


@pytest.mark.parametrize("percent", [D("-1"), D("100.01")])
def test_invalid_discount_percent(percent):
    with pytest.raises(ValueError):
        validate_discount(Discount(percent))


def test_negative_min_subtotal_rejected():
    with pytest.raises(ValueError):
        calculate_total([OrderItem(D("1"), 1)], Discount(D("5"), D("-1")))


def test_negative_price_rejected():
    with pytest.raises(ValueError, match="price"):
        calculate_total([OrderItem(D("-0.01"), 1)])


@pytest.mark.parametrize("qty", [0, -3, 1.5, True])
def test_invalid_quantity_rejected(qty):
    with pytest.raises(ValueError, match="quantity"):
        calculate_total([OrderItem(D("1"), qty)])


def test_float_price_rejected():
    with pytest.raises(ValueError):
        calculate_total([OrderItem(1.1, 1)])


def test_empty_order_rejected():
    with pytest.raises(ValueError):
        calculate_total([])


def test_format_total():
    from sentinelpr_lab import format_total

    assert format_total(D("25.5")) == "USD 25.50"
    assert format_total(D("0"), currency="EUR") == "EUR 0.00"

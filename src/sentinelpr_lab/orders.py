"""Order total calculation with percentage discounts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


@dataclass(frozen=True)
class OrderItem:
    price: Decimal
    quantity: int


@dataclass(frozen=True)
class Discount:
    """A percentage discount, optionally gated on a minimum subtotal.

    The discount applies when the order subtotal is greater than or equal to
    ``min_subtotal`` (a subtotal exactly at the threshold qualifies).
    """

    percent: Decimal
    min_subtotal: Decimal = Decimal("0")


def _to_decimal(value, field: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field} must be an int, str or Decimal, not {type(value).__name__}")
    try:
        return Decimal(value)
    except Exception as exc:  # decimal.InvalidOperation, TypeError
        raise ValueError(f"{field} is not a valid number: {value!r}") from exc


def validate_discount(discount: Discount) -> None:
    """Raise ValueError unless the discount is well formed."""
    if not Decimal("0") <= discount.percent <= Decimal("100"):
        raise ValueError("discount percent must be between 0 and 100")
    if discount.min_subtotal < 0:
        raise ValueError("discount min_subtotal must not be negative")


def _validate_item(item: OrderItem) -> Decimal:
    price = _to_decimal(item.price, "price")
    if price < 0:
        raise ValueError("price must not be negative")
    if isinstance(item.quantity, bool) or not isinstance(item.quantity, int):
        raise ValueError("quantity must be an integer")
    if item.quantity < 1:
        raise ValueError("quantity must be at least 1")
    return price


def calculate_total(items: list[OrderItem], discount: Discount | None = None) -> Decimal:
    """Return the order total, rounded half-up to whole cents."""
    if not items:
        raise ValueError("order must contain at least one item")

    subtotal = sum((_validate_item(i) * i.quantity for i in items), Decimal("0"))

    if discount is not None:
        validate_discount(discount)
        if subtotal >= discount.min_subtotal:
            subtotal -= subtotal * discount.percent / Decimal("100")

    return subtotal.quantize(CENT, rounding=ROUND_HALF_UP)


def format_total(total: Decimal, currency: str = "USD") -> str:
    """Render a total for display, e.g. ``"USD 25.50"``."""
    return f"{currency} {total.quantize(CENT, rounding=ROUND_HALF_UP)}"

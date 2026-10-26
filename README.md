# sentinelpr-integration-lab

A tiny order/discount service (`sentinelpr_lab`) used as a controlled target for
testing the SentinelPR platform against real GitHub pull requests. No database,
network, or secrets are needed; tests are deterministic.

## Install

```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Test

```bash
python -m pytest -v
```

## Usage

```python
from decimal import Decimal
from sentinelpr_lab import Discount, OrderItem, calculate_total

items = [OrderItem(Decimal("40.00"), 2), OrderItem(Decimal("20.00"), 1)]
# 20% off orders with a subtotal of at least 100.00
print(calculate_total(items, Discount(Decimal("20"), min_subtotal=Decimal("100"))))  # 80.00
```

Rules: prices must be non-negative `int`/`str`/`Decimal` (no floats), quantities
integers >= 1, discount percent 0-100, and a discount with `min_subtotal`
applies when subtotal **>=** `min_subtotal`. Totals round half-up to cents.
Invalid input raises `ValueError`.

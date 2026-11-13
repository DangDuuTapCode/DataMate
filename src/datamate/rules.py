"""Small, auditable business-rule primitives. Add rules only with tests."""
from .normalise import fold


def valid_revenue_status(value):
    status = fold(value)
    return not any(word in status for word in ("huy", "tra hang", "hoan tra", "return"))


def cancelled_status(value):
    return "huy" in fold(value)

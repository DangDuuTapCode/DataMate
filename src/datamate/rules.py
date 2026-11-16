"""Small, auditable business-rule primitives. Add rules only with tests."""
from .normalise import fold


UNSUCCESSFUL_ORDER_STATUS_CLASSES = frozenset({"cancelled", "returned", "delivery_failed"})


def classify_order_status(value):
    """Classify only explicit order outcomes; return None when evidence is unclear."""
    status = fold(value)
    if not status:
        return None

    padded = f" {status} "
    if " cancel " in padded or status.startswith("cancel") or " huy " in padded:
        return "cancelled"
    if any(phrase in status for phrase in (
        "tra hang", "doi tra", "hoan tra", "hoan hang", "hang tra ve", "return", "returned",
    )):
        return "returned"
    if any(phrase in status for phrase in (
        "khong giao duoc", "giao that bai", "giao hang that bai",
        "giao khong thanh cong", "not delivered", "delivery failed", "failed delivery",
    )):
        return "delivery_failed"
    if any(phrase in status for phrase in (
        "dang van chuyen", "dang giao", "in transit", "shipping", "shipped", "out for delivery",
    )):
        return "in_transit"
    if any(phrase in status for phrase in (
        "cho xu ly", "dang xu ly", "cho xac nhan", "chua xac nhan", "cho giao",
        "dang chuan bi", "pending", "processing",
    )):
        return "pending"
    if status in {"xong", "ok", "success", "successful", "complete", "completed", "delivered", "da lay"} or any(
        phrase in status for phrase in ("thanh cong", "hoan thanh", "da giao", "da lay hang")
    ):
        return "successful"
    return None


def valid_revenue_status(value):
    status = fold(value)
    if classify_order_status(value) in UNSUCCESSFUL_ORDER_STATUS_CLASSES | {"pending", "in_transit"}:
        return False
    return not any(word in status for word in (
        "huy", "cancel", "tra hang", "hoan tra", "return", "khong giao duoc", "not delivered",
        "that bai", "failed", "dang van chuyen", "shipping", "in transit", "pending",
    ))


def cancelled_status(value):
    return classify_order_status(value) == "cancelled"

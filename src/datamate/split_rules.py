"""Small runtime reader for split-specific competition rulebook defaults.

Only rules the deterministic executor can actually apply are exposed here.
Unknown or missing clauses stay unsupported instead of silently falling back
to a training-split convention.
"""
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

from .normalise import fold


class RulebookError(ValueError):
    """The split rulebook is missing, unreadable, or lacks a required clause."""


@dataclass(frozen=True)
class SplitRules:
    revenue_supported: bool
    revenue_date_headers: tuple[str, ...]
    revenue_excluded_statuses: frozenset[str]
    revenue_included_statuses: frozenset[str]
    cancellation_numerator_statuses: frozenset[str]
    ranking_default: str | None
    tie_breaker: str | None
    tet_lunar_window: tuple[int, int, int, int, int, int] | None
    tet_preceding_comparison_supported: bool
    revenue_amount_basis: str | None = None
    revenue_period_basis: str | None = None
    collection_status_policy: str | None = None
    deduplicate_identical_order_lines: bool = False

    @classmethod
    def from_text(cls, text):
        rows, raw_rows = {}, {}
        for line in str(text).splitlines():
            if "|" not in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or not cells[0] or set(cells[0]) <= {"-", ":", " "}:
                continue
            key = fold(cells[0])
            rows[key] = fold(cells[1])
            raw_rows[key] = cells[1]

        def row(*names):
            return next((rows[name] for name in names if name in rows), "")

        def raw_row(*names):
            return next((raw_rows[name] for name in names if name in raw_rows), "")

        status_rule = row("don tinh vao doanh thu", "orders counted as revenue")
        amount_rule = row("doanh thu mot don", "revenue per order")
        date_rule = row("don thuoc ky nao", "order period date")
        rank_rule = row("ban chay", "best-selling")
        cancellation_rule = row("ti le don huy trong ky", "cancellation rate")
        tet_rule = row("tet nam y dip tet mua tet", "tet")
        collection_status_rule = row(
            "trang thai thanh toan duoc tinh la tien thuc thu",
            "giao dich thanh toan duoc tinh la tien thuc thu",
            "payment status counted as collected",
            "collected payment status policy",
        )
        tet_rule_symbols = "".join(
            character
            for character in unicodedata.normalize(
                "NFKD", raw_row("tet nam y dip tet mua tet", "tet").casefold()
            )
            if not unicodedata.combining(character)
        ).replace("−", "-").replace("–", "-").replace("—", "-")

        excluded = set()
        if any(term in status_rule for term in ("khong huy", "excluding cancelled", "excluding canceled")):
            excluded.add("cancelled")
        if any(term in status_rule for term in ("khong tra hang", "bo ca don", "excluding returned", "any returned item")):
            excluded.add("returned")
        # User-approved DataMate convention: failed delivery is distinct from
        # cancellation/return, but all three are unsuccessful for revenue.
        excluded.add("delivery_failed")
        if any(term in status_rule for term in ("giao that bai", "khong giao duoc", "excluding failed delivery")):
            excluded.add("delivery_failed")

        included = set()
        if any(term in status_rule for term in ("dang giao van tinh", "in-transit orders included", "in transit included")):
            included.add("in_transit")
        if any(term in status_rule for term in ("dang xu ly van tinh", "pending orders included")):
            included.add("pending")

        if "ngay dat" in date_rule or "order date" in date_rule:
            date_headers = ("ngay dat", "order date", "ngay tao don")
            period_basis = "order_date"
        elif "ngay giao" in date_rule or "delivery date" in date_rule:
            date_headers = ("ngay giao", "delivery date")
            period_basis = "delivery_date"
        elif "ngay ban" in date_rule or "sales date" in date_rule:
            date_headers = ("ngay ban", "sales date")
            period_basis = "sales_date"
        else:
            date_headers = ()
            period_basis = None

        cancellation_numerator = set()
        if "don huy" in cancellation_rule or "cancelled" in cancellation_rule or "canceled" in cancellation_rule:
            cancellation_numerator.add("cancelled")
        if any(term in cancellation_rule for term in ("don khong thanh cong", "unsuccessful orders")):
            if any(term in cancellation_rule for term in ("don tra", "returned")):
                cancellation_numerator.add("returned")
            if any(term in cancellation_rule for term in ("giao that bai", "khong giao duoc", "delivery failed")):
                cancellation_numerator.add("delivery_failed")
        if any(term in cancellation_rule for term in ("bao gom don tra", "returned orders count", "returned in numerator")):
            cancellation_numerator.add("returned")

        line_amount = any(term in amount_rule for term in (
            "thanh tien cac dong", "gia tri cac dong", "line amount", "line-level amount",
            "line amounts", "after line-level discounts",
        ))
        revenue_supported = bool(status_rule and line_amount and date_headers and excluded)
        amount_basis = "line_amount_after_line_discount" if line_amount else None

        collection_status_policy = None
        if (
            ("chi " in collection_status_rule or "only " in collection_status_rule)
            and (
                ("thanh toan" in collection_status_rule and "thanh cong" in collection_status_rule)
                or ("payment" in collection_status_rule and "successful" in collection_status_rule)
            )
        ):
            collection_status_policy = "successful_status_only"

        if "so luong" in rank_rule or "quantity" in rank_rule:
            ranking_default = "quantity"
        elif "doanh thu" in rank_rule or "revenue" in rank_rule or "amount" in rank_rule:
            ranking_default = "revenue"
        else:
            ranking_default = None

        whole = fold(text)
        deduplicate_identical_order_lines = (
            "hai dong cua cung mot don giong nhau o moi o" in whole
            and "loi xuat file tinh mot lan" in whole
        )
        if "theo ma tang dan" in whole or "by code ascending" in whole:
            tie_breaker = "code"
        elif "khong co ma thi theo ten" in whole or "without a code, by name" in whole:
            tie_breaker = "name"
        else:
            tie_breaker = None
        if tie_breaker == "code" and any(term in whole for term in ("khong co ma", "no code")):
            tie_breaker = "code_or_name"

        tet_start = re.search(
            r"\b(\d{1,2})\s+thang\s+chap\b.*?\bnam am(?: lich)? y\s*-\s*(\d+)\b",
            tet_rule_symbols,
        )
        tet_end = re.search(
            r"\bmung\s+(\d{1,2})\s+thang\s+gieng\b.*?\bnam am(?: lich)? y\b",
            tet_rule_symbols,
        )
        tet_window = None
        if tet_start and tet_end:
            tet_window = (
                int(tet_start.group(1)), 12, -int(tet_start.group(2)),
                int(tet_end.group(1)), 1, 0,
            )

        return cls(
            revenue_supported=revenue_supported,
            revenue_date_headers=date_headers,
            revenue_excluded_statuses=frozenset(excluded),
            revenue_included_statuses=frozenset(included),
            cancellation_numerator_statuses=frozenset(cancellation_numerator),
            ranking_default=ranking_default,
            tie_breaker=tie_breaker,
            tet_lunar_window=tet_window,
            tet_preceding_comparison_supported=bool(tet_window and "truoc tet" in tet_rule and "cung so ngay" in tet_rule),
            revenue_amount_basis=amount_basis,
            revenue_period_basis=period_basis,
            collection_status_policy=collection_status_policy,
            deduplicate_identical_order_lines=deduplicate_identical_order_lines,
        )

    @classmethod
    def read(cls, path):
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            raise RulebookError(f"cannot read split rulebook: {path.name}") from error
        rules = cls.from_text(text)
        if (not rules.revenue_supported or not rules.ranking_default or not rules.tie_breaker
                or not rules.cancellation_numerator_statuses):
            raise RulebookError("split rulebook lacks supported revenue or ranking defaults")
        return rules

    @classmethod
    def test_defaults(cls):
        """Competition defaults for in-process synthetic tests and API callers."""
        return cls(
            revenue_supported=True,
            revenue_date_headers=("ngay dat", "ngay ban", "ngay tao", "ngay"),
            revenue_excluded_statuses=frozenset({
                "cancelled", "returned", "delivery_failed", "in_transit",
            }),
            revenue_included_statuses=frozenset(),
            cancellation_numerator_statuses=frozenset({"cancelled"}),
            ranking_default="quantity",
            tie_breaker="code_or_name",
            tet_lunar_window=(23, 12, -1, 10, 1, 0),
            tet_preceding_comparison_supported=True,
            revenue_amount_basis="line_amount_after_line_discount",
            revenue_period_basis="order_date",
            collection_status_policy=None,
            deduplicate_identical_order_lines=True,
        )

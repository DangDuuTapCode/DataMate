import datetime as dt
import re
from decimal import Decimal, ROUND_HALF_UP

from .normalization import parse_date, parse_decimal
from .normalise import fold, tokens
from .rules import classify_order_status
from .split_rules import SplitRules
from .types import Table

DATE = ("ngay dat", "ngay ban", "ngay tao", "ngay lap", "ngay")
LINE_AMOUNT = (
    "thanh tien", "tien hang", "tien ban", "line amount", "line amounts",
    "line amount after discount", "sales amount", "amount",
)
COLLECTED_AMOUNT = ("gia tri", "so tien", "tien", "amount", "value", "payment amount")
COLLECTION_DATE = ("ngay thu", "ngay thanh toan", "thoi diem", "payment date", "date received", "paid at", "collection date")
QUANTITY = ("so luong", "so luong ban", "sl", "quantity", "quy ra dv le")
ORDER = (
    "ma don", "so don", "ma hoa don", "so hoa don", "so phieu", "ma chung tu",
    "ma giao dich", "order id", "invoice id", "ma gd",
)
STATUS = ("trang thai", "status")
SPECIFIC_ORDER_STATUS = (
    "trang thai don hang", "trang thai don", "tinh trang don hang", "tinh trang don",
    "trang thai xu ly", "ket qua", "ghi chu tt", "xu ly",
)
GENERIC_ORDER_STATUS = ("trang thai", "tinh trang", "status")
PRODUCT = ("ten hang", "ten san pham", "ten mat hang", "ten mon", "ten sp")
PRODUCT_EXACT = (*PRODUCT, "san pham", "hang hoa", "hang ban", "mat hang")


def _column(headers, choices):
    columns = [fold(x) for x in headers]
    for choice in choices:
        if choice in columns:
            return columns.index(choice)
    for choice in choices:
        for index, column in enumerate(columns):
            if choice in column:
                return index
    return None


def _exact_column(headers, choices):
    """Match a documented metric header exactly; avoid substring false positives."""
    columns = [fold(x) for x in headers]
    for choice in choices:
        if choice in columns:
            return columns.index(choice)
    return None


def _order_status_column(headers):
    """Match documented status headers exactly; never match customer/invoice status substrings."""
    columns = [fold(header) for header in headers]
    specific = [columns.index(name) for name in SPECIFIC_ORDER_STATUS if name in columns]
    if len(specific) == 1:
        return specific[0]
    if specific:
        return None
    generic = [columns.index(name) for name in GENERIC_ORDER_STATUS if name in columns]
    return generic[0] if len(generic) == 1 else None


def _product_column(headers):
    """Find a descriptive product label, never a date/code/category substring."""
    columns = [fold(header) for header in headers]
    for choice in PRODUCT_EXACT:
        if choice in columns:
            return columns.index(choice)
    for index, column in enumerate(columns):
        if any(marker in column.split() for marker in ("ma", "id", "code", "sku", "ngay", "date", "so")):
            continue
        if any(choice in column for choice in PRODUCT):
            return index
    return None


def _is_payment_table(table):
    role = fold(f"{table.name} {table.source}")
    return any(term in role for term in ("thanh toan", "phieu thu", "payment", "receipt"))


def _is_inventory_table(table):
    role = fold(f"{table.name} {table.source}")
    return any(term in role for term in ("the kho", "ton kho", "inventory", "stock ledger"))


def _is_delivery_table(table):
    role = fold(f"{table.name} {table.source}")
    return any(term in role for term in ("phieu giao", "giao hang", "delivery", "shipping"))


def _is_order_table(table):
    role = fold(f"{table.name} {table.source}")
    words = set(role.split())
    return bool(words & {"hoadon", "invoice", "order", "donhang"}) and not bool(
        words & {"chitiethoadon", "orderline", "orderlines", "detail"}
    )


def _product_key_column(headers):
    for index, header in enumerate(headers):
        words = set(fold(header).split())
        if words & {"sku", "code"} or ("ma" in words and words & {"hang", "hh", "sp", "san", "pham"}):
            return index
    return None


def _decimal(value, decimal_separator=None):
    result = parse_decimal(value, decimal_separator=decimal_separator)
    return result.value if result.ok else None


def _column_decimal_separator(table, column_index):
    """Infer a thousands separator only when the entire source column agrees.

    Competition money exports may store VND values as strings such as
    ``82,500``. A single value is ambiguous, so never infer from one cell:
    inspect the whole column and enable grouping only when every
    separator-bearing string uses the same valid three-digit grouping.
    Mixed or malformed conventions remain fail-closed.
    """
    grouping = None
    saw_grouped_value = False
    grouped_pattern = re.compile(r"^[+-]?\d{1,3}([,.])\d{3}(?:\1\d{3})*$")
    for row in table.rows:
        if column_index >= len(row):
            return None
        value = row[column_index]
        if value is None or isinstance(value, (int, float, Decimal)):
            continue
        text = str(value).strip()
        if not text:
            continue
        if not any(separator in text for separator in (",", ".")):
            # Plain integer strings do not contribute locale evidence.
            if not parse_decimal(value).ok:
                return None
            continue
        match = grouped_pattern.fullmatch(text)
        if not match:
            return None
        separator = match.group(1)
        if grouping is not None and grouping != separator:
            return None
        grouping = separator
        saw_grouped_value = True
    if not saw_grouped_value:
        return None
    # parse_decimal's policy names the decimal separator; the other
    # punctuation is then accepted only as valid thousands grouping.
    return "." if grouping == "," else ","


def _date(value, date_system=None):
    # Vietnamese dates in the current competition data are day-first. The
    # general parser itself remains strict unless a caller supplies a policy.
    result = parse_date(value, day_first=True, excel_date_system=date_system)
    return result.value if result.ok else None


def _money(value):
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class Executor:
    """Allowlist executor. Incomplete or ambiguous evidence returns None."""
    def __init__(self, tables, rules=None):
        self.tables = tables
        self.rules = rules or SplitRules.test_defaults()

    def _revenue_fact(self):
        candidates = self._revenue_candidates()
        return candidates[0] if len(candidates) == 1 else None

    def _revenue_candidates(self):
        if not self.rules.revenue_supported:
            return []
        candidates = []
        for table in self.tables:
            if _is_payment_table(table) or _is_inventory_table(table) or _is_delivery_table(table):
                continue
            date = _exact_column(table.headers, self.rules.revenue_date_headers)
            value = _exact_column(table.headers, LINE_AMOUNT)
            product = _product_column(table.headers)
            product_key = _product_key_column(table.headers)
            # A line amount must have line-level identity; order totals such as
            # `Tổng đơn` and `Phải thu` never enter this allowlist.
            if date is not None and value is not None and (product is not None or product_key is not None):
                candidates.append((table, date, value, product, _order_status_column(table.headers), _column(table.headers, ORDER)))
        return candidates

    @staticmethod
    def _join_key(value):
        if value is None or not str(value).strip():
            return None
        if isinstance(value, (int, float)):
            try:
                numeric = float(value)
                if numeric.is_integer():
                    return str(int(numeric))
            except (OverflowError, ValueError):
                pass
        return str(value).strip().casefold()

    def _daily_revenue_fact(self):
        """Find direct line facts or one complete, one-to-many invoice join."""
        if not self.rules.revenue_supported:
            return None
        direct = self._revenue_candidates()
        if len(direct) == 1:
            table, date_col, value_col, _, status_col, _ = direct[0]
            return table, date_col, value_col, status_col, [table.name]
        if direct:
            return None

        line_candidates = []
        for table in self.tables:
            if _is_payment_table(table) or _is_inventory_table(table) or _is_delivery_table(table) or _is_order_table(table):
                continue
            value_col = _exact_column(table.headers, LINE_AMOUNT)
            line_key_col = _column(table.headers, ORDER)
            has_item_identity = _product_column(table.headers) is not None or _product_key_column(table.headers) is not None
            if value_col is not None and line_key_col is not None and has_item_identity:
                line_candidates.append((table, value_col, line_key_col))
        if len(line_candidates) != 1:
            return None

        order_candidates = []
        order_date_rule = any(
            header in {"ngay dat", "order date", "ngay tao don"}
            for header in self.rules.revenue_date_headers
        )
        for table in self.tables:
            if not _is_order_table(table):
                continue
            order_key_col = _column(table.headers, ORDER)
            date_choices = self.rules.revenue_date_headers
            if order_date_rule:
                # "Ngày bán" is accepted as the order date only in a table
                # whose role and unique invoice key are validated below.
                date_choices = (*date_choices, "ngay ban")
            date_col = _exact_column(table.headers, date_choices)
            status_col = _order_status_column(table.headers)
            if None not in (order_key_col, date_col, status_col):
                order_candidates.append((table, order_key_col, date_col, status_col))
        if len(order_candidates) != 1:
            return None

        line_table, value_col, line_key_col = line_candidates[0]
        order_table, order_key_col, date_col, status_col = order_candidates[0]
        order_rows = {}
        for row in order_table.rows:
            if not any(value is not None and str(value).strip() for value in row):
                continue
            key = self._join_key(row[order_key_col])
            if key is None or key in order_rows:
                return None
            order_rows[key] = (row[date_col], row[status_col])
        if not order_rows:
            return None

        joined_rows, seen_line_rows = [], set()
        for row in line_table.rows:
            if not any(value is not None and str(value).strip() for value in row):
                continue
            key = self._join_key(row[line_key_col])
            if key is None or key not in order_rows:
                return None
            row_key = tuple((type(value).__name__, repr(value)) for value in row)
            if row_key in seen_line_rows:
                continue
            seen_line_rows.add(row_key)
            order_date, order_status = order_rows[key]
            joined_rows.append([order_date, order_status, row[value_col]])
        if not joined_rows:
            return None

        joined = Table(
            name=f"{line_table.name}+{order_table.name}",
            headers=["Ngày đặt", "Trạng thái đơn hàng", "Thành tiền"],
            rows=joined_rows,
            source=f"{line_table.source}+{order_table.source}",
            date_system=order_table.date_system,
        )
        return joined, 0, 2, 1, [line_table.name, order_table.name]

    def _fact(self, metric, product=False, exclude_payments=False, exclude_inventory=False, exclude_delivery=False):
        candidates = []
        for table in self.tables:
            if (exclude_payments and _is_payment_table(table)) or (exclude_inventory and _is_inventory_table(table)):
                continue
            if exclude_delivery and _is_delivery_table(table):
                continue
            date = _column(table.headers, DATE)
            value = _column(table.headers, metric) if metric is not None else None
            prod = _product_column(table.headers)
            if date is not None and (metric is None or value is not None) and (not product or prod is not None):
                candidates.append((table, date, value, prod, _order_status_column(table.headers), _column(table.headers, ORDER)))
        return candidates[0] if len(candidates) == 1 else None

    def _collection_fact(self):
        """Find one explicit payment-event source, using receipt time and value."""
        candidates = []
        for table in self.tables:
            if not _is_payment_table(table):
                continue
            date = _exact_column(table.headers, COLLECTION_DATE)
            value = _exact_column(table.headers, COLLECTED_AMOUNT)
            if date is not None and value is not None:
                candidates.append((table, date, value, _column(table.headers, STATUS)))
        return candidates[0] if len(candidates) == 1 else None

    def _period(self, table, date_column, start, end, status_column=None, accepted_only=True):
        matched = []
        for row in table.rows:
            if not any(value is not None and str(value).strip() for value in row):
                continue
            day = _date(row[date_column], table.date_system)
            if day is None:
                return None
            if not start <= day <= end:
                continue
            if accepted_only and status_column is not None:
                status_class = classify_order_status(row[status_column])
                if status_class in self.rules.revenue_excluded_statuses:
                    continue
                if status_class in self.rules.revenue_included_statuses or status_class == "successful":
                    pass
                elif status_class in {"pending", "in_transit"}:
                    return None
                else:
                    return None
            matched.append(row)
        return matched

    def execute(self, plan, question):
        start, end = dt.date.fromisoformat(plan.start), dt.date.fromisoformat(plan.end)
        if plan.intent == "daily_revenue_threshold_count":
            fact = self._daily_revenue_fact()
            if not fact or plan.threshold is None:
                return None
            try:
                threshold = Decimal(plan.threshold)
            except Exception:
                return None
            if not threshold.is_finite() or threshold <= 0:
                return None
            table, date_col, value_col, status_col, evidence = fact
            rows = self._period(table, date_col, start, end, status_col)
            if rows is None or not rows:
                return None
            daily_totals = {}
            decimal_separator = _column_decimal_separator(table, value_col)
            for row in rows:
                day = _date(row[date_col], table.date_system)
                value = _decimal(row[value_col], decimal_separator)
                if day is None or value is None:
                    return None
                daily_totals[day] = daily_totals.get(day, Decimal(0)) + value
            answer = sum(total >= threshold for total in daily_totals.values())
            return {"type": "number", "answer": answer, "evidence": evidence}
        if plan.intent in ("revenue", "collected_amount", "quantity"):
            if plan.intent == "collected_amount":
                fact = self._collection_fact()
            elif plan.intent == "revenue":
                fact = self._revenue_fact()
            else:
                fact = self._fact(
                    QUANTITY,
                )
            if not fact:
                return None
            if plan.intent == "collected_amount":
                table, date_col, value_col, status_col = fact
                product_col = None
            else:
                table, date_col, value_col, product_col, status_col, _ = fact
            rows = self._period(
                table, date_col, start, end, status_col,
                accepted_only=plan.intent != "collected_amount",
            )
            if rows is None or not rows:
                return None
            if plan.intent == "collected_amount" and status_col is not None:
                settled = []
                nonsettled = {"cancelled", "returned", "delivery_failed", "pending", "in_transit"}
                for row in rows:
                    status_class = classify_order_status(row[status_col])
                    if status_class == "successful":
                        settled.append(row)
                    elif status_class in nonsettled:
                        continue
                    else:
                        return None
                rows = settled
                if not rows:
                    return None
            if product_col is not None:
                qwords = tokens(question)
                names = sorted({str(r[product_col]).strip() for r in rows if str(r[product_col]).strip()}, key=len, reverse=True)
                target = next((x for x in names if len(tokens(x)) > 1 and tokens(x).issubset(qwords)), None)
                if target:
                    rows = [r for r in rows if str(r[product_col]).strip() == target]
            decimal_separator = _column_decimal_separator(table, value_col)
            values = [_decimal(row[value_col], decimal_separator) for row in rows]
            if any(value is None for value in values):
                return None
            total = sum(values, Decimal(0))
            answer = _money(total) if plan.intent == "revenue" else float(total.quantize(Decimal("0.01")))
            return {"type": "number", "answer": int(answer) if isinstance(answer, float) and answer.is_integer() else answer, "evidence": [table.name]}
        if plan.intent == "order_count":
            fact = self._fact(None, exclude_payments=True, exclude_delivery=True)
            if not fact or fact[5] is None:
                return None
            table, date_col, _, _, status_col, order_col = fact
            rows = self._period(table, date_col, start, end, status_col)
            if rows is None or not rows:
                return None
            ids = {str(r[order_col]).strip() for r in rows}
            if "" in ids:
                return None
            return {"type": "number", "answer": len(ids), "evidence": [table.name]}
        if plan.intent == "cancellation_rate":
            options = []
            for table in self.tables:
                if _is_payment_table(table):
                    continue
                date_col, status_col, order_col = _column(table.headers, DATE), _order_status_column(table.headers), _column(table.headers, ORDER)
                if None not in (date_col, status_col, order_col):
                    options.append((table, date_col, status_col, order_col))
            if not options:
                return None
            if len(options) != 1:
                return None
            table, date_col, status_col, order_col = options[0]
            rows = self._period(table, date_col, start, end, accepted_only=False)
            if rows is None or not rows:
                return None
            orders = {}
            for row in rows:
                order_id, status = str(row[order_col]).strip(), row[status_col]
                if not order_id or order_id.casefold() in {"none", "null", "nan"}:
                    return None
                status_class = classify_order_status(status)
                if status_class is None:
                    return None
                if order_id in orders and orders[order_id] != status_class:
                    return None
                orders[order_id] = status_class
            rate = Decimal(sum(v in self.rules.cancellation_numerator_statuses for v in orders.values())) * 100 / len(orders)
            return {"type": "percent", "answer": float(rate.quantize(Decimal("0.01"))), "evidence": [table.name]}
        if plan.intent == "sales_ranking":
            q = fold(question)
            explicit_revenue = any(term in q for term in (
                "doanh thu", "doanh so", "tien ban", "nhieu tien", "gia tri", "amount", "revenue",
            ))
            explicit_quantity = any(term in q for term in (
                "so luong", "ban chay", "ban nhieu", "hot nhat", "quantity",
            ))
            rank_metric = "revenue" if explicit_revenue else "quantity" if explicit_quantity else self.rules.ranking_default
            if rank_metric == "revenue":
                fact = self._revenue_fact()
            elif rank_metric == "quantity":
                fact = self._fact(QUANTITY, product=True, exclude_inventory=True)
            else:
                fact = None
            if not fact:
                return None
            table, date_col, value_col, product_col, status_col, _ = fact
            product_key_col = _product_key_column(table.headers)
            if self.rules.tie_breaker == "code" and product_key_col is None:
                return None
            totals, display_names = {}, {}
            rows = self._period(table, date_col, start, end, status_col)
            if rows is None or not rows:
                return None
            decimal_separator = _column_decimal_separator(table, value_col)
            for row in rows:
                name = str(row[product_col]).strip() if product_col is not None else ""
                code = str(row[product_key_col]).strip() if product_key_col is not None else ""
                value = _decimal(row[value_col], decimal_separator)
                if (not name and not code) or (product_key_col is not None and not code) or value is None:
                    return None
                if name and fold(name) != "phi phuc vu":
                    key = code if product_key_col is not None else name
                    totals[key] = totals.get(key, Decimal(0)) + value
                    display_names.setdefault(key, name or code)
            if not totals:
                return None
            def tie_key(key):
                if self.rules.tie_breaker in ("code", "code_or_name") and product_key_col is not None:
                    return fold(key)
                return fold(display_names[key])
            ranked = sorted(totals, key=lambda key: (-totals[key], tie_key(key)))[:plan.top_k]
            names = [display_names[key] for key in ranked]
            return {"type": "string", "answer": names[0], "evidence": [table.name]} if plan.top_k == 1 else {"type": "list", "answer": names, "evidence": [table.name]}
        return None

    def execute_with_reason(self, plan, question, *, spec=None):
        """Run the allowlisted executor and return an internal abstention reason."""
        if plan is None:
            return None, "unsupported_intent"
        if plan.intent == "revenue" and not self.rules.revenue_supported:
            return None, "rulebook_unavailable"
        if spec is not None and spec.unit and plan.intent in ("revenue", "collected_amount") and fold(spec.unit) != "vnd":
            return None, "invalid_unit"
        if spec is not None and spec.unit and plan.intent in ("quantity", "sales_ranking"):
            metric = QUANTITY
            fact = self._fact(
                metric,
                product=plan.intent == "sales_ranking",
                exclude_inventory=plan.intent == "sales_ranking",
            )
            if fact:
                table, date_col, _, _, status_col, _ = fact
                unit_column = _column(table.headers, ("don vi tinh", "dvt", "unit"))
                if unit_column is None:
                    return None, "invalid_unit"
                rows = self._period(
                    table, date_col, dt.date.fromisoformat(plan.start),
                    dt.date.fromisoformat(plan.end), status_col,
                )
                wanted = fold(spec.unit)
                if rows is not None and rows and any(fold(row[unit_column]) != wanted for row in rows):
                    return None, "invalid_unit"

        candidate = self.execute(plan, question)
        if candidate is not None:
            return candidate, None
        return None, self._failure_reason(plan)

    def _failure_reason(self, plan):
        intent = plan.intent
        if intent in ("revenue", "quantity"):
            if intent == "revenue":
                if not self.rules.revenue_supported:
                    return "rulebook_unavailable"
                revenue_fact = self._revenue_fact()
                if not revenue_fact:
                    return "missing_column"
                table, date_col, *_ = revenue_fact
                return "no_data" if self._no_data_in_period(plan, table, date_col) else "insufficient_evidence"
            metric = QUANTITY
            candidates = []
            for table in self.tables:
                date_col, value_col = _column(table.headers, DATE), _column(table.headers, metric)
                if date_col is not None and value_col is not None:
                    candidates.append((table, date_col))
            if not candidates:
                return "missing_column"
            if len(candidates) == 1 and self._no_data_in_period(plan, *candidates[0]):
                return "no_data"
            return "insufficient_evidence"
        if intent == "daily_revenue_threshold_count":
            if not self.rules.revenue_supported:
                return "rulebook_unavailable"
            fact = self._daily_revenue_fact()
            if not fact:
                return "missing_column"
            table, date_col, *_ = fact
            return "no_data" if self._no_data_in_period(plan, table, date_col) else "insufficient_evidence"
        if intent == "collected_amount":
            candidates = [
                (table, _exact_column(table.headers, COLLECTION_DATE)) for table in self.tables
                if _is_payment_table(table)
                and _exact_column(table.headers, COLLECTION_DATE) is not None
                and _exact_column(table.headers, COLLECTED_AMOUNT) is not None
            ]
            if not candidates:
                return "missing_column"
            if len(candidates) == 1 and self._no_data_in_period(plan, *candidates[0]):
                return "no_data"
            return "insufficient_evidence"
        if intent == "order_count":
            candidates = [
                (table, _column(table.headers, DATE)) for table in self.tables
                if not _is_payment_table(table) and not _is_delivery_table(table)
                and _column(table.headers, DATE) is not None
                and _column(table.headers, ORDER) is not None
            ]
            if not candidates:
                return "missing_column"
            if len(candidates) == 1 and self._no_data_in_period(plan, *candidates[0]):
                return "no_data"
            return "insufficient_evidence"
        if intent == "cancellation_rate":
            return self._cancellation_rate_failure_reason(plan)
        if intent == "sales_ranking":
            candidates = [
                (table, _column(table.headers, DATE)) for table in self.tables
                if not _is_inventory_table(table)
                and _column(table.headers, DATE) is not None
                and _column(table.headers, QUANTITY) is not None
            ]
            if not candidates:
                return "missing_column"
            product_candidates = [
                (table, date_col) for table, date_col in candidates
                if _product_column(table.headers) is not None
            ]
            if len(product_candidates) == 1 and self._no_data_in_period(plan, *product_candidates[0]):
                return "no_data"
            if not product_candidates:
                if any(_product_key_column(table.headers) is not None for table, _ in candidates):
                    return "join_unsafe"
                return "join_unsafe" if any(_is_inventory_table(table) for table in self.tables) else "missing_column"
            return "insufficient_evidence"
        return "insufficient_evidence"

    def _no_data_in_period(self, plan, table, date_column):
        rows = self._period(
            table, date_column, dt.date.fromisoformat(plan.start),
            dt.date.fromisoformat(plan.end), accepted_only=False,
        )
        return rows == []

    def _cancellation_rate_failure_reason(self, plan):
        candidates = []
        for table in self.tables:
            if _is_payment_table(table):
                continue
            date_col = _column(table.headers, DATE)
            status_col = _order_status_column(table.headers)
            order_col = _column(table.headers, ORDER)
            if None not in (date_col, status_col, order_col):
                candidates.append((table, date_col, status_col, order_col))
        if not candidates:
            return "missing_column"
        if len(candidates) != 1:
            return "insufficient_evidence"

        table, date_col, status_col, order_col = candidates[0]
        rows = self._period(
            table, date_col, dt.date.fromisoformat(plan.start),
            dt.date.fromisoformat(plan.end), accepted_only=False,
        )
        if rows is None:
            return "insufficient_evidence"
        if not rows:
            return "no_data"

        order_statuses = {}
        missing_status = unknown_status = conflicting_status = False
        for row in rows:
            status = row[status_col]
            status_class = classify_order_status(status)
            if status_class is None:
                if status is None or not str(status).strip():
                    missing_status = True
                else:
                    unknown_status = True
                continue
            order_id = str(row[order_col]).strip()
            if not order_id or order_id.casefold() in {"none", "null", "nan"}:
                continue
            if order_id in order_statuses and order_statuses[order_id] != status_class:
                conflicting_status = True
            order_statuses[order_id] = status_class

        if missing_status:
            return "missing_order_status"
        if unknown_status:
            return "unknown_order_status"
        if conflicting_status:
            return "conflicting_order_status"
        return "insufficient_evidence"

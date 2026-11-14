import datetime as dt
from decimal import Decimal, ROUND_HALF_UP

from .normalization import parse_date, parse_decimal
from .normalise import fold, tokens
from .rules import cancelled_status, valid_revenue_status

DATE = ("ngay dat", "ngay ban", "ngay tao", "ngay lap", "ngay")
AMOUNT = ("thanh tien", "tien hang", "doanh thu", "tong tien", "gia tri", "tien")
QUANTITY = ("so luong", "so luong ban", "sl", "quantity", "quy ra dv le")
ORDER = ("ma don", "so don", "ma hoa don", "so hoa don", "so phieu", "don")
STATUS = ("trang thai", "tinh trang")
PRODUCT = ("ten hang", "ten san pham", "san pham", "hang hoa", "mat hang", "ten mon", "hang")


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


def _decimal(value):
    result = parse_decimal(value)
    return result.value if result.ok else None


def _date(value):
    # Vietnamese dates in the current competition data are day-first. The
    # general parser itself remains strict unless a caller supplies a policy.
    result = parse_date(value, day_first=True)
    return result.value if result.ok else None


def _money(value):
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class Executor:
    """Allowlist executor. Ambiguous schemas return None (caller must abstain)."""
    def __init__(self, tables):
        self.tables = tables

    def _fact(self, metric, product=False):
        candidates = []
        for table in self.tables:
            date, value = _column(table.headers, DATE), _column(table.headers, metric)
            prod = _column(table.headers, PRODUCT)
            if date is not None and value is not None and (not product or prod is not None):
                candidates.append((table, date, value, prod, _column(table.headers, STATUS), _column(table.headers, ORDER)))
        return max(candidates, key=lambda item: (len(item[0].rows), item[0].name)) if candidates else None

    @staticmethod
    def _period(table, date_column, start, end, status_column=None, accepted_only=True):
        for row in table.rows:
            day = _date(row[date_column])
            if not day or not start <= day <= end:
                continue
            if accepted_only and status_column is not None and not valid_revenue_status(row[status_column]):
                continue
            yield row

    def execute(self, plan, question):
        start, end = dt.date.fromisoformat(plan.start), dt.date.fromisoformat(plan.end)
        if plan.intent in ("revenue", "quantity"):
            fact = self._fact(AMOUNT if plan.intent == "revenue" else QUANTITY)
            if not fact:
                return None
            table, date_col, value_col, product_col, status_col, _ = fact
            rows = list(self._period(table, date_col, start, end, status_col))
            if product_col is not None:
                qwords = tokens(question)
                names = sorted({str(r[product_col]).strip() for r in rows if str(r[product_col]).strip()}, key=len, reverse=True)
                target = next((x for x in names if len(tokens(x)) > 1 and tokens(x).issubset(qwords)), None)
                if target:
                    rows = [r for r in rows if str(r[product_col]).strip() == target]
            values = [_decimal(row[value_col]) for row in rows]
            values = [value for value in values if value is not None]
            if not values:
                return {"type": "number", "answer": 0, "evidence": [table.name]}
            total = sum(values, Decimal(0))
            answer = _money(total) if plan.intent == "revenue" else float(total.quantize(Decimal("0.01")))
            return {"type": "number", "answer": int(answer) if isinstance(answer, float) and answer.is_integer() else answer, "evidence": [table.name]}
        if plan.intent == "order_count":
            fact = self._fact(AMOUNT)
            if not fact or fact[5] is None:
                return None
            table, date_col, _, _, status_col, order_col = fact
            ids = {str(r[order_col]).strip() for r in self._period(table, date_col, start, end, status_col) if str(r[order_col]).strip()}
            return {"type": "number", "answer": len(ids), "evidence": [table.name]}
        if plan.intent == "cancellation_rate":
            options = []
            for table in self.tables:
                date_col, status_col, order_col = _column(table.headers, DATE), _column(table.headers, STATUS), _column(table.headers, ORDER)
                if None not in (date_col, status_col, order_col):
                    options.append((table, date_col, status_col, order_col))
            if not options:
                return None
            table, date_col, status_col, order_col = max(options, key=lambda item: (len(item[0].rows), item[0].name))
            orders = {str(r[order_col]).strip(): r[status_col] for r in self._period(table, date_col, start, end, accepted_only=False) if str(r[order_col]).strip()}
            rate = Decimal(0) if not orders else (Decimal(sum(cancelled_status(v) for v in orders.values())) * 100 / len(orders))
            return {"type": "percent", "answer": float(rate.quantize(Decimal("0.01"))), "evidence": [table.name]}
        if plan.intent == "sales_ranking":
            fact = self._fact(QUANTITY, product=True)
            if not fact:
                return None
            table, date_col, value_col, product_col, status_col, _ = fact
            totals = {}
            for row in self._period(table, date_col, start, end, status_col):
                name, value = str(row[product_col]).strip(), _decimal(row[value_col])
                if name and value is not None and fold(name) != "phi phuc vu":
                    totals[name] = totals.get(name, Decimal(0)) + value
            if not totals:
                return None
            ranked = sorted(totals, key=lambda name: (-totals[name], fold(name)))[:plan.top_k]
            return {"type": "string", "answer": ranked[0], "evidence": [table.name]} if plan.top_k == 1 else {"type": "list", "answer": ranked, "evidence": [table.name]}
        return None

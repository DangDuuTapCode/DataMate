"""Deterministic planner plus a strict extension point for a local SLM/LLM."""
import json
import re
from typing import Protocol

from .normalise import fold
from .timeparse import resolve
from .types import QueryPlan


class Planner(Protocol):
    def plan(self, question, as_of_date) -> QueryPlan | None: ...


class RulePlanner:
    """Safe fallback. It creates only plans which the executor explicitly supports."""
    def plan(self, question, as_of_date):
        window = resolve(question, as_of_date)
        if not window:
            return None
        q = fold(question)
        if "ti le" in q and "don huy" in q:
            intent = "cancellation_rate"
        elif any(x in q for x in ("ban chay", "hot nhat", "ban nhieu nhat")):
            intent = "sales_ranking"
        elif "doanh thu" in q or "dthu" in q or ("bao nhieu tien" in q and "no" not in q and "nhap" not in q):
            intent = "revenue"
        elif re.search(r"(so|bao nhieu) don", q) and "huy" not in q:
            intent = "order_count"
        elif "bao nhieu" in q and any(x in q for x in ("so luong", "ban duoc", " bao nhieu ly", " bao nhieu chai", " bao nhieu kg", " bao nhieu vien")):
            intent = "quantity"
        else:
            return None
        top = re.search(r"(?:top )?(\d+)", q)
        return QueryPlan(intent, *window, 0.75, top_k=int(top.group(1)) if top else 1, evidence=("rule-planner",))


class JsonPlanAdapter:
    """Validates a locally generated SLM plan; it never calls a network API."""
    ALLOWED = {"revenue", "quantity", "order_count", "cancellation_rate", "sales_ranking"}

    def parse(self, payload):
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
            if set(data) - {"intent", "start", "end", "confidence", "entity", "top_k", "evidence"}:
                return None
            if data["intent"] not in self.ALLOWED or not 0 <= float(data["confidence"]) <= 1:
                return None
            return QueryPlan(**data)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

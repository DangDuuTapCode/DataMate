"""Deterministic question understanding and a strict local-SLM extension point."""
import json
import re
from typing import Protocol

from .normalise import fold
from .timeparse import resolve, resolve_as_of, resolve_comparison
from .types import QueryPlan, QuerySpec, SortSpec, TemporalScope


class Planner(Protocol):
    def plan(self, question, as_of_date) -> QueryPlan | None: ...


class RulePlanner:
    """Parse broad query intent; only emit executable plans from the allowlist."""

    EXECUTABLE = {"revenue", "quantity", "order_count", "cancellation_rate", "sales_ranking"}
    RANKING_INTENTS = {
        "sales_ranking", "customer_ranking", "debt_ranking", "period_ranking",
        "seller_ranking", "supplier_ranking", "best_sales_day", "profit_ranking", "slow_sellers",
    }

    @staticmethod
    def _top_k(question):
        q = fold(question)
        match = re.search(r"\btop\s+(\d+)\b", q)
        if not match:
            match = re.search(r"\b(\d+)\s+(?:khach|khach hang|mat hang|san pham|sp|mon hang)\b", q)
        if not match:
            return 1
        try:
            value = int(match.group(1))
        except ValueError:
            return 1
        return value if 1 <= value <= 100 else 1

    @staticmethod
    def _explicit_unit(question):
        """Normalize a unit only when the question states it explicitly."""
        q = fold(question)
        if "%" in str(question) or re.search(r"\b(phan tram|ti le|ty le|ti trong|ty trong)\b", q):
            return "percent"
        if re.search(r"(?:\d[\d.,]*\s*)?(?:vnd|vnđ|đồng|đ)(?:\b|$)", str(question), re.IGNORECASE):
            return "VND"
        units = (
            ("kilogram", "kg"), ("gram", "g"), ("lit", "L"), ("ml", "mL"),
            ("chai", "chai"), ("ly", "ly"), ("coc", "cốc"), ("lon", "lon"),
            ("hop", "hộp"), ("vien", "viên"), ("cai", "cái"), ("dia", "đĩa"),
            ("to", "tô"), ("thung", "thùng"), ("loc", "lốc"), ("binh", "bình"),
            ("goi", "gói"), ("cuon", "cuộn"), ("tuyp", "tuýp"),
        )
        requested_unit = re.search(
            r"\b(?:mot|moi|tung)\s+(" + "|".join(re.escape(token) for token, _ in units) + r")\b",
            q,
        )
        if requested_unit:
            for token, canonical in units:
                if requested_unit.group(1) == token:
                    return canonical
        for token, canonical in units:
            if re.search(rf"\b{re.escape(token)}\b", q):
                return canonical
        if re.search(r"\bkg\b", q):
            return "kg"
        if re.search(r"\bml\b", q):
            return "mL"
        if re.search(r"\bl\b", q):
            return "L"
        return None

    @staticmethod
    def _resolve_entity(question, entity_catalog):
        """Resolve only unique aliases supplied by a business profile."""
        if not entity_catalog:
            return None, False
        folded_question = fold(question)
        matches = set()
        for canonical, aliases in entity_catalog.items():
            if isinstance(aliases, str):
                aliases = (aliases,)
            for alias in aliases:
                folded_alias = fold(alias)
                if folded_alias and re.search(
                    rf"(?<![a-z0-9]){re.escape(folded_alias)}(?![a-z0-9])", folded_question
                ):
                    matches.add(canonical)
                    break
        if len(matches) == 1:
            return next(iter(matches)), False
        return None, len(matches) > 1

    @staticmethod
    def _intent(question):
        q = fold(question)
        has_percent_mark = "%" in str(question)
        canceled = any(term in q for term in ("huy", "don huy", "bi huy", "hoan don"))
        comparison = any(term in q for term in (
            "so voi", "vs", "thay doi", "tang hay giam", "tang giam", "hon hay kem", "cung ky", "thang lien truoc",
        ))
        tokens = set(q.split())
        customer = (
            any(term in q for term in ("khach", "khach hang", "ai mua", "ai la nguoi mua"))
            or "kh" in tokens
        )
        product = (
            any(term in q for term in ("mat hang", "san pham", "hang hoa", "ten hang"))
            or "sp" in tokens
            or ("hang" in tokens and "cua hang" not in q)
        )
        ranking = any(term in q for term in (
            "top", "ban chay", "chay nhat", "ban nhieu nhat", "nhieu tien nhat", "mua nhieu nhat",
            "nhiu tien nhat", "chi tieu nhieu nhat", "chi tieu cao nhat", "cao nhat", "lon nhat",
            "dat nhat", "loi nhat", "nhieu don nhat", "nhieu don hang nhat", "nhiu don hang nhat", "nhieu nhat", "hot nhat",
        ))

        debt = any(term in q for term in ("cong no", "con no", "dang no", "khach no", "ghi no", "mua chiu"))
        debt_payment = any(term in q for term in (
            "tra no", "tra bot no", "khach thanh toan", "khach tra tien", "thu tien no", "thu hoi",
        ))

        if canceled and (has_percent_mark or any(term in q for term in ("ti le", "ty le", "phan tram", "bao nhieu phan tram"))):
            return "cancellation_rate", (), "cancellation_rate"
        if any(term in q for term in ("nen uong", "uong moi lan", "lieu dung", "nen dung thuoc")):
            return "medical_advice", (), "medical_advice"
        if canceled and any(term in q for term in ("so don", "may don", "bao nhieu don", "dem don", "bao nhiu don")):
            return "cancellation_count", (), "cancellation_count"
        if any(term in q for term in ("no them", "ghi no them")) and any(term in q for term in ("tra duoc", "tra no", "da tra")):
            return "debt_ledger_change", (), "debt_ledger_change"
        if debt and ranking and customer:
            return "debt_ranking", ("customer",), "debt_outstanding"
        if debt and customer and "so khach" in q:
            return "indebted_customer_count", ("customer",), "indebted_customer_count"
        if debt_payment:
            return "debt_payment", (), "debt_payment"
        if debt:
            return "debt_outstanding", (), "debt_outstanding"
        if ranking and customer:
            return "customer_ranking", ("customer",), "customer_spend"
        customer_order_frequency = any(term in q for term in (
            "mua it nhat", "mua toi thieu", "mua tu", "don tro len", "don khac nhau",
        ))
        percent_query = has_percent_mark or any(term in q for term in ("ti le", "ty le", "phan tram"))
        if customer and customer_order_frequency and percent_query:
            return "customer_repeat_rate", ("customer",), "customer_repeat_rate"
        if customer and customer_order_frequency:
            return "customer_order_count", ("customer",), "customer_order_count"
        if customer and "don" in tokens and any(term in q for term in ("so khach", "dem so khach", "dem khach")):
            return "customer_order_count", ("customer",), "customer_order_count"
        if ranking and "thang nao" in q and any(term in q for term in ("doanh thu", "doanh so", "ban duoc", "tien")):
            return "period_ranking", ("period",), "period_revenue"
        if ranking and any(term in q for term in ("nguoi ban", "nhan vien ban", "nhan vien")) and any(
            term in q for term in ("doanh thu", "doanh so", "tien ban")
        ):
            return "seller_ranking", ("seller",), "seller_revenue"
        if (ranking and any(term in q for term in ("nha cung cap", "ncc"))
                and any(term in q for term in ("hang nhap", "phieu nhap", "tien nhap", "mua vao"))):
            return "supplier_ranking", ("supplier",), "supplier_purchase_amount"
        if "ngay nao" in q and any(term in q for term in ("tien", "doanh thu", "doanh so", "dthu", "ban duoc")) and ranking:
            return "best_sales_day", ("date",), "daily_revenue"
        if ("ti trong" in q or "ty trong" in q or "co cau doanh thu" in q or "phan tram doanh thu" in q
                or (has_percent_mark and "tong doanh thu" in q and any(term in q for term in ("nhom", "thuoc", "san pham", "kenh", "don ban qua")))
                or (has_percent_mark and "doanh thu" in q
                    and any(term in q for term in ("chiem", "dong gop"))
                    and any(term in q for term in ("nhom", "thuoc", "san pham", "kenh", "loai")))
                or ("ti le" in q and "doanh thu" in q and any(term in q for term in ("nhom", "thuoc", "san pham")))):
            return "revenue_share", ("category",), "revenue_share"
        if comparison:
            if any(term in q for term in ("so luong", "ban ra", "ban duoc", "ban dc", "kg", "cai", "chai", "ly", "vien")):
                return "quantity_change", (), "quantity_change"
            if any(term in q for term in ("doanh thu", "doanh so", "dthu", "revenue", "tien", "gia tri")):
                return "revenue_change", (), "revenue_change"

        if customer and any(term in q for term in ("trung binh", "binh quan")) and any(
            term in q for term in ("moi don", "mot don", "moi hoa don")
        ):
            return "customer_average_order_value", ("customer",), "average_order_value"
        if (any(term in q for term in ("gia tri trung binh mot don", "trung binh mot don", "gia tri tb don"))
                or ("trung binh" in q and "don" in tokens and any(term in q for term in ("doanh thu", "dthu", "revenue", "tien")))):
            return "average_order_value", (), "average_order_value"
        if (("gia von" in q or "gia nhap" in q) and
                any(term in q for term in ("ton kho", "trong kho", "con ton", "nam trong kho"))):
            return "inventory_value", ("product",), "inventory_value"
        if (any(term in q for term in ("gia nhap binh quan", "don gia nhap", "gia nhap mot"))
                or ("gia binh quan" in q and any(term in q for term in ("nhap", "gia von")))):
            return "unit_cost", ("product",), "unit_cost"
        if any(term in q for term in ("loi nhuan", "lai gop", "lai rong", "gia von", "bien loi nhuan", "loi nhat")):
            if ranking and any(term in q for term in ("loi nhuan", "lai gop", "lai rong", "loi nhat")):
                return "profit_ranking", ("product",), "profit"
            if "gia von" in q and not any(term in q for term in ("loi nhuan", "lai gop", "lai rong")):
                return "unit_cost", (), "unit_cost"
            return "profit", (), "profit"
        if any(term in q for term in ("phieu nhap", "nhap hang", "nhap vao", "tien nhap")):
            return "purchase_amount", (), "purchase_amount"
        if any(term in q for term in ("dot giao", "lan giao", "dot hang", "giao hang")):
            return "delivery_count", (), "delivery_count"
        if (any(term in q for term in ("han su dung", "han dung", "han lo", "lo hang"))
                or re.search(r"\bhet han\b", q)):
            return "expiry", (), "expiry"
        if any(term in q for term in ("het hang", "sap het hang", "dang het hang", "khong con hang")):
            return "stockout", ("product",), "stockout"
        if (any(term in q for term in ("ton kho", "ton cuoi", "ton thuc", "con ton", "con bao nhieu"))
                or ("con may" in q and bool(tokens & {"vien", "hop", "cai", "chai", "kg", "lon", "ly", "goi", "thung"}))):
            return "inventory", (), "inventory"
        if any(term in q for term in ("gia ban", "don gia", "gia moi", "gia ap dung")):
            return "price_at_date", (), "price_at_date"
        if any(term in q for term in (
            "hang e", "mat hang e", "hang bi e", "mat hang bi e", "ban cham",
            "khong ban duoc", "khong ban dc", "ko ban duoc", "ko ban dc",
            "khong ban ra duoc", "khong co don",
        )):
            return "slow_sellers", ("product",), "slow_sellers"
        if ranking and product:
            return "sales_ranking", ("product",), "sales_quantity"
        if canceled:
            return "cancellation_count", (), "cancellation_count"
        if any(term in q for term in ("ti le khach", "ty le khach")):
            return "customer_repeat_rate", ("customer",), "customer_repeat_rate"
        if any(term in q for term in ("doanh thu", "doanh so", "dthu", "revenue", "tien ban", "thu ve", "total", "ban duoc bao nhieu tien", "bao nhiu tien")) or (
            "ban" in tokens and "tien" in tokens
        ):
            return "revenue", (), "revenue"
        if any(term in q for term in ("so don", "may don", "bao nhieu don", "bao nhiu don", "dem don", "bao nhieu bill", "so bill")):
            return "order_count", (), "order_count"
        if any(term in q for term in ("so luong", "ban duoc", "ban dc", "ban ra", "bao nhieu kg", "bao nhieu chai", "bao nhieu ly", "bao nhieu vien")):
            return "quantity", (), "sales_quantity"
        if customer and any(term in q for term in ("mua", "khach hang", "kh ")):
            return "customer_activity", ("customer",), "customer_activity"
        return None

    def interpret(self, question, as_of_date, business_id=None, *, entity_catalog=None) -> QuerySpec | None:
        """Return a structured intent, including work not executable yet."""
        detected = self._intent(question)
        if detected is None:
            return None
        intent, dimensions, metric = detected
        comparison = resolve_comparison(question, as_of_date)
        period = resolve(question, as_of_date)
        point = resolve_as_of(question, as_of_date)
        q = fold(question)
        point_context = any(term in q for term in ("tinh den", "den het", "cuoi ngay", "ton kho ngay"))
        as_of_intents = {"debt_outstanding", "debt_ranking", "indebted_customer_count", "inventory",
                         "inventory_value", "stockout"}
        if comparison is not None:
            scope = TemporalScope(
                kind="comparison", start=comparison[0], end=comparison[1],
                comparison_start=comparison[2], comparison_end=comparison[3],
            )
        elif point is not None and point_context and intent in as_of_intents:
            scope = TemporalScope(kind="as_of", as_of=point.isoformat())
        elif period is not None:
            scope = TemporalScope(kind="period", start=period[0], end=period[1])
        elif point is not None:
            scope = TemporalScope(kind="as_of", as_of=point.isoformat())
        else:
            scope = TemporalScope(kind="as_of", as_of=as_of_date)
        executable = intent in self.EXECUTABLE and scope.kind == "period"
        evidence = (f"rule:{intent}", f"time:{scope.kind}")
        explicit_time = comparison is not None or period is not None or point is not None
        entity, entity_ambiguous = self._resolve_entity(question, entity_catalog)
        ambiguity_flags = []
        if not explicit_time:
            ambiguity_flags.append("implicit_time_scope")
        if entity_ambiguous:
            ambiguity_flags.append("entity_unresolved")
        unsupported_reason = None
        if not executable:
            unsupported_reason = (
                "intent_not_allowlisted" if intent not in self.EXECUTABLE
                else "temporal_scope_not_executable"
            )
        return QuerySpec(
            intent=intent,
            time=scope,
            confidence=0.75,
            top_k=self._top_k(question) if intent in self.RANKING_INTENTS else 1,
            dimensions=dimensions,
            evidence=evidence,
            executable=executable,
            schema_version="1.0.0",
            raw_question=question,
            business_id=business_id,
            entity=entity,
            metric=metric,
            unit=self._explicit_unit(question),
            sort=SortSpec(metric, "desc") if intent in self.RANKING_INTENTS else None,
            ambiguity_flags=tuple(ambiguity_flags),
            unsupported_reason=unsupported_reason,
        )

    def plan(self, question, as_of_date):
        """Compile only the allowlisted executable subset into an engine plan."""
        spec = self.interpret(question, as_of_date)
        if spec is None or not spec.executable or spec.time is None:
            return None
        return QueryPlan(
            spec.intent,
            spec.time.start,
            spec.time.end,
            spec.confidence,
            entity=spec.entity,
            top_k=spec.top_k,
            evidence=spec.evidence,
            compare_start=spec.time.comparison_start,
            compare_end=spec.time.comparison_end,
        )


class JsonPlanAdapter:
    """Validates a locally generated SLM plan; it never calls a network API."""

    ALLOWED = RulePlanner.EXECUTABLE

    def parse(self, payload):
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
            allowed_fields = {
                "intent", "start", "end", "confidence", "entity", "top_k", "evidence",
                "compare_start", "compare_end",
            }
            if not isinstance(data, dict) or set(data) - allowed_fields:
                return None
            if data["intent"] not in self.ALLOWED or not 0 <= float(data["confidence"]) <= 1:
                return None
            return QueryPlan(**data)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

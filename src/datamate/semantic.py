"""Conservative, evidence-backed source-column to canonical-field mapping.

This module proposes semantic mappings only. It does not alter source tables,
infer joins, or enable metrics in the executor.
"""
from dataclasses import dataclass

from .normalise import fold


@dataclass(frozen=True)
class ColumnMapping:
    source_index: int
    source_header: str
    candidate_field: str | None
    canonical_field: str | None
    status: str
    confidence: float
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class TableSchema:
    table_name: str
    source: str
    mappings: tuple[ColumnMapping, ...]

    @property
    def mapped_fields(self):
        return {
            item.canonical_field: item.source_index
            for item in self.mappings
            if item.status == "mapped" and item.canonical_field is not None
        }

    def to_dict(self):
        return {
            "table_name": self.table_name,
            "source": self.source,
            "mappings": [
                {
                    "source_index": item.source_index,
                    "source_header": item.source_header,
                    "candidate_field": item.candidate_field,
                    "canonical_field": item.canonical_field,
                    "status": item.status,
                    "confidence": item.confidence,
                    "evidence": list(item.evidence),
                }
                for item in self.mappings
            ],
            "mapped_fields": dict(self.mapped_fields),
        }


# Only high-precision aliases are listed here. Generic labels such as "Giá trị",
# "Thành tiền", "Ngày", and "Trạng thái" intentionally remain unresolved.
_EXACT_ALIASES = {
    "order_id": {
        "ma don", "ma don hang", "order id", "order code", "invoice id",
    },
    "customer_id": {
        "ma khach", "ma khach hang", "customer id", "customer code",
    },
    "product_id": {
        "ma san pham", "ma hang", "product id", "product code", "sku",
    },
    "order_date": {
        "ngay dat", "ngay tao don", "order date", "created at",
    },
    "payment_date": {
        "ngay thu", "ngay thanh toan", "payment date", "collected at",
    },
    "quantity": {
        "so luong", "sl", "quantity", "qty",
    },
    "unit_price": {
        "don gia", "unit price",
    },
    "order_total_after_discount": {
        "tong sau giam gia", "tong tien sau giam gia",
        "total after discount",
    },
    "order_status": {
        "trang thai don hang", "order status",
    },
    "payment_status": {
        "trang thai thanh toan", "payment status",
    },
}

_CONTEXTUAL_ALIASES = {
    ("thanh toan", "gia tri"): "payment_event_amount",
    ("lich su thanh toan", "gia tri"): "payment_event_amount",
    ("payment", "amount"): "payment_event_amount",
    ("thanh toan", "ngay"): "payment_date",
    ("payment", "date"): "payment_date",
    ("don hang", "ngay"): "order_date",
    ("thong tin don hang", "ngay"): "order_date",
    ("order", "date"): "order_date",
    ("thanh toan", "trang thai"): "payment_status",
    ("payment", "status"): "payment_status",
    ("don hang", "trang thai"): "order_status",
    ("thong tin don hang", "trang thai"): "order_status",
    ("order", "status"): "order_status",
    ("thanh toan", "ma giao dich"): "payment_transaction_id",
    ("lich su thanh toan", "ma giao dich"): "payment_transaction_id",
}


def _resolve_header(header):
    """Return (candidate field, confidence, evidence) without fuzzy matching."""
    raw = str(header or "")
    if " / " in raw:
        group_raw, leaf_raw = raw.rsplit(" / ", 1)
        group, leaf = fold(group_raw), fold(leaf_raw)
        contextual = _CONTEXTUAL_ALIASES.get((group, leaf))
        if contextual:
            return contextual, 0.98, ("exact_group_and_leaf_alias",)
        exact = {
            canonical: aliases
            for canonical, aliases in _EXACT_ALIASES.items()
            if leaf in aliases
        }
        if len(exact) == 1:
            canonical = next(iter(exact))
            return canonical, 0.96, ("exact_leaf_alias", "group_context_preserved")
        return None, 0.0, ("no_exact_alias",)

    normalized = fold(raw)
    matches = [
        canonical for canonical, aliases in _EXACT_ALIASES.items()
        if normalized in aliases
    ]
    if len(matches) == 1:
        return matches[0], 1.0, ("exact_header_alias",)
    return None, 0.0, ("no_exact_alias",)


def map_table_schema(table):
    """Map unambiguous exact aliases; collisions and unknown labels fail closed."""
    provisional = []
    for index, header in enumerate(table.headers):
        candidate, confidence, evidence = _resolve_header(header)
        provisional.append({
            "source_index": index,
            "source_header": str(header),
            "candidate_field": candidate,
            "confidence": confidence,
            "evidence": evidence,
        })

    counts = {}
    for item in provisional:
        candidate = item["candidate_field"]
        if candidate is not None:
            counts[candidate] = counts.get(candidate, 0) + 1

    mappings = []
    for item in provisional:
        candidate = item["candidate_field"]
        if candidate is None:
            mappings.append(ColumnMapping(
                source_index=item["source_index"],
                source_header=item["source_header"],
                candidate_field=None,
                canonical_field=None,
                status="unmapped",
                confidence=0.0,
                evidence=item["evidence"],
            ))
        elif counts[candidate] > 1:
            mappings.append(ColumnMapping(
                source_index=item["source_index"],
                source_header=item["source_header"],
                candidate_field=candidate,
                canonical_field=None,
                status="ambiguous",
                confidence=0.0,
                evidence=item["evidence"] + ("multiple_columns_match_same_field",),
            ))
        else:
            mappings.append(ColumnMapping(
                source_index=item["source_index"],
                source_header=item["source_header"],
                candidate_field=candidate,
                canonical_field=candidate,
                status="mapped",
                confidence=item["confidence"],
                evidence=item["evidence"],
            ))

    return TableSchema(
        table_name=table.name,
        source=table.source,
        mappings=tuple(mappings),
    )

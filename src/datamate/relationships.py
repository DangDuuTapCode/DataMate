"""Evidence-based relationship candidates between semantically mapped tables.

A validated candidate means its key/cardinality checks are safe enough for a
reviewed join plan. This module does not execute joins or infer business rules.
"""
from dataclasses import dataclass

from .semantic import map_table_schema


_RELATIONSHIP_KEYS = {
    "order_id",
    "customer_id",
    "product_id",
    "payment_transaction_id",
}


@dataclass(frozen=True)
class RelationshipCandidate:
    from_table: str
    to_table: str
    canonical_key: str
    from_column_index: int
    to_column_index: int
    cardinality: str
    status: str
    confidence: float
    from_row_count: int
    to_row_count: int
    from_distinct_keys: int
    to_distinct_keys: int
    matched_distinct_keys: int
    from_unmatched_keys: int
    to_unmatched_keys: int
    from_blank_keys: int
    to_blank_keys: int
    from_duplicate_excess: int
    to_duplicate_excess: int
    evidence: tuple[str, ...]

    def to_dict(self):
        return {
            "from_table": self.from_table,
            "to_table": self.to_table,
            "canonical_key": self.canonical_key,
            "from_column_index": self.from_column_index,
            "to_column_index": self.to_column_index,
            "cardinality": self.cardinality,
            "status": self.status,
            "confidence": self.confidence,
            "from_row_count": self.from_row_count,
            "to_row_count": self.to_row_count,
            "from_distinct_keys": self.from_distinct_keys,
            "to_distinct_keys": self.to_distinct_keys,
            "matched_distinct_keys": self.matched_distinct_keys,
            "from_unmatched_keys": self.from_unmatched_keys,
            "to_unmatched_keys": self.to_unmatched_keys,
            "from_blank_keys": self.from_blank_keys,
            "to_blank_keys": self.to_blank_keys,
            "from_duplicate_excess": self.from_duplicate_excess,
            "to_duplicate_excess": self.to_duplicate_excess,
            "evidence": list(self.evidence),
        }


def _column_values(table, column_index):
    values = []
    blank_count = 0
    for row in table.rows:
        value = row[column_index] if column_index < len(row) else None
        if value is None or not str(value).strip():
            blank_count += 1
            continue
        # Preserve exact source spelling and leading zeroes. No fuzzy or
        # numeric coercion is allowed for identifiers.
        values.append(str(value).strip())
    return values, blank_count


def _key_profile(table, column_index):
    values, blanks = _column_values(table, column_index)
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return {
        "values": set(counts),
        "counts": counts,
        "blank_count": blanks,
        "row_count": len(table.rows),
        "duplicate_excess": sum(count - 1 for count in counts.values()),
    }


def _candidate(left, right, field, left_index, right_index):
    left_profile = _key_profile(left, left_index)
    right_profile = _key_profile(right, right_index)
    left_keys = left_profile["values"]
    right_keys = right_profile["values"]
    overlap = left_keys & right_keys
    left_unmatched = left_keys - right_keys
    right_unmatched = right_keys - left_keys
    left_unique = left_profile["duplicate_excess"] == 0
    right_unique = right_profile["duplicate_excess"] == 0

    if not left_keys or not right_keys or not overlap:
        status, cardinality, confidence = "rejected", "unknown", 0.0
        evidence = ("no_nonblank_key_overlap",)
    elif left_unique and right_unique:
        if left_profile["blank_count"] or right_profile["blank_count"]:
            status, cardinality, confidence = "rejected", "one_to_one", 0.0
            evidence = ("canonical_key_match", "both_sides_unique", "blank_keys_prevent_validation")
        elif left_keys == right_keys:
            status, cardinality, confidence = "validated", "one_to_one", 1.0
            evidence = ("canonical_key_match", "both_sides_unique", "complete_key_coverage")
        else:
            status, cardinality, confidence = "candidate", "one_to_one", 0.5
            evidence = ("canonical_key_match", "both_sides_unique", "partial_key_coverage")
    elif not left_unique and right_unique:
        if not left_unmatched and left_profile["blank_count"] == 0:
            status, cardinality, confidence = "validated", "many_to_one", 1.0
            evidence = ("canonical_key_match", "right_side_unique", "all_left_keys_match")
        else:
            status, cardinality, confidence = "rejected", "many_to_one", 0.0
            evidence = ("canonical_key_match", "right_side_unique", "unmatched_or_blank_left_keys")
    elif left_unique and not right_unique:
        if not right_unmatched and right_profile["blank_count"] == 0:
            status, cardinality, confidence = "validated", "one_to_many", 1.0
            evidence = ("canonical_key_match", "left_side_unique", "all_right_keys_match")
        else:
            status, cardinality, confidence = "rejected", "one_to_many", 0.0
            evidence = ("canonical_key_match", "left_side_unique", "unmatched_or_blank_right_keys")
    else:
        status, cardinality, confidence = "ambiguous", "many_to_many", 0.0
        evidence = ("canonical_key_match", "both_sides_have_duplicate_keys", "join_multiplication_risk")

    return RelationshipCandidate(
        from_table=left.name,
        to_table=right.name,
        canonical_key=field,
        from_column_index=left_index,
        to_column_index=right_index,
        cardinality=cardinality,
        status=status,
        confidence=confidence,
        from_row_count=left_profile["row_count"],
        to_row_count=right_profile["row_count"],
        from_distinct_keys=len(left_keys),
        to_distinct_keys=len(right_keys),
        matched_distinct_keys=len(overlap),
        from_unmatched_keys=len(left_unmatched),
        to_unmatched_keys=len(right_unmatched),
        from_blank_keys=left_profile["blank_count"],
        to_blank_keys=right_profile["blank_count"],
        from_duplicate_excess=left_profile["duplicate_excess"],
        to_duplicate_excess=right_profile["duplicate_excess"],
        evidence=evidence,
    )


def discover_relationships(tables):
    """Return key-overlap/cardinality candidates; never perform a join."""
    schemas = [map_table_schema(table) for table in tables]
    results = []
    for left_index, left in enumerate(tables):
        left_fields = schemas[left_index].mapped_fields
        for right_index in range(left_index + 1, len(tables)):
            right = tables[right_index]
            right_fields = schemas[right_index].mapped_fields
            shared_fields = sorted(
                (set(left_fields) & set(right_fields)) & _RELATIONSHIP_KEYS
            )
            for field in shared_fields:
                results.append(_candidate(
                    left, right, field, left_fields[field], right_fields[field]
                ))
    return results

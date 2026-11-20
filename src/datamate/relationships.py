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
    "employee_id",
    "supplier_id",
    "purchase_receipt_id",
    "batch_id",
    "branch_id",
    "imei",
}


@dataclass(frozen=True)
class RelationshipCandidate:
    from_table: str
    from_source: str
    to_table: str
    to_source: str
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
    canonical_keys: tuple[str, ...] = ()
    from_column_indices: tuple[int, ...] = ()
    to_column_indices: tuple[int, ...] = ()

    def to_dict(self):
        return {
            "from_table": self.from_table,
            "from_source": self.from_source,
            "to_table": self.to_table,
            "to_source": self.to_source,
            "canonical_key": self.canonical_key,
            "canonical_keys": list(self.canonical_keys or (self.canonical_key,)),
            "from_column_index": self.from_column_index,
            "to_column_index": self.to_column_index,
            "from_column_indices": list(self.from_column_indices or (self.from_column_index,)),
            "to_column_indices": list(self.to_column_indices or (self.to_column_index,)),
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


def _candidate_from_profiles(
    left,
    right,
    canonical_keys,
    left_indices,
    right_indices,
    left_profile,
    right_profile,
    extra_evidence=(),
):
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
        if left_keys == right_keys and left_profile["blank_count"] == 0:
            status, cardinality, confidence = "validated", "one_to_one", 1.0
            evidence = ("canonical_key_match", "both_sides_unique", "complete_nonblank_key_coverage")
        elif left_keys == right_keys and left_profile["blank_count"] > 0:
            status, cardinality, confidence = "validated_left_join", "one_to_one", 0.95
            evidence = (
                "canonical_key_match", "both_sides_unique",
                "complete_nonblank_key_coverage", "blank_source_keys_require_left_join",
            )
        else:
            status, cardinality, confidence = "candidate", "one_to_one", 0.5
            evidence = ("canonical_key_match", "both_sides_unique", "partial_key_coverage")
    elif not left_unique and right_unique:
        if not left_unmatched and left_profile["blank_count"] == 0:
            status, cardinality, confidence = "validated", "many_to_one", 1.0
            evidence = ("canonical_key_match", "right_side_unique", "all_left_keys_match")
        elif not left_unmatched:
            # Blank source keys cannot match a dimension row. A LEFT JOIN
            # preserves those source-grain rows as null-dimension records;
            # the path/contract layers must carry and enforce that requirement.
            status, cardinality, confidence = "validated_left_join", "many_to_one", 0.95
            evidence = (
                "canonical_key_match", "right_side_unique",
                "all_nonblank_left_keys_match", "blank_source_keys_require_left_join",
            )
        else:
            status, cardinality, confidence = "rejected", "many_to_one", 0.0
            evidence = ("canonical_key_match", "right_side_unique", "unmatched_or_blank_left_keys")
    elif left_unique and not right_unique:
        if not right_unmatched and right_profile["blank_count"] == 0:
            status, cardinality, confidence = "validated", "one_to_many", 1.0
            evidence = ("canonical_key_match", "left_side_unique", "all_right_keys_match")
        elif not right_unmatched:
            status, cardinality, confidence = "validated_left_join", "one_to_many", 0.95
            evidence = (
                "canonical_key_match", "left_side_unique",
                "all_nonblank_right_keys_match", "blank_source_keys_require_left_join",
            )
        else:
            status, cardinality, confidence = "rejected", "one_to_many", 0.0
            evidence = ("canonical_key_match", "left_side_unique", "unmatched_or_blank_right_keys")
    else:
        status, cardinality, confidence = "ambiguous", "many_to_many", 0.0
        evidence = ("canonical_key_match", "both_sides_have_duplicate_keys", "join_multiplication_risk")

    canonical_keys = tuple(canonical_keys)
    left_indices = tuple(left_indices)
    right_indices = tuple(right_indices)
    return RelationshipCandidate(
        from_table=left.name,
        from_source=left.source,
        to_table=right.name,
        to_source=right.source,
        canonical_key=canonical_keys[0] if len(canonical_keys) == 1 else "+".join(canonical_keys),
        from_column_index=left_indices[0],
        to_column_index=right_indices[0],
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
        evidence=tuple(extra_evidence) + tuple(evidence),
        canonical_keys=canonical_keys,
        from_column_indices=left_indices,
        to_column_indices=right_indices,
    )


def _candidate(left, right, field, left_index, right_index):
    return _candidate_from_profiles(
        left,
        right,
        (field,),
        (left_index,),
        (right_index,),
        _key_profile(left, left_index),
        _key_profile(right, right_index),
    )


def _composite_key_profile(table, column_indices, *, deduplicate_exact_rows):
    rows = table.rows
    deduplicated_count = 0
    if deduplicate_exact_rows:
        unique_rows, seen_rows = [], set()
        for row in rows:
            row_key = tuple((type(value).__name__, repr(value)) for value in row)
            if row_key in seen_rows:
                deduplicated_count += 1
                continue
            seen_rows.add(row_key)
            unique_rows.append(row)
        rows = unique_rows

    counts = {}
    blank_count = 0
    for row in rows:
        values = tuple(
            str(row[index]).strip()
            if index < len(row) and row[index] is not None
            else ""
            for index in column_indices
        )
        if any(not value for value in values):
            blank_count += 1
            continue
        counts[values] = counts.get(values, 0) + 1
    return {
        "values": set(counts),
        "counts": counts,
        "blank_count": blank_count,
        "row_count": len(rows),
        "duplicate_excess": sum(count - 1 for count in counts.values()),
        "deduplicated_rows": deduplicated_count,
    }


def _composite_candidate(
    left,
    right,
    canonical_keys,
    left_indices,
    right_indices,
    *,
    deduplicate_identical_order_lines,
):
    left_profile = _composite_key_profile(
        left, left_indices,
        deduplicate_exact_rows=deduplicate_identical_order_lines,
    )
    right_profile = _composite_key_profile(
        right, right_indices,
        deduplicate_exact_rows=deduplicate_identical_order_lines,
    )
    deduplicated = (
        left_profile["deduplicated_rows"] + right_profile["deduplicated_rows"]
    )
    extra_evidence = ("composite_key",)
    if deduplicate_identical_order_lines:
        extra_evidence += ("rulebook_exact_duplicate_rows_policy_applied",)
        if deduplicated:
            extra_evidence += ("exact_duplicate_rows_removed",)
    return _candidate_from_profiles(
        left,
        right,
        canonical_keys,
        left_indices,
        right_indices,
        left_profile,
        right_profile,
        extra_evidence=extra_evidence,
    )


def discover_relationships(tables, *, deduplicate_identical_order_lines=False):
    """Return key-overlap/cardinality candidates; never perform a join."""
    schemas = [map_table_schema(table) for table in tables]
    results = []
    for left_index, left in enumerate(tables):
        left_fields = schemas[left_index].mapped_fields
        for right_index in range(left_index + 1, len(tables)):
            right = tables[right_index]
            right_fields = schemas[right_index].mapped_fields
            shared_mapped_fields = set(left_fields) & set(right_fields)
            shared_fields = sorted(shared_mapped_fields & _RELATIONSHIP_KEYS)
            for field in shared_fields:
                results.append(_candidate(
                    left, right, field, left_fields[field], right_fields[field]
                ))
            composite_fields = ("order_id", "order_line_number")
            if set(composite_fields).issubset(shared_mapped_fields):
                results.append(_composite_candidate(
                    left,
                    right,
                    composite_fields,
                    tuple(left_fields[field] for field in composite_fields),
                    tuple(right_fields[field] for field in composite_fields),
                    deduplicate_identical_order_lines=deduplicate_identical_order_lines,
                ))
    return results

"""Conservative graph-path discovery over validated schema relationships.

This module only describes candidate paths. It never joins data or claims that
a path is safe for aggregation when an edge can multiply the current grain.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipPathHop:
    from_table: tuple[str, str]
    to_table: tuple[str, str]
    canonical_keys: tuple[str, ...]
    from_column_indices: tuple[int, ...]
    to_column_indices: tuple[int, ...]
    cardinality: str
    fanout: bool

    def to_dict(self):
        return {
            "from_table": {"table_name": self.from_table[0], "source": self.from_table[1]},
            "to_table": {"table_name": self.to_table[0], "source": self.to_table[1]},
            "canonical_keys": list(self.canonical_keys),
            "from_column_indices": list(self.from_column_indices),
            "to_column_indices": list(self.to_column_indices),
            "cardinality": self.cardinality,
            "fanout": self.fanout,
        }


@dataclass(frozen=True)
class RelationshipPathResolution:
    status: str
    hops: tuple[RelationshipPathHop, ...] = ()
    candidate_count: int = 0
    reasons: tuple[str, ...] = ()

    @property
    def available(self):
        return self.status == "unique_safe"

    def to_dict(self):
        return {
            "status": self.status,
            "available": self.available,
            "candidate_count": self.candidate_count,
            "hops": [hop.to_dict() for hop in self.hops],
            "reasons": list(self.reasons),
        }


def _identity(table_name, source):
    return (str(table_name), str(source))


def _edge_hops(relationship):
    """Return both directions, retaining whether traversal multiplies rows."""
    if relationship.status != "validated":
        return ()
    keys = tuple(relationship.canonical_keys or (relationship.canonical_key,))
    left_indices = tuple(
        relationship.from_column_indices or (relationship.from_column_index,)
    )
    right_indices = tuple(
        relationship.to_column_indices or (relationship.to_column_index,)
    )
    if not keys or len(keys) != len(left_indices) or len(keys) != len(right_indices):
        return ()
    left = _identity(relationship.from_table, relationship.from_source)
    right = _identity(relationship.to_table, relationship.to_source)
    if left == right:
        return ()

    cardinality = relationship.cardinality
    if cardinality == "one_to_one":
        left_fanout = right_fanout = False
    elif cardinality == "many_to_one":
        left_fanout, right_fanout = False, True
    elif cardinality == "one_to_many":
        left_fanout, right_fanout = True, False
    else:
        return ()

    return (
        RelationshipPathHop(
            left, right, keys, left_indices, right_indices,
            cardinality, left_fanout,
        ),
        RelationshipPathHop(
            right, left, keys, right_indices, left_indices,
            cardinality, right_fanout,
        ),
    )


def resolve_relationship_path(
    relationships,
    source_table,
    target_table,
    *,
    max_hops=3,
    max_candidates=64,
):
    """Resolve one unambiguous path; reject fanout and competing paths.

    Table arguments are exact (table_name, source_filename) tuples. Only
    validated relationships are traversable. Multiple paths are never ranked
    heuristically, and one-to-many traversal is explicitly marked as fanout.
    """
    if (
        not isinstance(source_table, tuple) or len(source_table) != 2
        or not isinstance(target_table, tuple) or len(target_table) != 2
        or max_hops < 1 or max_candidates < 1
    ):
        return RelationshipPathResolution("invalid_request", reasons=("invalid_path_arguments",))
    source = _identity(*source_table)
    target = _identity(*target_table)
    if source == target:
        return RelationshipPathResolution("identity", reasons=("source_equals_target",))

    adjacency = {}
    for relationship in relationships:
        for hop in _edge_hops(relationship):
            adjacency.setdefault(hop.from_table, []).append(hop)

    paths = []
    overflow = False

    def walk(node, visited, hops):
        nonlocal overflow
        if overflow:
            return
        if len(hops) >= max_hops:
            return
        for hop in adjacency.get(node, ()):
            if hop.to_table in visited:
                continue
            candidate = hops + (hop,)
            if hop.to_table == target:
                paths.append(candidate)
                if len(paths) >= max_candidates:
                    overflow = True
                    return
            else:
                walk(hop.to_table, visited | {hop.to_table}, candidate)
            if overflow:
                return

    walk(source, {source}, ())
    if overflow:
        return RelationshipPathResolution(
            "ambiguous", candidate_count=len(paths),
            reasons=("candidate_path_limit_reached",),
        )
    if not paths:
        return RelationshipPathResolution("no_path", reasons=("no_validated_path_within_hop_limit",))
    if len(paths) != 1:
        return RelationshipPathResolution(
            "ambiguous", candidate_count=len(paths),
            reasons=("multiple_validated_paths",),
        )
    path = paths[0]
    if any(hop.fanout for hop in path):
        return RelationshipPathResolution(
            "fanout_risk", hops=path, candidate_count=1,
            reasons=("path_contains_one_to_many_traversal",),
        )
    return RelationshipPathResolution(
        "unique_safe", hops=path, candidate_count=1,
        reasons=("unique_validated_path_preserves_source_grain",),
    )

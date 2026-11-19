"""Explicit, query-scoped contract for grain-preserving fact joins.

This module validates the structure of a proposed execution contract. It does
not prove that a declared business grain or measure meaning is correct, and it
does not execute a join. Those claims still require reviewed source/rule
evidence before a planner may use the contract.
"""
from dataclasses import dataclass

from .relationship_paths import RelationshipPathHop, RelationshipPathResolution


@dataclass(frozen=True)
class FactJoinContract:
    fact_table: tuple[str, str]
    target_table: tuple[str, str]
    fact_grain: str
    measure_field: str
    measure_column_index: int
    aggregation_stage: str
    join_type: str
    path_hops: tuple

    def to_dict(self):
        return {
            "fact_table": {
                "table_name": self.fact_table[0],
                "source": self.fact_table[1],
            },
            "target_table": {
                "table_name": self.target_table[0],
                "source": self.target_table[1],
            },
            "fact_grain": self.fact_grain,
            "measure_field": self.measure_field,
            "measure_column_index": self.measure_column_index,
            "aggregation_stage": self.aggregation_stage,
            "join_type": self.join_type,
            "path_hops": [hop.to_dict() for hop in self.path_hops],
        }


def _valid_identity(value):
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and all(isinstance(part, str) and part.strip() for part in value)
    )


def _valid_hop(hop):
    if not isinstance(hop, RelationshipPathHop):
        return False
    if not _valid_identity(hop.from_table) or not _valid_identity(hop.to_table):
        return False
    if hop.from_table == hop.to_table or hop.fanout is not False:
        return False
    if (
        not isinstance(hop.cardinality, str)
        or hop.cardinality not in {"many_to_one", "one_to_one"}
    ):
        return False
    if (
        not isinstance(hop.canonical_keys, tuple)
        or not hop.canonical_keys
        or any(not isinstance(key, str) or not key.strip() for key in hop.canonical_keys)
        or len(set(hop.canonical_keys)) != len(hop.canonical_keys)
    ):
        return False
    if (
        not isinstance(hop.from_column_indices, tuple)
        or not isinstance(hop.to_column_indices, tuple)
        or len(hop.canonical_keys) != len(hop.from_column_indices)
        or len(hop.canonical_keys) != len(hop.to_column_indices)
    ):
        return False
    indices = hop.from_column_indices + hop.to_column_indices
    return all(
        isinstance(column, int) and not isinstance(column, bool) and column >= 0
        for column in indices
    )


def build_fact_join_contract(
    path_resolution,
    fact_table,
    target_table,
    *,
    fact_grain,
    measure_field,
    measure_column_index,
    aggregation_stage="after_join",
    join_type="inner",
):
    """Build a structural contract only for one validated, grain-safe path.

    fact_grain and measure_field are explicit declarations supplied by a
    higher-level reviewed query profile; this function does not infer or
    authenticate their business meaning.
    """
    if (
        not isinstance(path_resolution, RelationshipPathResolution)
        or not path_resolution.available
        or not isinstance(path_resolution.candidate_count, int)
        or isinstance(path_resolution.candidate_count, bool)
        or path_resolution.candidate_count != 1
        or not isinstance(path_resolution.hops, tuple)
        or not path_resolution.hops
        or not _valid_identity(fact_table)
        or not _valid_identity(target_table)
        or fact_table == target_table
        or not isinstance(fact_grain, str)
        or not fact_grain.strip()
        or not isinstance(measure_field, str)
        or not measure_field.strip()
        or not isinstance(measure_column_index, int)
        or isinstance(measure_column_index, bool)
        or measure_column_index < 0
        or aggregation_stage != "after_join"
        or not isinstance(join_type, str)
        or join_type not in {"inner", "left"}
    ):
        return None

    hops = path_resolution.hops
    if hops[0].from_table != fact_table or hops[-1].to_table != target_table:
        return None

    visited_tables = {fact_table}
    for index, hop in enumerate(hops):
        if not _valid_hop(hop):
            return None
        if index and hops[index - 1].to_table != hop.from_table:
            return None
        if hop.to_table in visited_tables:
            return None
        visited_tables.add(hop.to_table)

    # Validated relationships currently require complete key coverage and no
    # blank keys. The contract remains structural and does not execute joins.
    return FactJoinContract(
        fact_table=fact_table,
        target_table=target_table,
        fact_grain=fact_grain.strip(),
        measure_field=measure_field.strip(),
        measure_column_index=measure_column_index,
        aggregation_stage=aggregation_stage,
        join_type=join_type,
        path_hops=tuple(hops),
    )

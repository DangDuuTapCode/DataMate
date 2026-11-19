"""Execute only explicit, grain-preserving fact join contracts.

This executor is deliberately narrow: it performs no discovery, inference,
aggregation, filtering, or metric calculation. It revalidates each declared
many-to-one/one-to-one edge against the supplied in-memory tables and preserves
one output row per fact row. Blank source keys require an explicit LEFT JOIN.
"""
from dataclasses import dataclass

from .join_contracts import FactJoinContract
from .relationship_paths import RelationshipPathHop
from .semantic import map_table_schema
from .types import Table


_INVALID_KEY = object()


@dataclass(frozen=True)
class JoinedTableRows:
    identity: tuple[str, str]
    headers: tuple[str, ...]
    rows: tuple[tuple | None, ...]


@dataclass(frozen=True)
class FactJoinResult:
    fact_table: tuple[str, str]
    join_type: str
    row_count: int
    table_rows: tuple[JoinedTableRows, ...]

    def _table(self, identity):
        matches = [item for item in self.table_rows if item.identity == identity]
        return matches[0] if len(matches) == 1 else None

    def column(self, identity, column_index):
        table = self._table(identity)
        if (
            table is None
            or not isinstance(column_index, int)
            or isinstance(column_index, bool)
            or column_index < 0
            or column_index >= len(table.headers)
        ):
            return None
        values = []
        for row in table.rows:
            if row is None:
                values.append(None)
            elif column_index >= len(row):
                return None
            else:
                values.append(row[column_index])
        return tuple(values)

    def value(self, row_index, identity, column_index):
        table = self._table(identity)
        if (
            table is None
            or not isinstance(row_index, int)
            or isinstance(row_index, bool)
            or row_index < 0
            or row_index >= self.row_count
            or not isinstance(column_index, int)
            or isinstance(column_index, bool)
            or column_index < 0
            or column_index >= len(table.headers)
        ):
            return None
        row = table.rows[row_index]
        if row is None or column_index >= len(row):
            return None
        return row[column_index]


def _valid_identity(identity):
    return (
        isinstance(identity, tuple)
        and len(identity) == 2
        and all(isinstance(part, str) and part.strip() for part in identity)
    )


def _key(row, indices):
    values = []
    for index in indices:
        if index >= len(row):
            return _INVALID_KEY
        value = row[index]
        if value is None or not str(value).strip():
            return None
        # Match relationship discovery: exact trimmed text, preserving
        # case and leading zeroes. Never coerce identifiers to numbers.
        values.append(str(value).strip())
    return tuple(values)


def execute_fact_join_contract(tables, contract):
    """Execute a validated path while preserving the original fact row count.

    Returns None on any contract/table mismatch, duplicate target key,
    unmatched nonblank source key, or unsafe blank-key condition.
    """
    if (
        not isinstance(contract, FactJoinContract)
        or not _valid_identity(contract.fact_table)
        or not _valid_identity(contract.target_table)
        or not isinstance(contract.path_hops, tuple)
        or not contract.path_hops
        or not isinstance(contract.join_type, str)
        or contract.join_type not in {"inner", "left"}
        or contract.aggregation_stage != "after_join"
        or not isinstance(contract.measure_field, str)
        or not contract.measure_field.strip()
        or not isinstance(contract.measure_column_index, int)
        or isinstance(contract.measure_column_index, bool)
        or contract.measure_column_index < 0
    ):
        return None

    table_map = {}
    for table in tables:
        if not isinstance(table, Table):
            return None
        identity = (table.name, table.source)
        if not _valid_identity(identity) or identity in table_map:
            return None
        table_map[identity] = table

    if contract.fact_table not in table_map:
        return None
    fact = table_map[contract.fact_table]
    if (
        contract.measure_column_index >= len(fact.headers)
        or str(fact.headers[contract.measure_column_index]).strip()
        != contract.measure_field.strip()
    ):
        return None

    schemas = {identity: map_table_schema(table) for identity, table in table_map.items()}
    hops = contract.path_hops
    if (
        not all(isinstance(hop, RelationshipPathHop) for hop in hops)
        or hops[0].from_table != contract.fact_table
        or hops[-1].to_table != contract.target_table
    ):
        return None

    visited = {contract.fact_table}
    for index, hop in enumerate(hops):
        if (
            not isinstance(hop, RelationshipPathHop)
            or not _valid_identity(hop.from_table)
            or not _valid_identity(hop.to_table)
            or hop.from_table == hop.to_table
            or hop.fanout is not False
            or not isinstance(hop.requires_left_join, bool)
            or not isinstance(hop.cardinality, str)
            or hop.cardinality not in {"many_to_one", "one_to_one"}
            or not isinstance(hop.canonical_keys, tuple)
            or not hop.canonical_keys
            or not isinstance(hop.from_column_indices, tuple)
            or not isinstance(hop.to_column_indices, tuple)
            or len(hop.canonical_keys) != len(hop.from_column_indices)
            or len(hop.canonical_keys) != len(hop.to_column_indices)
            or any(not isinstance(key, str) or not key.strip() for key in hop.canonical_keys)
            or len(set(hop.canonical_keys)) != len(hop.canonical_keys)
        ):
            return None
        indices = hop.from_column_indices + hop.to_column_indices
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in indices
        ):
            return None
        if index and hops[index - 1].to_table != hop.from_table:
            return None
        if hop.to_table in visited:
            return None
        if hop.from_table not in table_map or hop.to_table not in table_map:
            return None
        if any(
            value >= len(table_map[hop.from_table].headers)
            for value in hop.from_column_indices
        ):
            return None
        if any(
            value >= len(table_map[hop.to_table].headers)
            for value in hop.to_column_indices
        ):
            return None
        for key, from_index, to_index in zip(
            hop.canonical_keys,
            hop.from_column_indices,
            hop.to_column_indices,
        ):
            if (
                schemas[hop.from_table].mapped_fields.get(key) != from_index
                or schemas[hop.to_table].mapped_fields.get(key) != to_index
            ):
                return None
        if hop.requires_left_join and contract.join_type != "left":
            return None
        visited.add(hop.to_table)

    # Each table's rows remain aligned to the original fact rows. This avoids
    # flattening colliding column names and makes multi-hop lookups explicit.
    aligned_rows = {contract.fact_table: list(fact.rows)}
    for hop in hops:
        target_table = table_map[hop.to_table]
        source_rows = aligned_rows.get(hop.from_table)
        if source_rows is None or len(source_rows) != len(fact.rows):
            return None

        target_index = {}
        for target_row in target_table.rows:
            if not isinstance(target_row, (list, tuple)):
                return None
            key = _key(target_row, hop.to_column_indices)
            if key is _INVALID_KEY:
                return None
            if key is None:
                continue
            if key in target_index:
                return None
            target_index[key] = tuple(target_row)
        if not target_index:
            return None

        aligned_target_rows = []
        for source_row in source_rows:
            if source_row is None:
                if contract.join_type != "left":
                    return None
                aligned_target_rows.append(None)
                continue
            if not isinstance(source_row, (list, tuple)):
                return None
            key = _key(source_row, hop.from_column_indices)
            if key is _INVALID_KEY:
                return None
            if key is None:
                if contract.join_type != "left" or not hop.requires_left_join:
                    return None
                aligned_target_rows.append(None)
                continue
            matched = target_index.get(key)
            if matched is None:
                # Nonblank unmatched keys invalidate the evidence; do not
                # silently drop them or turn them into null dimensions.
                return None
            aligned_target_rows.append(matched)

        aligned_rows[hop.to_table] = aligned_target_rows

    result_tables = tuple(
        JoinedTableRows(
            identity=identity,
            headers=tuple(table_map[identity].headers),
            rows=tuple(aligned_rows[identity]),
        )
        for identity in (contract.fact_table,) + tuple(hop.to_table for hop in hops)
    )
    if any(len(item.rows) != len(fact.rows) for item in result_tables):
        return None
    return FactJoinResult(
        fact_table=contract.fact_table,
        join_type=contract.join_type,
        row_count=len(fact.rows),
        table_rows=result_tables,
    )

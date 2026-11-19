# Conservative multi-hop relationship path discovery — 2026-11-20

## Goal

Build a safe foundation for combining information across more than two tables without enabling arbitrary joins or silently multiplying a metric's fact rows.

## Implementation

Added `src/datamate/relationship_paths.py`:
- `RelationshipPathHop` stores exact source-qualified endpoint table identities, canonical key tuple, physical column-index tuples, cardinality, and direction-specific fanout.
- `RelationshipPathResolution` provides explicit status, hops, candidate count, reasons, and availability.
- `resolve_relationship_path` traverses only validated edges, avoids cycles, and enforces a bounded hop count and candidate limit.
- Only a unique path with no one-to-many traversal returns `unique_safe`.
- Multiple paths return `ambiguous`; missing paths return `no_path`; one-to-many traversal returns `fanout_risk`.
- Composite key metadata is carried unchanged, including each physical key-column index.

Added `tests/test_relationship_paths.py` with seven synthetic tests:
1. Safe two-hop many-to-one path.
2. One-to-many fanout rejection.
3. Multiple validated paths are ambiguous.
4. Candidate/unvalidated edge is not traversable.
5. Source filename is part of node identity.
6. Composite key names and indices are preserved.
7. Invalid arguments fail closed.

## Verification

GitHub Actions run `44578825930`, commit `68564ac356af305e63aabe1703ce76d98aadb08f`:
- 293 tests executed.
- 291 passed.
- All feature tests passed.
- Two inherited failures remain: `test_no_large_files` and `test_no_secret_like_strings`, both reporting the existing `CODEX PROGRESS` artifact.
- No local checkout or local test execution was used.

Run: https://github.com/pl2n/DataMate/actions/runs/44578825930

## Explicit limitation

This is discovery-only. It is not wired into `CompositePlanner` or `Executor`, and it does not execute multi-hop joins. It does not resolve polymorphic document references or establish business semantics.

## Next step

Define a query-specific execution contract that includes:
- fact table and exact fact grain;
- target metric and aggregation stage;
- exact approved relationship path;
- allowed traversal cardinality and explicit fanout policy;
- evidence that the chosen path does not multiply or drop fact rows.

Add a synthetic fixture with deliberately duplicated bridge rows and competing relationships. Do not enable execution until the fixture proves the aggregate remains correct. Continue to reject raw-ID polymorphic references unless document type is part of the validated key.

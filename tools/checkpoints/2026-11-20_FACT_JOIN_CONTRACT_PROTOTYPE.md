# Fact join contract structural prototype — 2026-11-20

## Goal

Advance from discovery-only relationship paths toward a query-specific, grain-aware execution contract without enabling general JOIN execution.

## Changes

- Added `src/datamate/join_contracts.py`.
- Added immutable `FactJoinContract` with exact source-qualified fact/target identities, explicit fact-grain and measure declarations, physical measure index, aggregation stage, join type, and full path hops.
- Builder accepts only a unique safe relationship path and rejects fanout, unsupported cardinality, malformed keys/indices, endpoint mismatch, disconnected or cyclic paths, missing declarations, invalid measure indices, unsupported join types, and pre-join aggregation.
- Added `tests/test_join_contracts.py` synthetic regressions.
- Added `docs/FACT_JOIN_CONTRACT.md`.

## Safety boundary

This prototype is not wired into planner or Executor. It does not execute JOINs, enable a metric, or establish business semantics. Fact grain and measure meaning are declarations that still require reviewed, query-specific evidence. One-to-many allocation and pre-join aggregation remain unsupported.

## Commits

- `bad2dcda57a71d8c78d7e49a2c84b969e3008071` — contract builder.
- `2136219d904b5ce99671e3c3d285d5b60a638aae` — initial tests.
- `f5b476972f779b5abe02bf14f8ca438ac143c90f` — stricter cardinality/cycle validation.
- `085284c1562af575d55bf12f80715de6b331e3b3` — malformed path tests.
- `d87b325e158da97ab11f21380cb177e36d3ed680` — documentation.

## Verification

CI pending. No local checkout or local test execution was used.

## Next

Wait for CI and fix any failures. Then inspect one representative multi-source question and its exact source README/rulebook evidence before deciding whether any execution wiring is justified. Keep current composite runtime unchanged until that evidence exists.

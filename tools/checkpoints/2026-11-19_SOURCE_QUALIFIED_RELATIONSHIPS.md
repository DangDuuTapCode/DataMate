# Source-qualified relationship identity — 2026-11-19

## Issue found from the contest input

The archive contains multiple Excel workbooks with repeated worksheet names, commonly `Sheet1`. Before this change, `RelationshipCandidate` stored only `from_table` and `to_table`, and revenue detail-to-order capability checks matched only those names. Two distinct worksheets from different workbooks could therefore be confused.

## Fix

- `src/datamate/relationships.py`
  - Added `from_source` and `to_source` to `RelationshipCandidate`.
  - Included both values in deterministic `to_dict()` serialization.
  - Populated them from the exact source Table objects.
- `src/datamate/bundle_capabilities.py`
  - Detail-to-order validation now matches exact `(table_name, source)` identities.
  - Shape-scope uniqueness uses full table identities, allowing the same sheet name in two different workbooks without treating the identities as duplicates.
- Tests:
  - `tests/test_relationships.py`: verifies that two `Sheet1` tables from different workbooks retain distinct source identities.
  - `tests/test_bundle_capabilities.py`: verifies a detail-to-order evidence scope with repeated worksheet names and an unrelated same-named worksheet.

## Commits

- `c4278e84faace7a690fd5de92e0c62ff5df85823` — relationship evidence source fields.
- `5d2b62e6bc9ead2af82323989070dc3f23428efc` — source-qualified capability matching.
- `5e67affa186a4b428c3dac2ed43c68d24bd84a9b` — full-identity scope uniqueness.
- `abfc0dfc5b6adda4c2cfeaafd4ae75a4fe3194de` — repeated-sheet relationship test.
- `dfe61ceb3bb12b6ef3d4b2b80e36ae19a018ceba` — repeated-sheet detail-to-order test.
- `d16c67a7a26e7e4431a66524f4c105ccc8e2727f` — relationship documentation.
- `6e3af74a27e0a477f4597b6e800c93f8d8ac20a5` — progress docs.
- `38a85ba9ba0fef8cdedc93749a48adb4c2eb264b` — handoff.
- `a6ed87e409b0e9cd03f23caaef9e4a9cefc092c1` — state.

## Verification

No new GitHub Actions result has been verified. The earlier baseline run `44565561293` executed 272 tests, 270 passed, with two inherited `CODEX PROGRESS` hygiene failures. The additional tests and source identity changes are not yet covered by a verified CI result. No local checkout or local tests were run.

## Next

Continue toward a query-specific join planner, but do not execute arbitrary joins. It must consume exact source-qualified relationship evidence, preserve row grain, reject many-to-many paths, and require explicit source-role/metric dependencies. Add multi-hop or dimension joins only when a concrete query family and synthetic regression fixtures demonstrate safe semantics.

# P3 Catalog-Grounded Entity Slot — VERIFIED UNIT

- Date: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`; snapshot base `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git`.
- Pre-unit source archive: `DataMate_checkpoint_2026-11-15_P3_unit-extraction.zip`, SHA-256 `D82FE2E9EE19449F5B328F09D58D8CAB6D9FFDFA3D4BA749799899B8BBB1609A`; its manifest and extracted smoke test were verified.
- Added optional catalog-grounded alias matching to QuerySpec. Unique normalized alias match returns the canonical profile name; multiple canonical matches yield `entity=null` and `entity_unresolved`; no catalog yields null, never a guess.
- Added `entity_unresolved` to QuerySpec v1 ambiguity enum. Regression tests cover unique alias, ambiguity, absent catalog, and schema validity.
- Pre-change targeted test failed as expected due to missing `entity_catalog` API. Post-change `tests.test_query_schema`: 5/5 pass. Full suite: 59 run, 56 passed, 3 Git-only hygiene skips, exit 0.
- No train/public labels read; no holdout rerun. P3 remains NOT PASSED; accuracy metrics have not been refreshed for the changed parser.
- Changed: `src/datamate/understanding.py`, `schemas/query_spec.v1.schema.json`, `tests/test_query_schema.py`, this checkpoint, and state/handoff docs.
- Next: strengthen ambiguity evaluation with measurable precision/recall/F1 and synthetic positive/negative cases; then plan a fresh business-held-out review only after parser changes freeze. Do not use the inspected old holdout.
- No Git, official checkout/main, or source data operation.

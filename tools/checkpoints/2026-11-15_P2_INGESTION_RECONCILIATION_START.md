# Checkpoint P2 Ingestion Reconciliation — IN_PROGRESS

- Started: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`, snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`, no `.git`.
- P1 profile phase is verified at structural L1 in `2026-11-15_P1_MULTI_BUSINESS_PROFILE_COMPLETE.md`.
- P2 goal: expose typed per-source ingestion counts so `source_records = accepted + rejected + intentionally_skipped`; retain provenance; report file-level errors without aborting unrelated files.
- Baseline gap: current tables retain row locations but no reconciliation counters. Empty CSVs currently return no table; blank rows are silently skipped; a file error aborts `read_business` for the business.
- Pre-change full suite: 49 run, 46 passed, 3 Git-only skips.
- Next: add `IngestionStats` and error codes, instrument CSV/XLSX/SQLite, keep default fail-fast compatibility while adding an opt-in file-error collector for batch profiling, add synthetic regression tests, then rerun all formats and the full suite.
- Do not open answers or public-test data. No Git, official checkout, `main`, or ACL operation.

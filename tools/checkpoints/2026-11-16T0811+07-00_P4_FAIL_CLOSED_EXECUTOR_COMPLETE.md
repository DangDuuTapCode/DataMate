# P4 executor hardening — completion checkpoint

- Time: 2026-11-16 08:15 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated no-Git snapshot based on `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 direction: user asked to skip the independent-review wait. P3 remains **NOT VERIFIED / NOT PASSED**. No review annotations or acceptance percentage were created.
- Docker work: out of scope per the user.

## Findings and changes

`src/datamate/metrics.py` previously selected the largest matching table, ignored rows with invalid dates/numbers, and returned zero when the selected period had no rows. Those paths could silently produce partial answers.

The executor now returns no candidate (the API abstains) when:

- More than one table matches a fact schema, or cancellation-rate source tables are ambiguous.
- A nonblank row has an unparseable date, so period completeness cannot be established.
- Any selected-period revenue/quantity value is invalid.
- No rows match the requested period, distinguishing missing data from a genuine measured zero.
- An in-scope order ID is blank, or one order has conflicting statuses.
- A sales-ranking row has a blank product name or invalid quantity.

Added five synthetic regression tests in `tests/test_pipeline.py` for multiple source tables, invalid amounts, invalid dates, no matching rows, and conflicting order statuses.

## Verification

- Focused command: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — exit 0; 11 tests passed.
- Full command: `PYTHONPATH=src python -m unittest discover -s tests -v` — exit 0; 85 run, 82 passed, 3 skipped. All skips are repository-hygiene checks requiring `.git`, unavailable in this isolated snapshot.
- `git diff --check`: unavailable because this snapshot has no `.git`; source/test changes were reviewed directly. The entire snapshot remains intentionally without Git metadata.
- `src/datamate/metrics.py` SHA-256: `FB2E763E029FBC20517862B7317DF9EA7890A4EF47E186B897E268B685097FBA`.
- `tests/test_pipeline.py` SHA-256: `FA801A24C8DAD557EF14622655D662EF188B8B1A0136D4F2B14E7EEB7B501E53`.

## Changed files

- `src/datamate/metrics.py`
- `tests/test_pipeline.py`
- `tools/STATE.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/CHANGELOG_WORK.md`
- `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_START.md`
- `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_COMPLETE.md`

No data, labels, public/private test content, `sources/`, official checkout, branch, Git history, or remote was changed. No commit or push occurred.

## Status and next action

- P1/P2: retain prior verified status; not repeated.
- P3: **NOT VERIFIED / NOT PASSED**; independent review skipped at the user's direction.
- P4: **IN PROGRESS**. Remaining criteria include complete deterministic operator contracts, safe declared joins, sourced business rules, full traces, and replay evidence on supported scope. This slice does not prove the ≥81%/≥85% target.
- P5–P8: open; not re-audited in this work item. Docker is excluded from the current work by user direction.
- Next: continue a bounded P4 synthetic operator-semantics slice or implement P5 stable abstention reason codes, then run affected and full tests and checkpoint again.

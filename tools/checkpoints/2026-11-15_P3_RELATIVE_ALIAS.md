# Checkpoint P3 Relative-Time Alias — VERIFIED

- Date: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`.
- Snapshot base: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git`.
- Development example: `doanh thu hnay` from the separate `biz_125`–`biz_130` sample. The inspected `biz_107`–`biz_112` holdout was not used or rerun.

## Finding and fix

- Before the fix, the new `hnay` regression failed because `resolve()` returned no period; `RulePlanner` consequently defaulted to the record date without recognizing the explicit relative-day phrase.
- `resolve()` and `resolve_as_of()` now recognize `hnay` as today, using the supplied `as_of_date` (not the system date). QuerySpec records a one-day period and no implicit-time ambiguity flag.
- `src/datamate/timeparse.py` SHA-256: `29AB443295312563C3A48D0BE53A320B56FEEDF845698FBA5DE7B8DFF731FB55`.

## Verification

- Focused: `PYTHONPATH=src python -m unittest tests.test_timeparse tests.test_understanding -v` — 13/13 pass.
- Full: `PYTHONPATH=src python -m unittest discover -s tests -v` — 57 run, 54 passed, 3 Git-dependent hygiene checks skipped; exit code 0.
- No full train or holdout replay was run after this change. This work item does not change any holdout metrics.

## Files changed and next action

- `src/datamate/timeparse.py`
- `tests/test_timeparse.py`
- This checkpoint, plus `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `tools/STATE.md`.
- P3 remains **IN_PROGRESS / NOT PASSED**. Next: continue with explicit unit/entity/dimension extraction using separate development examples, add positive ambiguity tests, and later evaluate a newly frozen holdout. Do not reuse the inspected holdout or read answers/public data. No Git/official checkout/main operation was performed.

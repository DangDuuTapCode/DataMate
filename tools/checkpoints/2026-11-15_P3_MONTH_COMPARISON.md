# P3 completed-month comparison scope

- Status: DONE; synthetic positive and negative cases pass. P3 overall remains NOT PASSED.
- Created: 2026-11-15 19:25 +07:00.
- Working copy: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3.
- Base: NO_GIT snapshot of feature/offline-core at 24cfa0908bd20f6e5b210366e956cae0d665b56e.
- Files changed: src/datamate/timeparse.py; tests/test_timeparse.py; docs/IMPLEMENTATION_PROGRESS.md; docs/NEXT_SESSION_HANDOFF.md; tools/STATE.md; this checkpoint.
- timeparse.py SHA-256: EC2343B7CA8520AE5DE50FD2EC2A0856E3850FFE7E940F04CEAE7DA234A77925.
- test_timeparse.py SHA-256: AAE30C8EA8EF30477149E95ED995CCBD3602DCA5F6261E26965766794ADD524E.

## Change

resolve_comparison now resolves a completed previous month against the month before it when both periods are explicit in the question, including December-to-November across a year boundary. It uses full calendar months, not as-of-date-to-date windows. It abstains if the primary period is missing or there is no comparison cue.

## Verification and failure history

- Baseline timeparse suite before the new tests: 8/8 passed.
- Two synthetic positive regressions initially failed as expected (None instead of comparison ranges).
- The first code insertion used over-escaped regex literals; both regressions remained red. The cause was patch-script escaping. Correcting the regex strings made both pass.
- Added negative cases to ensure a lone “previous month” or a comparison without an explicit primary month does not invent a window.
- Focused timeparse suite: 11/11 passed.
- Full suite: PYTHONPATH=src python -m unittest discover -s tests -v — 71 run, 68 passed, 3 Git-dependent hygiene checks skipped because there is no .git; exit 0.

No holdout was read or rerun. No train answer labels/public-test content accessed. No Git action occurred.

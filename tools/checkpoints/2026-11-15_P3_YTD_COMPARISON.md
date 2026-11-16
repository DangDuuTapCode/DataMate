# P3 year-to-date comparison scope

- Status: DONE; synthetic regression passes. P3 overall remains NOT PASSED.
- Created: 2026-11-15 19:16 +07:00.
- Working copy: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3.
- Base: NO_GIT snapshot of feature/offline-core at 24cfa0908bd20f6e5b210366e956cae0d665b56e.
- Files changed: src/datamate/timeparse.py; tests/test_timeparse.py; docs/IMPLEMENTATION_PROGRESS.md; docs/NEXT_SESSION_HANDOFF.md; tools/STATE.md; this checkpoint.
- timeparse.py SHA-256: E5C7732AA5CABDB525603D00AD6509DDBD5075B21A1847D2C2B6D2DF379252A7.
- test_timeparse.py SHA-256: 6A24962027D1A318137483A19DFF7CC0A90E76FC0F6C4941B1ED57F1F9F45D38.

## Change

resolve_comparison now recognizes an explicit year-to-date window compared with the same elapsed period of the previous year. It anchors current end to the record's as_of_date and clamps the previous-year day to that month's last valid day (for example, 29 February compares through 28 February in a non-leap year). It only activates when the question includes a start-of-year phrase, a same-period phrase, and an explicit comparison cue.

## Verification

Before adding regressions: timeparse suite 6/6 passed.
After adding synthetic regressions but before the fix: 8 tests ran, 2 expected failures; both returned no comparison scope.
After the fix: timeparse suite 8/8 passed; understanding suite 7/7 passed.
Full suite: PYTHONPATH=src python -m unittest discover -s tests -v — 66 run, 63 passed, 3 Git-dependent hygiene checks skipped because there is no .git; exit 0.

The change used synthetic cases only. P3-HOLDOUT-2 was not read or rerun, and no train answer labels or public-test content were accessed. No Git operation occurred.

# P4 split calendar and Tết time support — start, 2026-11-16 13:54 GMT+7

- Scope: use the competition-provided `calendar.csv` at runtime to resolve the Tết window and the rulebook's “same number of days immediately before Tết” comparison. Preserve existing Gregorian period parsing.
- Evidence: both official ZIP packages expose `rulebook.md` and `calendar.csv`; calendar schema is `date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday`, covering 2024-01-01 through 2027-12-31 (1,461 rows). The train and public rulebooks both specify lunar 23/12 of Y-1 through lunar 10/1 of Y, and comparison against the same number of days immediately before the window.
- Inspection was limited to these split-level rules and calendar metadata. No question records, answer labels, or business data from either ZIP were opened.
- Current gap: `timeparse.resolve` and `resolve_comparison` are Gregorian-only; `RulePlanner` does not receive the runtime calendar.
- Next: add a strict calendar reader and optional calendar-aware Tết resolver, pass the per-split calendar from `main`, add synthetic calendar/parser and runner regressions, run only the focused tests, then checkpoint and update STATE/progress/handoff.
- Safety: only edit the isolated working copy `work/rehydrated-2026-11-15-P3/source`; keep `sources/`, `main`, official checkout, and Git metadata untouched. No Docker, public-test question/answer access, commit, or push.

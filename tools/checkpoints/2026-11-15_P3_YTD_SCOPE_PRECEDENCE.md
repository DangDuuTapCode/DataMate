# P3 year-to-date scope precedence — 2026-11-15

- Status: implemented and regression-tested; P3 overall remains NOT PASSED.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`.
- Base: NO_GIT snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Changed files: `src/datamate/timeparse.py`, `tests/test_timeparse.py`, this checkpoint, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `tools/STATE.md`.
- `timeparse.py` SHA-256: `EA890116E57AFB5885DCB7831ACABB2B96B4A943D03BF0E7AF5BC465AD8FD2C0`.
- `test_timeparse.py` SHA-256: `AD49A26D70497F58DDCE3BE4B30FCE0FFF594FD53A2B053694EC37944F9B3BFB`.

## Finding and correction

A question-only development sample exposed that “năm nay, tính từ đầu năm đến hết hôm nay” was interpreted as the single endpoint date. The explicit year-to-date phrase was recognized too late: the `hôm nay` branch returned first. A synthetic regression failed before the fix with `2025-11-08..2025-11-08`, while the expected scope was `2025-01-01..2025-11-08`.

Moved current-year and “từ đầu năm” period resolution ahead of relative day endpoint handling. The period end remains anchored to the row's `as_of_date`. This does not alter comparison scope parsing.

## Verification

- Before fix: the new focused synthetic regression failed with the one-day scope above.
- After fix: `PYTHONPATH=src python -m unittest tests.test_timeparse -v` — 15/15 passed.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 75 run, 72 passed, 3 Git-dependent hygiene skips; exit 0.
- P3-HOLDOUT-2 was not rerun or used to choose this rule. The 24 question-only development records remain in ignored local logs and are excluded from archives. No train answer labels or public-test content was read.
- No Git operation, official checkout edit, source data edit, or `main` edit occurred.
- P3 has no current independent full-slot acceptance evaluation and remains NOT PASSED; no 81% claim is made.

## Next

Continue P3 with synthetic or separately selected question-only development cases. Keep all inspected holdouts frozen. Before any acceptance claim, freeze parser and annotations and obtain an independent full-slot review with business-level metrics and enough positive ambiguity cases.

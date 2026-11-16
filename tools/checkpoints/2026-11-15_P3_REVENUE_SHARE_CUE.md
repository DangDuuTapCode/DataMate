# P3 percent revenue-share cue — 2026-11-15

- Status: implemented and regression-tested; P3 overall remains NOT PASSED.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`.
- Base: NO_GIT snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Changed files: `src/datamate/understanding.py`, `tests/test_understanding.py`, this checkpoint, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `tools/STATE.md`.
- `understanding.py` SHA-256: `1C8B9C94C6BE480C860C922F676C5FE83409E9E9CE80BF6BD574D2053389BE92`.
- `test_understanding.py` SHA-256: `98CA80F037D2FF1320327647132B9927EF474B1DC4BB87F2DB46017F41F7E24C`.

## Finding and correction

A synthetic question asking what percentage of store revenue is represented by prescription medicine was classified as total revenue even though it contained `%`, the subject category, revenue, and the contribution verb “chiếm”. The focused regression failed before the fix.

Added a narrow revenue-share rule for percent-marked questions that contain revenue, a contribution cue (`chiếm` or `đóng góp`), and a subject/category term. Existing total-revenue and share rules remain unchanged.

## Verification

- Before fix: synthetic regression predicted `revenue`; expected `revenue_share`.
- After fix: `PYTHONPATH=src python -m unittest tests.test_understanding -v` — 8/8 passed.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 77 run, 74 passed, 3 Git-dependent hygiene skips; exit 0.
- No holdout replay, answer-label/public-test access, or Git operation occurred. Question-only development records remain ignored and excluded from archives.
- P3 remains NOT PASSED; no independent full-slot metric supports the 81% gate.

## Next

Continue P3 only with synthetic or separate question-only development cases. Preserve all inspected holdouts. Before any acceptance claim, freeze parser and obtain independent full-slot review, including business-level and ambiguity-positive reporting.

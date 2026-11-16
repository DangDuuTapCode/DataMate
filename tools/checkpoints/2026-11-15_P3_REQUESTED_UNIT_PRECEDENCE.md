# P3 requested-unit precedence — 2026-11-15

- Status: implemented and regression-tested; P3 overall remains NOT PASSED.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`.
- Base: NO_GIT snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Changed files: `src/datamate/understanding.py`, `tests/test_query_schema.py`, this checkpoint, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `tools/STATE.md`.
- `understanding.py` SHA-256: `463073091ADAB75FCB4FBA1958232E82E62DF52D0CBAA1935580E99807032B39`.
- `test_query_schema.py` SHA-256: `2B2AD96C7E5BA2E90461ADAD6C69DDA0527E6D4D705C5345906483DA564AD332`.

## Finding and correction

A synthetic question asking for the average cost of one tube of a product described as containing ten tablets returned `viên` from the product packaging rather than the requested `tuýp`. The new focused regression failed before the fix.

Added the `tuýp` alias and made explicit unit phrases after `một`, `mỗi`, or `từng` take precedence over other units mentioned in the product description. Existing unit fallback behavior remains for questions without that requested-unit construction.

## Verification

- Before fix: focused synthetic regression failed (`viên` predicted, `tuýp` expected).
- After fix: `PYTHONPATH=src python -m unittest tests.test_query_schema -v` — 6/6 passed.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 76 run, 73 passed, 3 Git-dependent hygiene skips; exit 0.
- No holdout replay, answer-label/public-test access, or Git operation occurred. The inspected question-only development records remain in ignored local logs and are excluded from archives.
- P3 remains NOT PASSED; no independent full-slot acceptance metric supports the 81% target yet.

## Next

Continue P3 with synthetic or separately selected question-only development cases. Freeze all inspected holdouts. A future acceptance result requires a frozen parser, independent full-slot annotations, adequate positive ambiguity cases, and per-business reporting.

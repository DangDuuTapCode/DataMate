# P3 supplier-ranking QuerySpec — 2026-11-15

- Status: implemented and regression-tested; P3 overall remains NOT PASSED.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`.
- Base: NO_GIT snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Changed files: `src/datamate/understanding.py`, `tests/test_understanding.py`, this checkpoint, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `tools/STATE.md`.
- `understanding.py` SHA-256: `C4721BF01AD10FF24262E103AF278EAA9B09237D700F67D0A346196CA420AB15`.
- `test_understanding.py` SHA-256: `0A77476F9709834220903772E843DA7B99A3873BD6FB704EFF4B114C3D06D281`.

## Finding and correction

A synthetic “which supplier has the greatest value of received goods” question was misclassified as product sales ranking. Added a supplier-specific ranking rule that records `supplier_ranking`, the `supplier` dimension, `supplier_purchase_amount`, descending sort, and the requested `top_k` slot.

Supplier purchase ranking remains non-executable because the metric is not in the engine allowlist. The structured QuerySpec preserves the understood request without returning an unsupported answer.

## Verification

- Before fix: synthetic regression failed (`sales_ranking` predicted; `supplier_ranking` expected).
- After fix: `PYTHONPATH=src python -m unittest tests.test_understanding -v` — 9/9 passed.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 78 run, 75 passed, 3 Git-dependent hygiene skips; exit 0.
- No holdout replay, answer-label/public-test access, or Git operation occurred. Question-only development logs are excluded from archives.
- P3 remains NOT PASSED; no independent full-slot score supports the 81% target.

## Next

Continue P3 using synthetic or separate question-only development cases. Keep inspected holdouts frozen. Supplier ranking execution is a later workstream and needs a verified supplier/purchase schema before it can be safely added to the execution allowlist.

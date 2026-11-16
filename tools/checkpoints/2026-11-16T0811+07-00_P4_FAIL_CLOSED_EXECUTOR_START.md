# P4 executor hardening — start checkpoint

- Time: 2026-11-16 08:11 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`; isolated no-Git snapshot based on `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User direction: skip the independent-review wait for P3 and move on. P3 remains **NOT VERIFIED / NOT PASSED**; no acceptance metric is inferred or fabricated.
- Docker work is out of scope for this continuation.

## Finding

`src/datamate/metrics.py` chooses the largest table when multiple tables match a fact schema. It also drops unparseable numeric values and date rows, which can turn incomplete input into a confident partial total. Revenue returns zero when no in-period rows match, conflating no data with an observed zero.

## Bounded scope and allowlist

- Fail closed on ambiguous source tables, unparseable date rows, and invalid numeric values for in-scope calculations.
- Distinguish no matching data from a genuine zero total.
- Add synthetic regression tests only; do not open train answer labels or public/private test content.
- Allowlist: `src/datamate/metrics.py`, `tests/test_pipeline.py`, `tools/STATE.md`, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, `docs/CHANGELOG_WORK.md`, and this checkpoint.

## Acceptance evidence to collect

- New regressions demonstrate the old partial/ambiguous behavior and pass after the fix.
- Focused pipeline tests and complete unittest suite pass.
- `git diff --check` is unavailable because this snapshot has no `.git`; inspect whitespace and changed-file allowlist directly.
- No source archives, `sources/`, official checkout, branch, or Git history are modified.

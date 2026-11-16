# P5 structured executor failure reasons — start checkpoint

- Time: 2026-11-16, Asia/Bangkok.
- Working copy: isolated no-Git snapshot, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User chose to skip the P3 independent reviewer; P3 remains **NOT VERIFIED / NOT PASSED**. Docker is out of scope.

## Objective

Emit stable internal reason codes when a supported query abstains because a required source column is missing, a requested unit is not supported by source data, or answering would require an unsafe join. Keep output-only `verify()` and organizer-facing JSONL backward-compatible.

## Initial state

`verify.py` already declares `missing_column`, `invalid_unit`, and `join_unsafe`, but `Executor.execute()` only returns `None`; the runner therefore reports these cases as generic `insufficient_evidence`.

## Allowlist

- `src/datamate/metrics.py`
- `src/datamate/verify.py`
- `src/datamate/main.py`
- `tests/test_pipeline.py`
- `tests/test_api.py`
- This checkpoint and completion checkpoint; `tools/STATE.md`, progress, handoff, changelog.

## Acceptance evidence

- Synthetic tests exercise each structured reason and verify the submission record remains `{"id": ..., "type": "abstain"}`.
- Focused tests and complete suite pass.
- P5 remains partial if other rubric gates (source/denominator/reconciliation and false-answer review) remain unmet.

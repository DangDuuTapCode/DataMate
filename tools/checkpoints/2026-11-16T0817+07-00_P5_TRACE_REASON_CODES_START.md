# P5 abstention reason codes — start checkpoint

- Time: 2026-11-16 08:17 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on feature commit `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User direction: proceed without waiting for P3 independent review; P3 remains NOT VERIFIED / NOT PASSED. Docker is out of scope.

## Bounded objective

Add stable internal abstention status/reason codes to execution traces while preserving the existing submission JSONL schema. Cover unsupported intent, missing time, insufficient evidence, missing source, and ingestion parse failure using synthetic tests.

## Allowlist

- `src/datamate/verify.py`
- `src/datamate/main.py`
- `tests/test_api.py`
- `tests/test_pipeline.py`
- `tools/STATE.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/CHANGELOG_WORK.md`
- This checkpoint and a completion checkpoint.

No train answer labels, public/private test content, source archives, official checkout, Git metadata, or Docker tools are in scope.

## Acceptance evidence

- Trace reason code is in the documented stable allowlist and appears for abstentions.
- Submission output remains `{"id": ..., "type": "abstain"}` with no added fields.
- Focused API/verifier tests and complete suite pass.
- P5 remains partial unless source/column/units/reconciliation checks and false-answer evaluation are also proven.

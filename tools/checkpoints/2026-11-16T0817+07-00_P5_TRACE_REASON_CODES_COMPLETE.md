# P5 abstention reason codes — completion checkpoint

- Time: 2026-11-16 08:20 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User direction: skip the P3 independent-review wait and continue. P3 remains **NOT VERIFIED / NOT PASSED**. Docker work is out of scope.

## Changes

- Added stable trace reason codes in `src/datamate/verify.py`: `unsupported_intent`, `ambiguous_entity`, `missing_time_range`, `missing_column`, `parse_failure`, `source_unavailable`, `invalid_unit`, `join_unsafe`, `insufficient_evidence`, and `verification_failed`.
- Added `verify_with_reason`; retained `verify` as an output-only compatibility wrapper.
- Runtime traces now include `verification` status/reason and a serialized, versioned `query_spec`. Submission JSONL remains `{"id": ..., "type": "abstain"}` for abstentions and does not gain trace-only fields.
- Main runner maps missing source files to `source_unavailable`, typed ingestion failures to `parse_failure`, missing temporal scope to `missing_time_range`, and unsupported interpretations to `unsupported_intent`.
- Added synthetic tests for missing time, insufficient evidence, source unavailable, ingestion parse failure, trace decision metadata, and submission schema preservation.

## Verification

- Focused command: `PYTHONPATH=src python -m unittest tests.test_api tests.test_pipeline -v` — exit 0; 20 passed.
- Full command: `PYTHONPATH=src python -m unittest discover -s tests -v` — exit 0; 90 run, 87 passed, 3 skipped. Skips require `.git`, absent by design in this isolated snapshot.
- SHA-256:
  - `src/datamate/verify.py`: `40F3D5F8C77EC2863FE2AAD947681931AC1804165F4650248DAE729A33BFE814`
  - `src/datamate/main.py`: `120BCCA18D35310D89C94F148A7FE7841531C0B1AE577B162CB8084DC5EC2F5F`
  - `tests/test_api.py`: `A388DBA5289B5D02DD8C0A850D8E69ECCA37B8EE8B1A1485278F43A88160489D`
  - `tests/test_pipeline.py`: `D639844457272430382901DA904F3F1DE294D123EFB6CB89A516B2C71CA1168C`

## Limitations and next action

- P5 remains **IN PROGRESS**, not accepted. `missing_column`, `invalid_unit`, and `join_unsafe` are reserved codes not yet emitted from structured executor outcomes. Source availability, denominator/null/reconciliation checks, adversarial coverage and false-answer evaluation are incomplete.
- P4 remains in progress; its separate checkpoint lists remaining operators, declared joins, business rules, and replay criteria.
- Next: implement a reproducible train-only two-stage replay. Freeze and hash predictions before the evaluator opens train labels; report unsupported scope and per-business/per-intent metrics. Do not use public test for tuning.

No train answer labels, public/private test content, source archives, `sources/`, official checkout, branch, Git history, or remote was modified or accessed in this work item. No commit or push occurred.

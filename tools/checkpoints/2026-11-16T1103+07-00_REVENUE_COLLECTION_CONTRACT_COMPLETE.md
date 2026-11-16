# Revenue versus collected-money contract — implementation complete

- Completed: 2026-11-16 11:03 Asia/Bangkok.
- Started from `tools/checkpoints/2026-11-16T1043+07-00_REVENUE_COLLECTION_CONTRACT_START.md`.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated, no `.git`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 reviewer is skipped at the user's direction. P3 remains **NOT VERIFIED / NOT PASSED**. P4/P5/P6 remain below acceptance and are not claimed complete.

## Business rule implemented

- The user set default revenue to order value after discounts.
- Explicit collected/paid questions now use a separate `collected_amount` QuerySpec/plan intent. The executor sums one unambiguous payment-event table by its explicit receipt/payment date and amount field. It excludes pending/failed/canceled statuses through the existing status guard.
- Revenue field selection now prefers order-total/receivable headers (`Tổng đơn`, `Phải thu`, equivalent generic headers) over subtotals. Revenue still excludes payment tables.
- The executor abstains if the payment-event table, date, amount, period rows, or parseable values are not supported. It never substitutes order totals, remaining debt, or a current paid-balance snapshot for money received during a period.
- Requests for both revenue and collected money, or ranking collected money, are represented as non-executable intents rather than collapsed into one scalar.
- Source evidence in biz_127 and biz_129 READMEs supports the order-total, paid-summary, line-total, payment-event, and payment-date distinctions. No business-ID-specific logic or answer value was added.

## Files changed in this slice

- `src/datamate/metrics.py`
- `src/datamate/understanding.py`
- `tests/test_pipeline.py`
- `tests/test_understanding.py`
- `tests/test_query_schema.py`

## Verification

- Focused regression set: 9 passed, exit 0. Covers metric separation, QuerySpec schema, split receipts by receipt date, pending payment exclusion, missing/ambiguous event evidence, gross order total priority, and non-collapsing multi-metric requests.
- Live data smoke (read-only) for biz_127 and biz_129: default revenue selected `don_hang`; explicit collected amount selected `thanh_toan`; all four executions produced an answer without runtime error. Monetary answer values were not printed. This verifies available source rows and headers, not train-label correctness.
- Full suite after final source/test changes: `PYTHONPATH=src python -m unittest discover -s tests -v` — exit 0; 127 run, 124 passed, 3 repository-hygiene tests skipped because this isolated copy has no `.git`.

## Frozen train replay v8

- Prediction generation: `PYTHONPATH=src python tools/replay_predictions.py --data-root ..\..\evaluation\train-inputs-2026-11-16 --output-dir ..\..\evaluation\p6-train-replay-v8-revenue-collection-2026-11-16` — exit 0; 3,000 questions / 30 businesses; freeze says `answer_labels_accessed=false`.
- Pre-evaluation validation: `validate_frozen_replay()` passed; 3,000 prediction records and 3,000 matching traces; input manifest matches v7; code manifest matches current `src/datamate` and schema files.
- Evaluator command, run only after freeze/ID/hash validation: `PYTHONPATH=src python tools/evaluate_replay.py --replay-dir ..\..\evaluation\p6-train-replay-v8-revenue-collection-2026-11-16 --data-root ..\..\evaluation\train-inputs-2026-11-16 --train-archive ..\..\..\sources\train.zip --report ..\..\evaluation\p6-train-replay-v8-revenue-collection-2026-11-16\evaluation_report.json` — exit 0. The evaluator is the only step that opened train answer labels.
- Replay report: `work/evaluation/p6-train-replay-v8-revenue-collection-2026-11-16/evaluation_report.json`, SHA-256 `22f5277a408551aaf95a1aacfc921da8a658109fb6e44c4ad7557f6f20b7b64c0`.
- Freeze manifest SHA-256: `cca232397eb2041d165b505a1fd378d86daa2bea92c58c94db437abf78247af3`.
- Prediction SHA-256: `18127e7d8d78dc90ff7d64ad1e275a1c727248ecc2c2ef4dafca0a4a29d28c59` (identical to v7; all prediction records are unchanged).
- Trace SHA-256: `53af920b29f27ad7c9ac422906646e58bee5f31a425d512063d2514eac357f2a`.
- Code manifest SHA-256: `83e40ed01258b863f40afc871c2d4d806d1a83e6a2bfe61e9ab718fa7d8f86b2`.
- Input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`.
- Train-answer archive SHA-256: `0b5fe9d13edf5fae306bda9cafaf699c06b639846c8e1d9e41c39a86d1160b3d`.
- Metrics: 47 correct, 37 wrong, 2,916 abstain; PA 0.003333 (0.33%); answer coverage 2.80%; answered accuracy 55.95%; 70/70 unanswerable cases correctly abstained; runtime errors `{}`; p95 35 ms.
- Versus v7, predictions, correctness counts and answer quality are identical. This slice clarifies metric meaning and supports explicit payment-event questions, but did not improve train PA or answer coverage. The replay is in-sample and below acceptance; no independent/generalization claim.

## Failed attempts and corrections

- New red regressions initially failed as expected: no distinct collected-money intent/executor existed. The implementation then made them pass.
- The first edited `debt_payment` condition had a missing closing parenthesis; focused import/test caught the `SyntaxError`, which was corrected before the passing run.
- English `collected amount this month` is recognized as a structured collected-money intent, but the period resolver does not recognize that English relative-time phrase. The test now correctly expects a non-executable QuerySpec with `temporal_scope_not_executable`, preserving fail-closed time behavior.
- An initial frozen-replay validation one-liner omitted `tools` from the import path; it did not open labels. Re-running through `tools.replay_predictions` passed all freeze, input, code, ID, and trace checks.
- An initial exploratory smoke helper had a malformed lambda, and the next attempt omitted `PYTHONPATH`; both were read-only diagnostics. The corrected PowerShell here-string smoke completed for both businesses.

## Limits and next work

- v8 predictions matching v7 means existing train questions did not exercise the new collected-money intent; synthetic regressions and the real-data smoke verify its generic path.
- P3 reviewer remains skipped; P3 is NOT VERIFIED / NOT PASSED. P4/P5/P6 and the remaining Playbook workstreams stay in progress; no ≥81% result is claimed.
- Next: analyze only the already-frozen train evaluation errors for generalizable categories, then address the highest-impact non-business-specific cause. Do not tune on Public Test or inspect hidden labels.
- No Docker, official checkout, Git branch, source archive, ACL, commit, push, merge, or reset action was performed.

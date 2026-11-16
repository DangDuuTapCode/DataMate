# P5 structured executor failure reasons — completion checkpoint

- Time: 2026-11-16 09:33 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 independent reviewer was skipped at the user's direction. P3 remains **NOT VERIFIED / NOT PASSED**. Docker is out of scope. No commit, push, merge, or official-checkout write occurred.

## Implemented

- Added `Executor.execute_with_reason()` while retaining `execute()` compatibility.
- A supported query with no required date/metric/order/status/product column emits `missing_column`.
- Sales ranking that needs a product-name lookup but only has product codes, or relies on an inventory ledger, emits `join_unsafe`.
- Quantity/ranking with an explicit requested unit abstains with `invalid_unit` if the source lacks a unit column or its observed units do not match the requested unit. Matching units may execute; conversion remains unsupported.
- The runner passes this failure reason to the verifier. Reasons stay inside `trace.jsonl`; organizer-facing `submission.jsonl` remains unchanged.

## Verification

- Focused pipeline + API tests before the final two trace tests: 32/32 passed. The complete suite after all changes: 108 run, 105 passed, 3 Git-dependent hygiene checks skipped, exit 0.
- Regression coverage verifies each of `missing_column`, `invalid_unit`, and `join_unsafe` in traces and confirms abstention serialization stays `{"id":"q","type":"abstain"}`.
- Latest source hashes:
  - `metrics.py`: `8C9B5394B9E1D531269CF77ADEE4BBF5DB49071ED15CC868F37BA95FFCCEAF41`
  - `verify.py`: `5DFD1F8C22F3743ADEDB7C057BDBECB78E79C9B6CC5917C2FB22234AA721359E`
  - `main.py`: `2AB796038E674BD9043EE23A674F9578C47E6BF47C0560162211E51DE74B4731`
  - `test_pipeline.py`: `76C935AB83CB516D49A079E7FF45EF032A42F63EB1BDD0BE7C1F78B05AA227B3`
  - `test_api.py`: `6A467689A261D9CAB447CF7B7A6D332C56792AA7B03F84D9724681E35EAAA5C4`

## P6 full train diagnostic after prediction freeze

- Replay: `work/evaluation/p6-train-replay-v5-full-2026-11-16`; 3,000 questions across all 30 businesses. Prediction generation recorded `answer_labels_accessed=false`; the evaluator validated the frozen prediction/input/code manifests before opening train answers.
- Metrics: 45 correct, 60 wrong, 2,895 abstentions, PA `-0.005`, answer coverage `3.5%`, answered accuracy `42.86%`, false-answer rate `57.14%`, 70 correctly abstained on 70 unanswerable examples, p50 `0 ms`, p95 `97 ms`, runtime errors `{}`.
- Compared with v3 (`PA -0.01267`, 40 correct, 78 wrong), v5 improved 5 correct and removed 18 wrong answers. It remains an **in-sample diagnostic**, not an independent acceptance holdout; train questions were used for prior question-only diagnostics/development. It is far below the playbook target.
- Abstention reason counts: `ambiguous_entity` 658, `insufficient_evidence` 687, `invalid_unit` 14, `join_unsafe` 5, `missing_column` 319, `missing_time_range` 59, `unsupported_intent` 1,153.
- Wrong answers by intent: cancellation_rate 2, order_count 2, quantity 2, revenue 53, sales_ranking 1. Revenue errors are concentrated in biz_127 (31) and biz_129 (15); do not tune with IDs/labels. Investigate semantics from source schema and tests.

## Replay integrity

- Prediction SHA-256: `393b75e4e3952281b3a4f4398b4af528219dc69b4e7c9b22b03399ee5420936e`.
- Trace SHA-256: `d4fd07a6bc9a04a145c927215c545792fe6f2ccd9dea1bf13a5a9152f391dab9`.
- Input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`.
- Code manifest SHA-256: `a0f76c3b789f5591a9a69b2282e7622852d703dba10d30041a06e6f48e9eb041`.
- Freeze manifest SHA-256: `285236cae00bd24d97fc3a5ff40e1b969841cf2b6afc9f5a0151491cdceb86ff`.
- Input dataset is the read-only extraction of train questions and business data; source `sources/train.zip` was not modified. No Public Test content or labels were used.

## Status and next exact action

- P5 is **IN PROGRESS / NOT ACCEPTED**: the new reason codes are emitted, but answered false-rate is still 57.1%, and denominator/reconciliation/trace completeness gates need broader validation.
- P6 is **IN PROGRESS / NOT ACCEPTED**: replay is reproducible and hash-guarded, but accuracy is negative, data is in-sample, and no SLM/offline benchmark has been justified or measured.
- Next: inspect high-impact revenue failures through generic QuerySpec/filter/time and source semantics, add only source-grounded regressions, then work toward P7 business-level coverage. Keep all frozen predictions immutable.

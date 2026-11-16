# P6 checkpoint — inbound purchase exclusion and base quantity ranking (2026-11-16)

## Scope and safety

- User direction: focus on demonstrable bug fixes; do not change unrelated behavior.
- Edited only `src/datamate/metrics.py` and `tests/test_pipeline.py` in the isolated snapshot `work/rehydrated-2026-11-15-P3/source`.
- No Git metadata exists in that source snapshot. The official repository, main branch, and synced `sources/` were not modified. No commit, push, portal action, or public-label access occurred.
- No question ID, expected answer, or row-specific value was hardcoded.

## Changes

1. Added conservative source-role detection for inbound purchasing ledgers, including compact Vietnamese names such as `SoNhapHang`, spaced variants, and purchase/inbound aliases. Purchase ledgers are excluded from revenue candidate discovery, safe daily-revenue line discovery, quantity and sales-ranking facts, order counts, cancellation-rate source selection, and matching failure-reason source scans.
2. Reordered quantity aliases so normalized/base-unit headers (`SL lẻ`, `Số lượng lẻ`, base quantity and equivalent documented labels) are preferred over raw/package quantity headers.
3. Added three pipeline regressions covering purchase-only abstention, purchase-versus-sales source selection, and base-unit ranking where raw-unit ranking differs.

## Verification

- Focused command: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 56/56 passed.
- Full command: `PYTHONPATH=src python -m unittest discover -s tests -v` — 167 run; 164 passed; 3 Git-dependent hygiene skips because this snapshot has no `.git`; exit 0.
- One initial focused run exposed that the real `SoNhapHang` table name is concatenated; added that observed naming variant and reran all 56 focused tests successfully.
- Fresh train replay command used `tools/replay_predictions.py` against `work/evaluation/train-inputs-2026-11-16-with-split-metadata`, outputting to `work/evaluation/p6-train-replay-v19-purchase-baseqty-2026-11-16`. Freeze says 3,000 questions, 30 businesses, `answer_labels_accessed=false`.
- Frozen provenance: code manifest `0e341e7d913b4c4219d155724297bd9f403551428de177abfc1c6f7cc4dcd12f`; input manifest `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; predictions `5f168fe9b624a78c9b99e314020acbe28ae0e04677346a3f1750bd6676c73805`; traces `f8fdcad5b1e525fb58b8df574cca7d4b47c2bbb637eca9934ee6b70ac791c358`.
- After freeze validation, evaluator reported 30 correct, 4 wrong, 2,966 abstain / 3,000; coverage 1.1333%; answered accuracy 88.24%; false-answer rate 11.76%; penalized accuracy 0.8667%; p95 21 ms; runtime errors 0. Prior v18 was 28 correct, 10 wrong, 2,962 abstain and PA 0.6000%. Train result is in-sample diagnostic, not independent acceptance/generalization.
- Remaining wrong train outputs: one biz_125 May-2025 sales-ranking label differs from code's normalized quantity total by 3 units; three cancellation-rate labels appear to include delivery-failed orders while current rulebook says cancellation numerator is canceled-only. These are not silently tuned. The latter requires resolving business-rule/label mismatch before changing semantics.

## Public output

- One public inference run was started against the extracted question-only inputs at `work/evaluation/public-input-2026-11-16-v1`, writing to the new path `work/submission-build/public-submission-2026-11-16-v19/public_submission.jsonl` and logs under the sibling `logs/`.
- No public answer file was present or read. At checkpoint creation, inference was still running; do not overwrite or start a second pass. After completion, validate JSONL schema, ordered IDs/count, trace count/runtime errors, and record SHA-256. Do not claim public accuracy.

## Source checksums

- `src/datamate/metrics.py`: `C624C373FE31F90FD70DEA4F781CDFCFD3C6968394BCD3EA3CD53769A485BBBD`
- `tests/test_pipeline.py`: `A65B5E4C25D448B87AD48B7EC6C213B18F32DA2131FB56557B651B87C120D566`

## Next

Complete the existing public inference only, validate its format and runtime logs, record counts/hash, and update state/progress/handoff. Keep the two unresolved train issues explicit.

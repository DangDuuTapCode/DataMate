# P6 — exported summary rows double-counted as sales lines

**Status:** bounded fix completed; train-only in-sample replay evaluated. This is not independent acceptance evidence.

## Root cause

The biz_130 sales workbook contains `TỔNG NGÀY ...` and `Tổng tháng ...` rows inside the line-item table. Those rows have blank order/date/status cells and an amount. The merged-order metadata forward-fill treated the summary text in `Tên hàng hóa` as a product row and attached the previous order/date/status. In April 2026, this added 31 summary rows totaling 2,803,347,000 to 9,673 true dated line rows totaling 1,401,673,500, producing a false 4,205,020,500 aggregate. The successful-order amount is near the train reference after excluding unsuccessful orders.

## Changes

- `src/datamate/metrics.py`: recognize exported subtotal/total labels; skip them in date-range discovery and period execution; reset forward-filled order metadata at a summary row. Source `Table.rows` remain unchanged.
- `tests/test_pipeline.py`: add a regression for daily and monthly totals interleaved with merged order metadata.
- No data, labels, public test content, Git history, official checkout, or submission artifact was changed in this bounded work item.

## Verification

- Focused pipeline suite: `PYTHONPATH=src python -m unittest discover -s tests -p test_pipeline.py -v` — 62 passed.
- Complete suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 174 run, 171 passed, 3 Git-dependent skips, exit 0.
- Fresh label-free v22 replay: `PYTHONPATH=src python tools/replay_predictions.py --data-root ..\..\..\work\evaluation\train-inputs-2026-11-16-with-split-metadata --output-dir ..\..\..\work\evaluation\p6-train-replay-v22-summary-row-exclusion-2026-11-16 --source-root .`
- Freeze validation passed for all 3,000 predictions/traces, ID/order/schema and manifests. `answer_labels_accessed=false` before evaluation. Input manifest SHA-256: `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; code manifest: `739566b3d05fe7b2ad0ae9291e40d9433562cb778e4be33ecb20ed859a743f66`; predictions: `86d4f7ddbbbc71bb23f233af71e050db496c5e1f126989b4548f0673` (full hash in `freeze_manifest.json`); traces: `6bec3d970526805a870ad195a7f5a3fd7ac928d53451318e7c1740560cd78068`.
- Train-only evaluator command: `PYTHONPATH=src python tools/evaluate_replay.py --replay-dir ..\..\..\work\evaluation\p6-train-replay-v22-summary-row-exclusion-2026-11-16 --data-root ..\..\..\work\evaluation\train-inputs-2026-11-16-with-split-metadata --train-archive ..\..\..\work\submission-build\context-final-verified-2026-11-15\training_code\data\train.zip --report ..\..\..\work\evaluation\p6-train-replay-v22-summary-row-exclusion-2026-11-16\score-report.json`
- v22 result: 181 correct, 54 wrong, 2,765 abstain / 3,000; coverage 7.833%; answered accuracy 77.02%; false-answer rate 22.98%; penalized accuracy 4.233%; runtime errors 0; p95 664 ms. v21 comparison: +12 correct, −12 wrong, same abstentions; answered accuracy rose 71.91% → 77.02%.
- These are in-sample train diagnostics only. Public labels were not read.

## Risks and next work

- 47/54 remaining wrong answers are tagged as revenue. Highest-evidence categories are unexecuted order-count/threshold filters, multi-month list/trend/ranking questions treated as scalar revenue, and medication/category filters silently ignored.
- Add generic order-count/threshold intent handling; fail closed for unimplemented active-ingredient and OTC filters; detect unsupported multi-month output operators before scalar revenue execution. Add regression tests and replay from a new output path.
- v22 p95 latency is higher than v21 (664 ms vs 494 ms). Profile the new summary-row check and cache/optimize it without changing behavior before another full replay.
- Keep reviewer status skipped/not verified/not passed. Do not use public questions for tuning, do not inspect public/private labels, and do not commit/push/submit.

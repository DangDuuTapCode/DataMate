# Shared unsuccessful-order status convention — implementation complete

- Completed: 2026-11-16 11:54 Asia/Bangkok.
- Started from `tools/checkpoints/2026-11-16T1126+07-00_UNSUCCESSFUL_ORDER_STATUS_RULE_START.md`.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated/no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 reviewer remains skipped at the user's direction; P3 is **NOT VERIFIED / NOT PASSED**. This slice does not establish any Playbook phase acceptance threshold.

## User-approved business convention

- Preserve the source status value unchanged and distinguish canceled (customer/system), returned after delivery, and failed delivery. All three classes contribute to the numerator of DataMate's unsuccessful-order rate (the existing question intent is `cancellation_rate`).
- Keep pending and in-transit separate; they are not unsuccessful outcomes. Count unique order IDs in the denominator.
- If an in-period order has a missing/unrecognized status, if an order has conflicting outcome classes, or if no exact documented order-status field is available, abstain. Do not infer from customer status or e-invoice status.
- Exact aliases are used only: order-status headers include `Trạng thái đơn`, `Trạng thái đơn hàng`, generic `Trạng thái`/`Tình trạng`/`Status`, and README-confirmed `Kết quả`, `Ghi chú TT`, `Trạng thái xử lý`, or `Xử lý`. Substring matches are no longer used for order-status resolution.
- `Đổi trả` is mapped to returned; `Không giao được` is mapped to failed delivery. The raw column remains unchanged in the `Table` source records.

## Changed files

- `src/datamate/rules.py` — added explicit, non-mutating order-status classifier and unsuccessful class set; revenue filter reuses the known outcome classes while retaining existing nonfinal-status exclusions.
- `src/datamate/metrics.py` — added exact documented order-status header matching; cancellation-rate calculation groups the three unsuccessful classes by unique order ID and abstains on unknown/missing/conflicting statuses.
- `tests/test_pipeline.py` — five new regressions for distinct classes/shared numerator/raw preservation, `Ghi chú TT`, unknown/missing statuses, customer/e-invoice header false positives, and repeated lines. Updated two older in-transit expectations now that `Đang giao` is classified consistently as in-transit.
- `docs/BUSINESS_COVERAGE.md` — records the global rule and v9 diagnostic.
- `tools/STATE.md`, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `docs/CHANGELOG_WORK.md` — updated progress and handoff.
- This completion checkpoint; the start checkpoint remains intact.

## Source evidence and smoke checks

- Read-only README/profile evidence marks biz_101 `Kết quả` as order status and biz_113/117 `Ghi chú TT` as order status; biz_116 `Trạng thái` is order status. biz_108 has both order `Trạng thái` and a separate `Trạng thái HĐĐT`, so exact matching avoids incorrectly selecting the latter.
- Read-only train-source value check, without labels: biz_101's four values (`Xong`, `Đã hủy`, `Đổi trả`, `Đang giao`) classified as successful, canceled, returned, and in-transit; biz_116's seven values (`ok`, `Thành công`, `khách hủy`, `Không giao được`, `trả hàng`, `Đã trả hàng`, `Đang vận chuyển`) classified across the expected five groups, with zero unknown status rows in both checked businesses.
- Full-period executor smoke: biz_101 4.60%, biz_116 2.47%. These are raw-data diagnostics, not label validation.

## Tests

- Initial focused command without source path: `python -m unittest tests.test_pipeline -v` failed to import `datamate`. Reran with `PYTHONPATH=src`.
- The first focused run with the new code found that English `cancelled` was not classified as cancellation and that prior synthetic expectations still counted `Đang giao` as final; fixed the classifier and updated those in-transit expectations.
- Focused regression: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 35 passed, exit 0.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 132 run, 129 passed, 3 Git-dependent hygiene tests skipped because the working copy has no `.git`; exit 0.

## Frozen v9 train replay and evaluator result

- Prediction command: `PYTHONPATH=src python tools/replay_predictions.py --data-root ..\..\evaluation\train-inputs-2026-11-16 --output-dir ..\..\evaluation\p6-train-replay-v9-order-outcomes-2026-11-16` — exit 0; all 30 businesses and 3,000 questions; freeze records `answer_labels_accessed=false`.
- `validate_frozen_replay()` passed for the 3,000 predictions and 3,000 matching traces; input manifest and current source code manifest matched. Labels were read only afterward by the evaluator.
- Evaluator command: `PYTHONPATH=src python tools/evaluate_replay.py --replay-dir ..\..\evaluation\p6-train-replay-v9-order-outcomes-2026-11-16 --data-root ..\..\evaluation\train-inputs-2026-11-16 --train-archive ..\..\..\sources\train.zip --report ..\..\evaluation\p6-train-replay-v9-order-outcomes-2026-11-16\evaluation_report.json` — exit 0.
- Scope: train only, 3,000 questions/30 businesses; explicitly in-sample diagnostic, not an independent acceptance holdout.
- Metrics: 40 correct, 44 wrong, 2,916 abstain; PA -0.001333 (-0.13%); answer coverage 2.80%; answered accuracy 47.62%; false-answer rate 52.38%; 70/70 gold-unanswerable questions correctly abstained; p95 42 ms; runtime errors `{}`.
- Intent error counts: revenue 30; cancellation_rate 12; quantity 1; sales_ranking 1; order_count 0. V8 had cancellation_rate 2 wrong, order_count 2 wrong, quantity 2 wrong, revenue 30 wrong, sales_ranking 1 wrong. Overall v9 has seven fewer correct and seven more wrong than v8 with unchanged coverage.
- The new cancellation-rate results are less aligned with the train references (2 correct/12 wrong among 14 answered, versus v8 12/2). This is recorded as a convention mismatch signal; no answer-specific or label-driven tuning was performed. The explicit user-approved status semantics remain authoritative unless the user changes them.

## Integrity hashes

- Code manifest SHA-256: `b0615af156d7d0502823593c44f7c404933dec4b9c05cbf841e8181f265c9b57`.
- Input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`.
- Prediction SHA-256: `76fc89bc51e96f96f67b434c79ebcbf1b56777b50d867493cadc7e19b2950fa8`.
- Trace SHA-256: `7ab1077e91debed56cac0a29df619045a7f6316eaab7b01192c41b907bc442d8`.
- Freeze manifest SHA-256: `df958e2b71eeadefef685ac4e7186c88f834931e3327adb69a23b37ca213e90e`.
- Evaluation report SHA-256: `8a5af3ef640afb7b458457ffd2f626f6217da41d0ff6534b60886f466f6411eb`.
- `src/datamate/rules.py` SHA-256: `9e981f8183ee74806b572f77a4ecd88190ebee1488dd873f2cc1e671922c2abc`.
- `src/datamate/metrics.py` SHA-256: `c1684081523a9d04a14aa50f658da4236caac2d5b53ba9f485b73206fd72c243`.
- `tests/test_pipeline.py` SHA-256: `084ce7c6917b448de815bbad8bd0134effb9b1a93187fef34c2d4cdec11fb704`.

## Limits and next step

- The code change improves conformance to the explicit business rule but train-reference cancellation-rate accuracy declined. Do not silently redefine the metric to chase labels; keep the mismatch visible and focus the next work on other generalizable release gaps.
- This working copy has no Git metadata. No official checkout, Git branch/history, source archive, Public Test data, Docker image, ACL, or permissions were changed. No commit or push occurred.
- P3 reviewer skipped; P3 remains **NOT VERIFIED / NOT PASSED**. P7 L5 remains 0/30; no ≥81% phase claim is made.

# CURRENT STATE — 2026-11-16 — summary-row bug fixed; P6 error reduction continues

## Latest completed bounded fix — 21:49 GMT+7

- Fixed double-counting of exported `TỔNG NGÀY` / `Tổng tháng` rows embedded in sales detail. Root cause, exact row/sum evidence, tests and replay hashes: `tools/checkpoints/2026-11-16T2149+07-00_P6_SUMMARY_ROW_DOUBLE_COUNT_FIX_COMPLETE.md`.
- Full suite: 174 run, 171 passed, 3 Git-dependent skips. v22 validated then scored on train: 181 correct, 54 wrong, 2,765 abstain / 3,000; answered accuracy 77.02%, penalized accuracy 4.233%, zero runtime errors. In-sample diagnostic only.
- Compared with v21: +12 correct and −12 wrong, same abstentions. biz_130 ordinary monthly/day revenue was corrected; remaining errors mainly show unsupported count thresholds, multi-month output operators and silently ignored business filters.
- Next: implement generic order/threshold count semantics; fail closed for unsupported active-ingredient/OTC filters and multi-month scalar misroutes; add regressions. Profile the v22 p95 increase (664 ms vs 494 ms) and optimize summary-row checks safely.
- Current code changes in this slice: `src/datamate/metrics.py`, `tests/test_pipeline.py`. No Git repository exists in this isolated snapshot; no commit/push/official checkout changes.

## Active P6 work item — daily revenue threshold day count — started 17:08 GMT+7

- Continuing from v16's validated train-only diagnostic. It recorded 26 correct, 4 wrong, 2,970 abstentions / 3,000, with 1.00% answer coverage and 0 runtime errors; this is in-sample and not acceptance evidence.
- Trace inspection found a generic routing gap: “how many days ... sales at least 15,000,000 VND” was routed to quantity and answered from an incoming-purchase quantity table (4,291 vs train reference 8). The intended generic operation is count distinct dates whose eligible after-discount revenue sum meets an explicit threshold.
- Start checkpoint: `tools/checkpoints/2026-11-16T1708+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_START.md`.
- Next: implement fail-closed threshold parsing and daily aggregation; synthetic tests first, then a fresh freeze + train-only evaluation if focused tests pass. Preserve v16. No public/private labels.
- Revenue continues to exclude unsuccessful orders; cancellation/return/delivery-failed distinctions remain intact. No threshold answer or dataset-specific mapping will be hardcoded.
- Completed at 17:17 GMT+7: the new intent groups rulebook-supported line revenue by date and counts dates meeting an explicit positive inclusive threshold. Added strict threshold parsing, QueryPlan transport, execution, verifier support, and regressions. Also fixed the previously undefined payment status alias and excluded pending/nonsettled payment events from collected totals.
- Verification: focused understanding/pipeline tests 71 passed; complete suite 160 run, 157 passed, 3 Git-dependent skips, exit 0. Completion record: `tools/checkpoints/2026-11-16T1717+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_COMPLETE.md`.
- Next: create fresh v17 replay from the frozen metadata-complete train input; validate all hashes before train-only evaluation. Preserve v16 and do not open public/private labels.
- Latest targeted fix completed: documented unique-key line-to-invoice join, exact duplicate-line handling, workbook Excel date-epoch propagation, and decisive source-column decimal policy. Synthetic regressions cover fail-closed duplicate/unmatched keys, missing epoch, and ambiguous-only number columns. biz_124 inference smoke now answers 8 days from its actual line/invoice data. Full suite: 164 run, 161 passed, 3 Git-dependent skips. Evidence: `tools/checkpoints/2026-11-16T1752+07-00_P6_EXCEL_JOIN_AND_COLUMN_POLICY_COMPLETE.md`.
- Next: freeze v18 using a fresh replay folder and unchanged metadata-complete train inputs; validate all hashes before train-only evaluation. Then extract only public inputs (never labels) to a new workspace directory and create/validate `public_submission.jsonl`. Latest user direction: fix reproducible bugs only; avoid unrelated refactors.
- v18 generation start: `tools/checkpoints/2026-11-16T1755+07-00_P6_V18_TRAIN_REPLAY_START.md`; use only new output directory `work/evaluation/p6-train-replay-v18-revenue-join-dates-2026-11-16/`.
- v18 completed and passed freeze validation for 3,000 predictions/traces, IDs/order/schema, source/input/output checksums, and metadata inclusion; generator confirms labels untouched. Hashes/evidence: `tools/checkpoints/2026-11-16T2018+07-00_P6_V18_TRAIN_FREEZE_VALIDATED.md`. Train-only evaluator may run; it revalidates before opening labels. Public archive was separately checked by central directory: 113 members, 97 public files, no answer member; extracted 1,000-question/14-business public input to `work/evaluation/public-input-2026-11-16-v1/`, with no answer file.
- v18 train evaluation: 28 correct, 10 wrong, 2,962 abstain / 3,000; 1.2667% coverage, 73.68% answered accuracy, PA 0.600%, p95 14ms, no runtime errors. Worse PA than v17, so no improvement claim. False answers reveal a generic bug: purchases entered sales-ranking selection, and biz_126 chose raw quantity instead of README base-unit `SL lẻ`. Start fix checkpoint `tools/checkpoints/2026-11-16T2024+07-00_P6_SALES_SOURCE_AND_BASE_QUANTITY_FIX_START.md`. Fix before public inference.
- v17 generation start checkpoint: `tools/checkpoints/2026-11-16T1718+07-00_P6_V17_TRAIN_REPLAY_START.md`; output must be the new `work/evaluation/p6-train-replay-v17-daily-revenue-threshold-2026-11-16/` directory.
- v17 replay completed for 3,000 questions/30 businesses with `answer_labels_accessed=false`. Freeze validator passed code/input/prediction/trace checks, IDs/order/schema, and rulebook/calendar inclusion. Hashes and evidence: `tools/checkpoints/2026-11-16T1728+07-00_P6_V17_TRAIN_FREEZE_VALIDATED.md`. Train-only evaluator may now run; it revalidates before reading answers.
- v17 evaluator completed after revalidation: 26 correct, 3 wrong, 2,971 abstain / 3,000; coverage 0.9667%, answered accuracy 89.66%, penalized accuracy 0.7667%, p95 22 ms, runtime errors 0. Daily-threshold intent parsed the biz_124 question but correctly abstained `missing_column` because date/status are on the invoice table, separate from line amounts.
- Structural scan (README + workbook headers/keys, no answer use) found a safe join path: unique nonblank invoice IDs and 100% line-ID coverage for 97,033 line rows. Start checkpoint for the bounded fail-closed join: `tools/checkpoints/2026-11-16T1736+07-00_P6_DAILY_REVENUE_SAFE_JOIN_START.md`. Next: implement, test, and create a fresh replay only after the focused/full suite.
- Safe join is implemented and synthetic regressions pass, but the biz_124 real-data smoke still abstains. Root cause: executor dropped Excel `date_system`; scan found 31,997 invoice dates stored as numeric serials. `ingest._xlsx` and `parse_date` already expose the necessary epoch, but metrics did not propagate it. Start checkpoint: `tools/checkpoints/2026-11-16T1742+07-00_P6_EXCEL_DATE_SYSTEM_PROPAGATION_START.md`. Next: propagate workbook epoch through `_period` and joined table, add a fail-closed regression, test, then smoke again.
- After epoch propagation, the remaining abstention is numeric ambiguity in the line-amount column. Read-only scan of biz_124 `Thanh tien` found 97,033 populated strings, 89,638 per-cell ambiguous; full-column inference finds a consistent `.` decimal policy and makes all 97,033 parse. This is the current bounded bugfix; start record `tools/checkpoints/2026-11-16T1747+07-00_P6_REVENUE_COLUMN_SEPARATOR_FIX_START.md`. Keep scope to evidenced parse/execution defects; no broad refactor.

## P1 targeted rules review — 14:46 GMT+7

- Technical approach aligns in concept with DataMate: Vietnamese Q&A over structured data, deterministic calculations, typed answers, and abstention. No whole-entry compliance certification is possible yet; task-specific portal guidance still controls.
- Critical open items: outside scenario-set provenance/track permission; whether contest data may be included in a submitted image; valid model category for a deterministic no-model system; complete open-source/image license evidence; competition-time GitHub sharing under §8.2. The pasted §4.5 is stricter than the linked PDF, so retain the stricter interpretation pending organizer clarification.
- Current `training_code/` has no data archive, but README proposes adding `train.zip` and Dockerfile copies the whole directory. Do not add datasets to the image unless current official DataMate guidance explicitly requires and permits it.
- Full findings and source scope: `tools/checkpoints/2026-11-16T1446+07-00_P1_TARGETED_COMPETITION_RULE_REVIEW.md`.

## Active P6 — current rulebook/calendar replay, 14:15 GMT+7

- Start checkpoint: `tools/checkpoints/2026-11-16T1415+07-00_P6_CURRENT_RULEBOOK_CALENDAR_REPLAY_START.md`.
- Input preflight: training replay root has only `questions.jsonl` and `data/`; no answer file. Output directory is new; isolated source has no `.git`.
- v13 generated 3,000 predictions/traces with `answer_labels_accessed=false`, but pre-score validation failed because `src/datamate/understanding.py` changed after freeze. It remains unevaluated; no labels were opened. Failure evidence: `tools/checkpoints/2026-11-16T1433+07-00_P6_REPLAY_FREEZE_MISMATCH.md`.
- Focused verification found the concrete regression: current `RulePlanner` lacks `split_rules` argument and the Tết API runner raises `TypeError`. Pre-fix results: 39 passed, 1 failed. Fix start: `tools/checkpoints/2026-11-16T1434+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_START.md`.
- Restored the known rulebook/calendar forwarding; focused timeparse/understanding/Tết-runner tests now pass 40/40. Completion: `tools/checkpoints/2026-11-16T1435+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_COMPLETE.md`.
- v13 remains preserved and unevaluated. v14 was generated in a separate output directory for 3,000 train questions and passed `validate_frozen_replay` for source, input, prediction, trace, order/count, and schema. `answer_labels_accessed=false`; no labels have been opened. Evidence: `tools/checkpoints/2026-11-16T1448+07-00_P6_V14_FREEZE_VALIDATED.md`.
- v14's evaluator result is preserved, but is not a quality metric: all 3,000 records abstained because the frozen input omitted `rulebook.md`. Trace evidence: 3,000 `RulebookError` events with reason `rulebook_unavailable`. The archive contains `train/rulebook.md` and `train/calendar.csv`; v14 output remains unchanged. See `tools/checkpoints/2026-11-16T1450+07-00_P6_V14_INCOMPLETE_INPUT_FINDING.md`.
- v15 remains preserved and unscored: its input manifest omitted `rulebook.md` and `calendar.csv`. Fixed `build_input_manifest` to require/hash both split metadata files and added regressions that changes to either fail frozen-input validation. Focused replay tests: 3/3 passed. Evidence: `tools/checkpoints/2026-11-16T1633+07-00_P6_REPLAY_METADATA_HASH_FIX_COMPLETE.md`.
- Next: generate v16 at a fresh output path; verify the manifest lists both metadata files and all source/input/prediction/trace checksums before any label evaluation. Do not score v13–v15 or access public/private labels.
- v16 metadata-hashed replay is now running in session `50250` to `work/evaluation/p6-train-replay-v16-metadata-hashed-2026-11-16/`. Start record: `tools/checkpoints/2026-11-16T1635+07-00_P6_V16_METADATA_HASHED_REPLAY_START.md`. Wait for this process; do not duplicate it.
- v16 completed and passed freeze validation: manifest explicitly contains `rulebook.md` and `calendar.csv`; 3,000 prediction/trace IDs, order, schema, code/input/output checksums all match; `answer_labels_accessed=false`. Details/hashes: `tools/checkpoints/2026-11-16T1642+07-00_P6_V16_METADATA_HASHED_FREEZE_VALIDATED.md`. Next, train-only evaluator may run; it repeats validation before reading train answers.
- v16 train-only evaluator completed after revalidating the freeze. Results: 26 correct, 4 wrong, 2,970 abstain/3,000; 1.00% coverage, 86.67% answered accuracy, 13.33% false-answer rate, 0.733% penalized accuracy, p95 18 ms, 0 runtime errors. Train-only and in-sample; not acceptance or generalization. Wrong intents: cancellation_rate 2, quantity 1, sales_ranking 1. Abstention reasons led by unsupported_intent 1,169, ambiguous_entity 783, missing_column 658. Evidence: `tools/checkpoints/2026-11-16T1645+07-00_P6_V16_TRAIN_DIAGNOSTIC_EVALUATED.md`.
- Next: inspect the four errors and largest abstention buckets using train labels only after freeze, then make generic fixes with synthetic regression and run a new frozen train diagnostic. P3 reviewer remains NOT VERIFIED / NOT PASSED.

## Latest P4 checkpoint — split calendar and Tết support, 14:08 GMT+7

- Completion evidence: `tools/checkpoints/2026-11-16T1408+07-00_P4_SPLIT_CALENDAR_TET_SUPPORT_COMPLETE.md`.
- Runtime uses the active split's calendar and rulebook to map its configured lunar Tết interval to solar dates. Preserves explicit Gregorian periods; preceding-Tết comparison requires the documented rule.
- Focused tests: 19 time parser tests + 1 runner test passed. Read-only metadata smoke on train and public archives passed; no questions/answers/labels or business rows were read.
- General-rule review: the supplied regulation does not establish permission for the external scenario file or certify full solution compliance. Keep its provenance/license and track permission unresolved; do not include it in training/package until documented.
- Compliance blockers from targeted manifest review: no model is declared, while the portal screenshot lists only API/LLM/SLM categories; confirm the valid category instead of mislabeling. `openpyxl==3.1.5` and a vLLM base image are present, but no full third-party license/provenance inventory exists; section 4.5 remains unverified.

## Latest P5 checkpoint — typed verifier gate, 14:12 GMT+7

- Completion evidence: `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`.
- Verified the existing type/evidence/confidence/ranking-cardinality gate; added tests rejecting empty/overlong ranking lists while retaining shorter nonempty lists when fewer candidates exist.
- Focused verifier tests: 5 passed. This bounded P5 slice is complete; P5 overall remains partial/not accepted.

## P4 Tết support start checkpoint — completed at 14:08 GMT+7

- Start record: `tools/checkpoints/2026-11-16T1354+07-00_P4_SOLAR_LUNAR_TIME_SUPPORT_START.md`.
- It limited source inspection to split rulebook and calendar metadata. Implementation and verification are in the 14:08 completion record above.

## Latest checkpoint — competition-rule conformance correction, 13:44 GMT+7

- Completion record: `tools/checkpoints/2026-11-16T1344+07-00_P4_COMPETITION_RULEBOOK_CONFORMANCE_COMPLETE.md`.
- Runtime reads the split's `rulebook.md`. Revenue now uses line-level after-discount amounts and the rulebook's date/status clauses; cancellation rate uses that split's numerator; rankings use explicit/default metric, code tie-break and valid short top-k outputs. Earlier D10 convention is superseded for contest inference.
- Focused changed-code tests passed 16/16 across two targeted commands; actual train rulebook parser smoke passed. Full test suite was not run due to the user's time constraint.

## P5 typed verifier gate start checkpoint — completed at 14:12 GMT+7

- Start record: `tools/checkpoints/2026-11-16T1330+07-00_P5_TYPED_ANSWER_VERIFICATION_START.md`.
- Completion evidence: `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`.

## Latest checkpoint — VND and million-suffix normalization, 2026-11-16 13:25 GMT+7

- Evidence: `tools/checkpoints/2026-11-16T1325+07-00_P4_VND_MILLION_NORMALIZATION_COMPLETE.md`.
- Parser handles explicit VND grouping plus Vietnamese `tr`/`triệu` suffixes; ambiguous bare `10.000` and `1,156tr` stay ambiguous absent explicit policy/column evidence. Source audit parsed all 131,192 biz_127 `Amount` values and 145,479 biz_129 `Tiền bán` values; no cell coercion of remaining placeholders.
- Focused normalization+ingestion: 25 passed. Full suite: 142 run, 139 passed, 3 Git-dependent skips, exit 0.
- v12 freeze validated 3,000 predictions/traces before evaluator label access. Predictions identical to v11; metrics unchanged (40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 38 ms, no runtime errors). No improvement claim.
- Detail/order reconciliation is weak (biz_127 exact 9,605/33,874; biz_129 exact 11,587/38,499); no unsafe join was introduced. P3 remains NOT VERIFIED / NOT PASSED; P4/P5 remain partial. No Public Test, Git/official checkout, `sources/`, Docker, commit, or push action.

## Latest checkpoint — no-data reason coverage across intents, 2026-11-16 13:00 GMT+7

- Completion evidence: `tools/checkpoints/2026-11-16T1300+07-00_P4_NO_DATA_REASON_INTENT_COVERAGE_COMPLETE.md`.
- Synthetic tests cover empty periods for collected amount, order count, unsuccessful-order rate, and ranking; malformed dates stay `insufficient_evidence`; a zero collection answers 0. Added explicit revenue regression for canceled, returned, and failed-delivery exclusions, confirmed by the user.
- Focused pipeline suite: 40 passed. Full suite: 140 run, 137 passed, 3 Git-dependent skips, exit 0. This unit changed tests/docs only; source code and frozen replay inputs are unchanged.
- P3 remains NOT VERIFIED / NOT PASSED; P4/P5 remain partial/not accepted. No Public Test, Git/official checkout, `sources/`, Docker, commit, or push action.

## Latest checkpoint — no-data versus zero, 2026-11-16 12:48 GMT+7

- `tools/checkpoints/2026-11-16T1248+07-00_P4_NO_DATA_ZERO_SEMANTICS_COMPLETE.md` records implementation, tests, replay hashes, limits, and next action.
- `no_data` is emitted only when a unique supported source has no raw rows in the requested period; matching rows whose valid aggregate is zero still answer `0`. Internal trace reason is separate from unchanged submission abstain JSONL. Reason contract: `docs/VERIFIER_REASON_CODES.md`.
- Focused tests: 48/48. Full suite: 136 run, 133 passed, 3 Git-dependent skips, exit 0.
- v11 was frozen and validated for 3,000 predictions/traces before evaluator label access. Predictions match v10 byte-for-byte; score unchanged: 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 37 ms, no runtime errors. Revenue still accounts for 30/44 wrong answers. `no_data` appeared in 0/3,000 traces, so evidence is synthetic for its occurrence path.
- P3 reviewer skipped; P3 remains NOT VERIFIED / NOT PASSED. P4/P5 remain in progress/not accepted; no 81% claim. No Public Test tuning, Git/official checkout, `sources/`, Docker, or commit/push action.

## Latest checkpoint — P5 order-status trace reasons, 2026-11-16 12:32 GMT+7

- Status-rate abstentions now distinguish `missing_order_status`, `unknown_order_status`, and `conflicting_order_status` in internal traces. Submission JSONL continues to emit the existing abstain record.
- Focused pipeline/API suite: 47 passed. Full suite: 135 run, 132 passed, 3 Git-dependent skips, exit 0.
- Frozen v10 train replay validated 3,000 predictions/traces before evaluator label access. Prediction file is byte-identical to v9 (SHA-256 `76fc89bc51e96f96f67b434c79ebcbf1b56777b50d867493cadc7e19b2950fa8`). Metrics unchanged: 40 correct, 44 wrong, 2,916 abstain, PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 18 ms, runtime errors 0. New codes do not occur in these train traces; they are covered by synthetic tests.
- Report: `work/evaluation/p6-train-replay-v10-status-trace-2026-11-16/evaluation_report.json`; completion evidence: `tools/checkpoints/2026-11-16T1232+07-00_P5_ORDER_STATUS_TRACE_REASON_COMPLETE.md`.
- P3 reviewer skipped; P3 remains NOT VERIFIED / NOT PASSED. No Public Test tuning, Git/official checkout, `sources/`, or Docker action.

## Latest checkpoint — shared unsuccessful-order status convention, 2026-11-16 11:54 GMT+7

- Applied the user's global convention: canceled, returned, and failed-delivery remain distinct raw-outcome classes and all count in the unsuccessful-order-rate numerator. In-transit/pending remain separate. Rate uses unique order IDs and abstains on missing/unknown status, conflicting statuses, or ambiguous/missing exact order-status headers.
- Added non-mutating status classification and exact documented aliases for order status, including `Kết quả` and `Ghi chú TT`; this avoids substring false matches such as `Trạng thái HĐĐT` and `trang_thai_kh`. `Đổi trả` maps to returned; `Không giao được` maps to delivery failed.
- Added five pipeline regressions for distinct statuses/shared rate numerator/raw-value preservation, documented aliases, unknown/missing values, unrelated status headers, and duplicate order lines. Focused suite: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 35 passed.
- Read-only train-source smoke (no answer labels): biz_101 `Kết quả` classified all 4 observed values; biz_116 `Trạng thái` classified all 7 observed values. Full-period executor smoke returned 4.60% and 2.47% respectively with zero unknown status classes in these two datasets.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 132 run, 129 passed, 3 Git-dependent skips; exit 0. Initial focused invocation without `PYTHONPATH=src` failed to import `datamate`; corrected invocation passed. Initial focused tests also caught missing English `cancelled` recognition and stale expectations for `Đang giao`; both were corrected, with in-transit remaining distinct and excluded under the existing nonfinal-status firewall.
- Frozen v9 train replay validated 3,000 predictions and 3,000 traces before evaluator-only label access. Metrics: 40 correct, 44 wrong, 2,916 abstain; PA -0.13%; coverage 2.80%; answered accuracy 47.62%; p95 42 ms; runtime errors 0. Cancellation-rate: 2/14 answered correct, 12 wrong versus v8's 12 correct/2 wrong. This shows mismatch with train references; retain the user-approved convention and do not tune it to labels. In-sample diagnostic only.
- P3 reviewer remains skipped; P3 is NOT VERIFIED / NOT PASSED. No labels were used in implementation or source-data smoke; train labels were opened only by the evaluator after freeze validation. Details/hashes: `tools/checkpoints/2026-11-16T1154+07-00_UNSUCCESSFUL_ORDER_STATUS_RULE_COMPLETE.md`.
- P7 latest matrix is now derived from v9: `docs/BUSINESS_COVERAGE_V9.md` and `work/evaluation/business-coverage-matrix-train-v2-2026-11-16.json`. L1/L2/L4 30/30, L3/L5 0/30. The generator's stale hardcoded v7 and 0/30 text was corrected; focused tests 4/4, full suite 133 run/130 passed/3 Git-dependent skips, exit 0. Evidence: `tools/checkpoints/2026-11-16T1156+07-00_P7_MATRIX_REFRESH_COMPLETE.md`.

## Latest checkpoint — revenue/collected-money contract, 2026-11-16 11:03 GMT+7

- Implemented the user's rule: default revenue chooses after-discount order total; explicit received/paid questions use a distinct `collected_amount` intent and payment-event date/amount; absent or ambiguous source data abstains. The executor does not substitute order total, debt, or paid-balance snapshots for receipts.
- Added regressions for intent/schema separation, split receipts by event date, pending/missing/ambiguous payment evidence, order-total priority, and two-metric requests. Real-data smoke for biz_127/biz_129 selected `don_hang` for revenue and `thanh_toan` for collection; no answer values were printed.
- Full suite: 127 run, 124 passed, 3 Git-dependent hygiene skips, exit 0.
- Frozen v8 train evaluation: same predictions as v7; 47 correct, 37 wrong, 2,916 abstain; PA 0.33%, coverage 2.80%, answered accuracy 55.95%; runtime errors 0; p95 35 ms. This semantic fix did not improve train score; v8 is in-sample and below acceptance.
- P3 reviewer remains skipped; P3 is NOT VERIFIED / NOT PASSED. P4/P5/P6 remain in progress. Details/hashes: `tools/checkpoints/2026-11-16T1103+07-00_REVENUE_COLLECTION_CONTRACT_COMPLETE.md`.
- Next: use frozen train evaluation for error-category analysis, then fix the highest-impact generic cause. No Public Test tuning.

## Latest checkpoint — P7 structural business coverage, 2026-11-16 10:37 GMT+7

- Generated a structural profile for all 30 train businesses: 30 READMEs, 128 files, 339 tables/sheets, zero profile errors, and no questions passed to the profiler. The profile contains schema/README metadata, no cell values.
- Added a reproducible business coverage matrix tool and 3 tests. Matrix JSON and `docs/BUSINESS_COVERAGE.md` include levels, source structure hints, and frozen v7 per-business metrics.
- Level evidence: L1 30/30; L2 appeared in replay with no runtime errors 30/30 (not row reconciled); L3 mapped business-intent tests 0/30; L4 train replay 30/30; L5 release-supported 0/30. P7 remains NOT ACCEPTED; 0% L5 is below 81%.
- v7 train-only: PA 0.33%, coverage 2.80%, answered accuracy 55.95%; 47 correct, 37 wrong, 2,916 abstain; p95 18 ms; no runtime errors. Macro PA 1.05%; macro coverage 3.58%; macro answered accuracy 55.30% among 8 businesses with answers. Diagnostic only, not independent acceptance.
- User-defined revenue contract: default is order value after discounts; collected/paid amounts are separate and only answerable when explicitly requested; abstain when evidence is insufficient.
- Full suite after the new tool: 119 run, 116 passed, 3 repository-hygiene skips because this isolated copy has no `.git`; exit 0.
- P3 reviewer was skipped per user; P3 remains NOT VERIFIED / NOT PASSED. Exact evidence and commands: `tools/checkpoints/2026-11-16T1037+07-00_P7_BUSINESS_COVERAGE_MATRIX_COMPLETE.md`.
- Next: continue remaining Playbook workstreams; use the clarified revenue semantics in the next safe implementation slice.

## Current work item — P3/P4/P5/P6 safety and evaluation — 2026-11-16 10:18 GMT+7

- User explicitly said to skip the P3 reviewer. Reviewer status is skipped; P3 remains **NOT VERIFIED / NOT PASSED** and no ≥81% acceptance metric is claimed.
- Added generic recognition/fail-closed handling for named-product filters, product/channel/payment breakdowns, natural-language revenue shares, best-sales-day typos/English `revenue`, and average revenue. Scalar revenue requests with a percent unit now produce internal `invalid_unit` abstention rather than a currency sum. Follow-up covers product mentions via `món`/`tiền bán`/`bán <name>` and point-of-sale channel.
- P4 now excludes failed-delivery/nonfinal statuses (`không giao được`, `đang vận chuyển`, `failed`, `shipping`, `pending`, etc.) from revenue/quantity/ranking totals. Focused pipeline tests: 26 passed. Latest full suite: 116 run, 113 passed, 3 Git-dependent hygiene skips, exit 0.
- P3-focused suite before the latest P4-only status change: 48/48 passed. The subsequent full suite includes all those cases.
- Latest P6 current-code v7 train replay (3,000 questions/30 businesses) scored PA `0.00333`: 47 correct, 37 wrong, 2,916 abstain; 2.80% coverage; 55.95% answered accuracy; 44.05% false-answer rate; 70/70 unanswerable cases correctly abstained; no runtime errors; p95 18 ms. In-sample only, not acceptance. Versus v6b: 4 more correct, 9 fewer wrong; versus v5: 23 fewer wrong. Report: `work/evaluation/p6-train-replay-v7-current-code-2026-11-16/evaluation_report.json`.
- v7 wrong answers: revenue 30 (all number-vs-number; 21 biz_127, 9 biz_129; QuerySpec has no filters/dimensions), cancellation_rate 2, order_count 2, quantity 2, sales_ranking 1. P4/P3 follow-up is included in this replay.
- At 10:18, source schemas showed distinct gross/receivable and paid/balance fields and revenue semantics were unresolved. The user later defined the metric; see the 11:03 revenue/collected-money checkpoint for the implemented contract and limitations.
- User-directed P3 reviewer skip remains in effect. P3 is **NOT VERIFIED / NOT PASSED**; no ≥81% metric is claimed. P4/P5/P6 remain partial. No Public Test tuning, official checkout write, Git operation, Docker work, or source archive mutation occurred.
- Evidence: `tools/checkpoints/2026-11-16T1004+07-00_P3_P6_REVENUE_ANALYSIS_COMPLETE.md`, `tools/checkpoints/2026-11-16T1010+07-00_P4_NONFINAL_STATUS_FIREWALL_COMPLETE.md`, and `tools/checkpoints/2026-11-16T1018+07-00_P6_CURRENT_CODE_REPLAY_COMPLETE.md`. The incomplete earlier attempt `work/evaluation/p6-train-replay-v6-revenue-firewall-2026-11-16` is preserved and not evaluable.

## Current continuation — 2026-11-16

- User directed us to skip the independent-review wait for P3 and proceed. P3 remains **NOT VERIFIED / NOT PASSED**; no reviewer result or ≥81% metric is claimed.
- P1 and P2 remain complete based on their prior verified evidence; those checks were not repeated.
- P4 is **IN PROGRESS**. Hardened the deterministic executor to abstain on multiple matching source tables, nonblank rows with unparseable dates, invalid numeric values in the selected period, no matching rows, missing order IDs, and conflicting statuses for one order. Synthetic regressions added.
- Verification: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 11 passed; complete suite — 85 run, 82 passed, 3 Git-dependent hygiene checks skipped, exit 0.
- Changed source/test SHA-256: `metrics.py` `FB2E763E029FBC20517862B7317DF9EA7890A4EF47E186B897E268B685097FBA`; `test_pipeline.py` `FA801A24C8DAD557EF14622655D662EF188B8B1A0136D4F2B14E7EEB7B501E53`.
- This is a narrow safety improvement, not P4 acceptance: broader operator contracts, declared joins, business-specific rules, and supported-scope replay remain open. P5–P8 are not accepted. Docker work is out of scope per the user.
- Working copy remains an isolated no-Git snapshot. No GitHub sync, commit, push, branch operation, source archive/data/label access, or official checkout change occurred in this work item.
- Detailed evidence: `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_COMPLETE.md`.
- P5 trace decision metadata now uses stable reason codes for unsupported intent, missing time range, ambiguous entity, insufficient evidence, source unavailable, parse failure, and verification failure. Submission JSONL remains unchanged; richer decision data and validated QuerySpec are written only to trace logs.
- Focused API/verifier tests: 20/20. Full suite after P4 and P5 changes: 90 run, 87 passed, 3 Git-dependent hygiene checks skipped, exit 0. Full P5 evidence: `tools/checkpoints/2026-11-16T0817+07-00_P5_TRACE_REASON_CODES_COMPLETE.md`.
- P5 remains partial: `missing_column`, `invalid_unit`, and `join_unsafe` are reserved reason codes but are not yet produced from structured executor failures; source/denominator/reconciliation gates and false-answer evaluation remain open.
- P3 reviewer gate is skipped at the user's direction, but P3 is still **NOT VERIFIED / NOT PASSED** because the required ≥81% acceptance evidence is not available. Synthetic filter-firewall behavior and schema tests pass; do not claim the phase met its threshold.
- P4 has additional schema-grounded executor tests: distinguish order totals from payment events; avoid inventory/delivery evidence for sales/order metrics; use high-confidence product/order headers; recognize English cancellation status. Current full suite: 102 run, 99 passed, 3 Git-only skips. P4 remains **IN PROGRESS / NOT ACCEPTED**.
- P5 now emits `missing_column`, `invalid_unit`, and `join_unsafe` from structured executor diagnostics; output JSONL remains unchanged. Full suite after this slice: 108 run, 105 passed, 3 Git-only skips. P5 is **IN PROGRESS / NOT ACCEPTED**: false-answer rate remains high and broader verification gates remain open.
- P6's latest full train diagnostic (v5, 3,000/30, frozen before label access) is PA `-0.005`: 45 correct, 60 wrong, 2,895 abstain, 3.5% coverage, 42.86% answered accuracy, 57.14% false-answer rate, p95 97 ms. It is in-sample and not independent acceptance. Wrong answers are concentrated in revenue (53), including biz_127 (31) and biz_129 (15). Full hashes/report: `tools/checkpoints/2026-11-16T0933+07-00_P5_EXECUTOR_REASON_CODES_COMPLETE.md` and `work/evaluation/p6-train-replay-v5-full-2026-11-16/evaluation_report.json`.
- Known risk: revenue answers from order-total schemas remain inaccurate in biz_127/biz_129; do not hardcode business-specific answers. Validate filter/date/aggregation semantics and fail closed where unsupported.
- Current hashes: `metrics.py` `8BBD1F0922F693E9E7EA8CEAAA7417D3EF4676B85F39CA534CEFBA6CC1F37E4A`; `rules.py` `90220AE6885BC14AA4B0193F1F11B98C3E488B0C837CC8ADD54B323DDBCCDB29`; `test_pipeline.py` `6ABA07B6C5894CF4B0E2DFA904D2A384084DE203018F1B1DEB761BC86E302A0F`.
- Working copy is isolated and has no `.git`, based on `24cfa0908bd20f6e5b210366e956cae0d665b56e`. No GitHub/official checkout writes, commit/push, source-archive mutation, or Docker work occurred.
- Latest checkpoints: `tools/checkpoints/2026-11-16T0848+07-00_P3_FILTER_FIREWALL_START.md`, `tools/checkpoints/2026-11-16T0920+07-00_P3_FILTER_FIREWALL_COMPLETE.md`, `tools/checkpoints/2026-11-16T0920+07-00_P4_ORDER_PAYMENT_PRODUCT_SAFETY_COMPLETE.md`, and `tools/checkpoints/2026-11-16T0933+07-00_P5_EXECUTOR_REASON_CODES_COMPLETE.md`.

## GitHub synchronization checkpoint — 2026-11-15

- Synced 38 reviewed files from the verified Source Release to the real repository's `feature/offline-core` branch. Commit: `3b0bf3b66e9a78fa68fa29e8b97a23787bac2f0a`, parent `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Complete suite in the target checkout: 80 tests passed. `git diff --check` passed. Post-push fetch confirmed local HEAD and `origin/feature/offline-core` match and worktree is clean.
- No Public/Private JSONL, archive, labels, logs, secrets, Docker image, internal checkpoints, or local report was pushed. `main` was untouched.
- Current worktree for further playbook work remains this isolated no-Git snapshot; its local checkpoint docs are not part of the release commit.
- P3 remains **NOT PASSED**; P4–P8 incomplete; Docker image remains unbuilt. Current user-facing progress report: `work/checkpoints/DATAMATE_CURRENT_PROGRESS_2026-11-15.md`.

## Emergency Docker investigation checkpoint — 2026-11-15

- Read the latest Docker mission, inspected the frozen Source Release/build context, inference entry point, dependencies/manifests, and all 10 pages of the official Docker guide.
- Build context remains verified as a build input only. The actual image is **BLOCKED**: local Docker was previously unavailable, Codespaces status cannot be checked through the connected GitHub tools, the local browser surface is disabled, and no accessible remote runner/workflow was found. Do not claim image/runtime/offline/GPU/export success.
- GitHub connector confirms repository access and public visibility, but does not expose Codespaces or workflow provisioning. Do not upload to the public repo: private/protected destination and branch protection are not established. No repo, source release, Public JSONL, or portal change was made.
- At the Docker investigation checkpoint, the repository was still at `24cfa0908bd20f6e5b210366e956cae0d665b56e`. A later GitHub sync advanced only `feature/offline-core` to `3b0bf3b66e9a78fa68fa29e8b97a23787bac2f0a`; see the synchronization checkpoint above.
- Full evidence and exact next action: `work/docker-build-investigation-2026-11-15/DOCKER_BUILD_INVESTIGATION.md`.
- Playbook status is unchanged: P3 **NOT PASSED**, P4–P8 incomplete. Continue from the latest P3 checkpoint only after preserving this Docker blocker.

Current isolated source: work/rehydrated-2026-11-15-P3/source, no .git, based on feature/offline-core commit 24cfa0908bd20f6e5b210366e956cae0d665b56e. The official checkout now contains the reviewed source-release sync commit above; main and sources remain untouched.

P1 and P2 are user-confirmed complete with existing structural profile/reconciliation evidence. P3 is NOT PASSED because reviewed full-slot QuerySpec metrics, including enough ambiguity-positive cases, are missing. P4–P8 remain incomplete. Do not infer phase completion from old historical sections below.

A Public Submissions candidate was generated once: work/submission-build/public-test-submission-2026-11-15/submission.jsonl. It has 1,000 valid ordered records/traces, no runtime errors, 718 abstentions, and no accuracy/PA measurement. It is not uploaded. Docker/Test Solution is still blocked because Docker/Podman/Buildah/Nerdctl and local CI are unavailable. Latest checkpoint: tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_COMPLETE.md.

# STATE.md — DataMate (Zalo AI Challenge 2026) · cập nhật 12/11/2026

## Checkpoint DF-1 — 14/11/2026
- Đã thêm parser số/ngày strict có trạng thái `ok`/`empty`/`invalid`/`ambiguous`, giữ raw value và `SourceLocation`.
- Đã thêm provenance theo dòng cho CSV/XLSX/SQLite; CSV không còn tạo thêm bản sao `list(csv.reader(...))`; SQLite vẫn mở `mode=ro`.
- XLSX phát hiện header không đủ hoặc có cấu trúc nhiều hàng/gộp ô và trả lỗi rõ ràng thay vì tự gộp cột. Chưa có chính sách header theo từng nguồn.
- Đã chạy 17 test cũ với `PYTHONPATH=src` và smoke test parser; chưa kịp thêm test parser/ingest bền vững vì người dùng yêu cầu dừng và push ngay.
- Việc tiếp theo: thêm test synthetic cho parser và ingestion trước khi chuyển sang iterator/streaming descriptor hoặc Data Discovery.

## Đã xong
- Phiên A (M0–M1): đọc luật và đề, kiểm kê train + public, phân tích rulebook và câu hỏi.
- Báo cáo đầy đủ: Claude Doc “DataMate – Báo cáo Giai đoạn 1 (M0–M1)”.
- Công cụ: `inventory.py` (kiểm kê dữ liệu), `qstats.py` (thống kê câu hỏi và đáp án).
- Phiên B1 (feature/offline-core): ingest CSV/XLSX streaming/SQLite, time parser Gregorian, rule planner, allowlist executor subset (doanh thu/số lượng/số đơn/tỉ lệ huỷ/top bán chạy), verifier, output validator, test synthetic, predict.sh/Dockerfile baseline.
- Phiên B2: API nội bộ không mạng, scorer local kiểu output, trace log từng câu ở /result/logs/trace.jsonl theo Docker Guide.

## Trạng thái hiện tại 13/11/2026
- VERIFIED: unit tests synthetic cho rule subset; output JSONL deterministic; reader XLSX streaming không cần nạp nguyên sheet.
- UNVERIFIED: chạy full train/public, Docker build/run, score, SLM/LLM model/weights, tất cả rules phức tạp.
- Không dùng public/private test để tuning. Không commit dataset/output/weights.

## Chạy lại (cần train.zip, public_test.zip đã giải nén)
```
python inventory.py train/ inv_train.json --titles
python inventory.py public_test/ inv_public.json --titles
python qstats.py train/ 40
python qstats.py public_test/ 15
```

## Phạm vi đã đọc (để phiên sau không nhầm)
- Đọc đầy đủ: rulebook train; chữ trong 4 file Project (file “tổng quan” chỉ có một URL); 3 ảnh.
- calendar.csv: chỉ xem header và 2 dòng đầu; hai bản (train, public) giống hệt nhau.
- Rulebook public: chỉ đọc phần khác biệt so với train (48 dòng). Dòng “Trả góp” của cửa hàng điện thoại bị cắt ở 400 ký tự, cần đọc lại nguyên văn.
- README: chỉ đọc dòng mô tả đầu của 44 file (30 train + 14 public). Cần đọc đầy đủ khi viết loader.
- File dữ liệu: chỉ header, 1–2 dòng mẫu và số dòng; chưa đọc nội dung ô.
- Câu hỏi: thống kê toàn bộ 4.000 câu, chỉ xem tay khoảng 52 câu mẫu.
- Đính chính (13/11): Docker guideline CÓ trong tài liệu Project và đã được đối chiếu (xem `docs/decisions.md`); lịch nộp lấy từ `Submission_Guidance`. Vẫn chưa có: `build-your-own-skill-library.pdf`, nội dung trang challenge.zalo.ai, thông tin GPU của đội.

## Việc kế tiếp — Phiên B (loader + bộ chấm điểm)
1. Đọc đầy đủ README của một business cho mỗi kiểu file (10 kiểu) và ghi chú cấu trúc.
2. Viết loader cho header 2 tầng, sheet theo tháng, ngày và số dạng chữ; đối soát tổng đơn và thanh toán.
3. Viết `scorer.py` đúng luật khớp (chuỗi NFC/lowercase/giữ dấu, số, % hai chữ số, list, table) kèm test từ các ví dụ trong luật.
4. Thước đo xong: tỉ lệ business train đọc đúng theo đối soát.

## Lưu ý môi trường sandbox (tránh lặp lỗi cũ)
- Không GPU, 1 CPU, khoảng 3 GB RAM; có pandas 3.0.6, openpyxl 3.1.5, scikit-learn; không có duckdb.
- Lệnh chạy quá 300 giây bị dừng: chia nhỏ hoặc ghi kết quả trung gian ra file.
- Shell là dash: không dùng `<(...)` hay `time (...)`; in tiếng Việt bằng Python, không dùng `cut -c` hoặc `head -c` vì cắt hỏng UTF-8.
- XLSX thường thiếu thẻ dimension: đếm dòng bằng cách quét thẻ `<row` trong file zip (vài giây).
- web_fetch chỉ mở URL đã xuất hiện trong kết quả tìm kiếm trước đó.

## Checkpoint hoạt động — P0, 15/11/2026

- Working copy riêng: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`; snapshot từ `feature/offline-core` tại `24cfa0908bd20f6e5b210366e956cae0d665b56e`, không có `.git`, không khởi tạo lịch sử giả.
- Audit trước đó xác nhận remote `https://github.com/DangDuuTapCode/DataMate.git`; working tree sạch; main `6be6997015a1d394ab8ed0eadd0141407ea1a1da`; feature đi trước main 3 commit, không tụt sau. Refs cache khớp; chưa xác nhận fetch mới.
- Snapshot khớp 39/39 path và SHA-256; test snapshot 17 chạy, 14 pass, 3 hygiene test cần Git bị skip; checkout chính lúc P0 đạt 17/17.
- Process chạy dưới `ADMIN-PC\CodexSandboxOffline`, repo chính thuộc `ADMIN-PC\Admin`; Git báo `dubious ownership`. Không đổi safe.directory/ACL, không nâng quyền. Repo chính, main, working copy cũ và `sources/` không bị sửa.
- Chỉ kiểm kê archive: train 3.000 câu/30 business (chưa đọc đáp án); public 1.000 câu/14 business (không có answers); không dùng public để tuning. Archive vẫn chưa giải nén.
- P1–P9: **NOT MEASURED**, chưa tuyên bố đạt 81%. Chưa sửa source. Tiếp theo thêm synthetic tests normalization/ingestion, sửa lỗi có bằng chứng, chạy lại full suite, cập nhật đủ ba tài liệu và checkpoint append-only.

## Checkpoint P1 — 15/11/2026

- P1 structural ingestion metric achieved: 30/30 train businesses (100%) read fully; 128 structured files, 339 tables/sheets, 3,997,042 rows. No answer labels loaded. Four businesses with unflagged UTF-8 archive filenames were separately re-extracted with correct UTF-8 names and revalidated 4/4. See ignored reports under `logs/`.
- Added safe XLSX report-preamble detection (complete header among first 32 rows), absolute/relative worksheet target resolution and XML row cleanup; CSV/XLSX blank/duplicate header checks; conservative numeric separator inference; Excel date overflow returns invalid status.
- Synthetic parser/ingestion tests: 20/20. Full suite: 37 run, 34 pass, 3 repo-hygiene checks skipped without `.git`.
- P1 structural ≥81% gate: **100% PASS**. Semantic normalizer accuracy and question-answer performance remain unmeasured. P2–P9: **NOT MEASURED**.
- No source archive, public data, QA labels, official checkout or `main` changed. P1 detailed checkpoint: `tools/checkpoints/2026-11-15_P1_NORMALIZATION_INGESTION.md`.

## Playbook-aligned current phase status — 2026-11-15

- Use Master Implementation Playbook numbering: P1 profile audit; P2 ingestion hardening; P3 QuerySpec/understanding. Earlier numbering is historical.
- P1: COMPLETE at L1 structural scope, consistent with user confirmation. 30/30 READMEs; 128 structured files; 339 tables/sheets with headers. Matrix: `docs/BUSINESS_COVERAGE_MATRIX.md`; machine profile: ignored `logs/train_business_profiles.json`. P7 supported-business coverage remains a separate metric.
- P2: COMPLETE at 100% structural reconciliation, consistent with user confirmation and current re-audit: 30/30 businesses; 128 files; 339/339 tables/sheets; 3,997,277 source = 3,997,042 accepted + 0 rejected + 235 skipped; all scans reconciled, zero failures. Report: ignored `logs/p2_reaudit_2026-11-15.json`; checkpoint: `tools/checkpoints/2026-11-15_P2_INGESTION_REAUDIT.md`.
- P3: IN_PROGRESS. Versioned QuerySpec schema and regression suite exist, but current full-slot accuracy on an independently reviewed business holdout and ambiguity-positive metrics are missing. Historic 2,843/3,000 interpreted (94.77%) and 1,620/3,000 executable (54.0%) are coverage only.
- Latest full suite: 78 run, 75 passed, 3 Git-dependent hygiene checks skipped in the no-`.git` snapshot; exit 0.
- Latest source checkpoint: `tools/checkpoints/2026-11-15_P3_SUPPLIER_RANKING_SPEC.md`. P3 remains NOT PASSED; no 81% claim.
- Next exact action: prepare a blind, business-held-out QuerySpec review packet with all nine slots; freeze code/evaluator hashes before evaluation; evaluate once after independent review. Keep inspected prior holdouts frozen.
- Safety: no labels read, no public data used, no Git history initialized, no official checkout or `main` edits, no commit/push/merge.

## Playbook checkpoint P2 — 2026-11-15

- P2 ingestion hardening is **VERIFIED at structural reconciliation scope (100%)**: 30/30 train businesses, 128 structured files, 339 tables/sheets; 3,997,277 source records = 3,997,042 accepted + 0 rejected + 235 intentionally skipped; every scan completed and every table reconciled.
- `IngestionStats` exposes reconciliation counters and scan completeness; typed `IngestionError` marks partial scans incomplete. `read_business(errors=...)` continues other files while the default remains fail-fast. Row provenance is retained.
- Focused ingestion suite 13/13; final complete suite 52 run, 49 pass, 3 Git-dependent skips in this no-`.git` copy; exit 0. Census report is ignored at `logs/train_ingestion_reconciliation.json`.
- Full evidence and changed-file list: `tools/checkpoints/2026-11-15_P2_INGESTION_RECONCILIATION_COMPLETE.md`.
- P3 remains IN_PROGRESS. Next add the versioned QuerySpec schema and a reviewed business-held-out gold evaluation; measure intent/slots/schema validity/ambiguity recall. Existing query coverage is not accuracy. Keep holdout out of tuning and do not open train answers before predictions are frozen.
- No Git repository was initialized; no original sources, official checkout, main, train labels, or public-test data were changed/read. No commit or push.

## P3 checkpoint — schema and first holdout, 2026-11-15

- QuerySpec v1 JSON Schema, serializer/validator, and regression tests added. Generated train specs validate 2,843/2,843 (100% structural validity); full-train coverage 2,843/3,000 and executable coverage 1,620/3,000 remain coverage metrics only.
- First agent-reviewed business-held-out question set (`biz_107`–`biz_112`, 48 questions): intent accuracy 41/48 = 85.42%; core slot exact match 23/48 = 47.92%; slot micro-F1 84.21%; schema-valid 45/45 generated outputs. Ambiguity recall not measurable (zero positive gold examples). Entity/unit/filter accuracy not included; independent human review is still needed.
- P3 is **IN_PROGRESS / NOT PASSED**: slot exact match is below 81%, ambiguity recall is not measured. Preserve this inspected holdout unchanged and do not tune against it.
- Full test suite: 55 run, 52 passed, 3 Git-only skips, exit 0. Detailed checkpoint: `tools/checkpoints/2026-11-15_P3_QUERY_SCHEMA_HOLDOUT_PARTIAL.md`.
- Next: use separate dev cases to improve general intent/time/dimension parsing; add synthetic ambiguity metrics; create a new business-held-out sample after freezing those changes. Keep labels to evaluation only; no answer/public labels read here.

## Latest P3 development checkpoint — 2026-11-15

- Separate dev examples from `biz_125`–`biz_130` exposed two gaps: `dthu` was not retained in average-order-value/best-sales-day intent paths, and “đắt nhất” was missing from ranking synonyms. Both are fixed in `understanding.py`; focused tests 7/7 pass.
- Full suite after fixes: 56 run, 53 pass, 3 Git-only skips; exit 0. Current parser SHA-256: `238F4DEA12B9B248AD9049917C372D316643C4564316D82D95E2FB4E3D3A5697`.
- The first 48-item holdout is frozen for the earlier parser hash and must not be rerun or used for tuning. Its intent/slot metrics are historical baseline only, not current performance.
- P3 remains IN_PROGRESS / NOT PASSED. Next: continue on separate dev examples; add synthetic ambiguity cases and improve entity/unit/time/dimension slots; then create and freeze a new reviewed business-held-out evaluation with positive ambiguity cases.

### P3 relative-time alias — 2026-11-15

- Added tested `hnay` handling to `resolve()` and `resolve_as_of()`, anchored to record `as_of_date`.
- Focused suite 13/13; full suite 57 run, 54 pass, 3 Git-only skips; exit 0. No holdout/full-train replay after this code change.
- Evidence/hash: `tools/checkpoints/2026-11-15_P3_RELATIVE_ALIAS.md`. P3 remains IN_PROGRESS; next handle explicit unit/entity/dimension slots and positive ambiguity cases on separate development data, then use a new held-out evaluation.

## P3 explicit unit extraction — 2026-11-15

- Added conservative explicit-unit normalization; unspecified unit remains null.
- Pre-change regression: four explicit cases failed. Focused schema 4/4, understanding/time 13/13; full suite 58 run, 55 pass, 3 Git-dependent skips; exit 0.
- No holdout/full-train replay after parser change. P3 NOT PASSED. Evidence: `tools/checkpoints/2026-11-15_P3_UNIT_EXTRACTION.md`.
- Next: conservative entity extraction with ambiguity tests on development/synthetic inputs. Old holdout stays frozen; no labels/public data read.

## P3 catalog-grounded entity slot — 2026-11-15

- Unique optional profile-alias match returns canonical entity; competing matches return null with `entity_unresolved`; no catalog means null.
- Focused tests 5/5; complete suite 59 run, 56 pass, 3 Git-only skips; exit 0. No holdout replay/labels.
- Evidence: `tools/checkpoints/2026-11-15_P3_ENTITY_SLOT.md`. P3 remains NOT PASSED.
- Next: report ambiguity precision/recall/F1 on synthetic cases; then design a new held-out business evaluation after parser freeze. Preserve old holdout.

## P3 ambiguity evaluator — 2026-11-15

- Added ambiguity TP/FP/FN, precision/recall/F1; missing class denominators report null and reason.
- Synthetic suite 2/2; full suite 61 run, 58 pass, 3 Git-only skips; exit 0. No holdout replay or labels.
- Evidence: `tools/checkpoints/2026-11-15_P3_AMBIGUITY_METRICS.md`. P3 NOT PASSED.
- Next: fresh held-out business question split, positive/negative ambiguity review, freeze manifest then evaluate once. Do not reuse old inspected holdout.

## Latest checkpoint — P3-HOLDOUT-2 diagnostic (2026-11-15)

- Active copy: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3; no .git. Base snapshot: feature/offline-core commit 24cfa0908bd20f6e5b210366e956cae0d665b56e; no Git operations.
- Parser SHA-256: AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C.
- P3-HOLDOUT-2: 50 question-only candidates, 6 businesses, candidate SHA f05d7aab84fb23267dc156b5ec2d71a6bca02f41f60aa35822f9d4bbc59a2aad; gold SHA e9b3db32c3eaebf908e91338e112a3aa9d8b4cb1b4efb267414926de30fe2948.
- Diagnostic metrics: intent 44/50 = 88.00%; core slot exact 40/50 = 80.00% (gate FAIL); micro-F1 91.84%; schema validity 48/48 interpreted = 100%; ambiguity TP/FP/FN 1/2/1, P/R/F1 33.33%/50.00%/40.00%.
- Per-business below-gate: biz_115 slot 75%; biz_117 intent 77.78%, slot 66.67%; biz_118 intent and slot 66.67%.
- Gold is single-agent, not independently reviewed; prior full-train query-only diagnostics may have included these rows; two ambiguity positives are subjective. Diagnostic only; do not tune this split. Entity/unit/filter/answer accuracy NOT MEASURED.
- Full test suite: 61 run, 58 passed, 3 Git-dependent skips, exit 0. No source/test changes in this unit. No answer labels/public data read.
- Candidate/gold/metrics/error outputs remain local in ignored logs/; excluded from checkpoint archive due training-question content.
- Checkpoint artifact: tools/checkpoints/2026-11-15_P3_HOLDOUT2_DIAGNOSTIC.md; archive manifest/hash and extract-smoke results are reported in the session handoff after archive creation.
- Next exact unit: synthetic/separate development cases outside biz_107–biz_118 and biz_125–biz_130; make one general parser fix with a focused regression first. Do not tune on the frozen holdout.
## Archive verification — P3-HOLDOUT-2 diagnostic

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_holdout2-diagnostic.zip
- Archive SHA-256: e30fac0110e145d6e561974433c1a72527c0a1a969357365615024ff3b623b13 (external sidecar: work\checkpoints\2026-11-15_P3_HOLDOUT2_DIAGNOSTIC\archive.sha256; kept outside the ZIP to avoid self-reference).
- Archive entries: 76; internal manifest entries: 75; every SHA-256 verified; ZIP integrity PASS.
- Excluded: local logs, question candidates, gold annotations, train/public data, and generated smoke copies.
- Extracted smoke: work\rehydrated-smoke-P3-holdout2; 61 tests run, 58 passed, 3 Git-dependent skips; exit 0.
- Full post-build evidence: work\checkpoints\2026-11-15_P3_HOLDOUT2_DIAGNOSTIC\POST_BUILD_VERIFICATION.md.

## P3 evaluator full-slot coverage — 2026-11-15

- Expanded evaluator to cover metric, time, top_k, dimensions, sort, ambiguity_flags, entity, unit, and filters; added separate time/dimensions exact metrics.
- Focused synthetic tests 4/4; full suite 63 run, 60 passed, 3 Git-only skips; exit 0.
- Parser unchanged. Earlier P3-HOLDOUT-2 result remains a six-slot diagnostic and was not rerun; do not compare with nine-slot exact metrics.
- Evaluator SHA-256: 0ECE353F0A2DF805A9C04F2D8BD8A44DA63943D76C880D679D2846DB80AAD4CE.
- Test SHA-256: BABA7A5558408B786ACB9923B1D03C097758EE657F4AB2CEC02A42B7796105AE.
- Full evidence: tools/checkpoints/2026-11-15_P3_EVALUATOR_FULL_SLOTS.md. P3 not passed.
- Next exact unit: independent synthetic/development parser case, baseline failure first; never tune on frozen holdouts.
## P3 full-slot evaluator checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_full-slot-evaluator.zip
- SHA-256: 9b68864ee4eb3ccf25482ff0ba681daff711186c3143d0c51888196890325416; sidecar: work\checkpoints\2026-11-15_P3_EVALUATOR_FULL_SLOTS\archive.sha256.
- Archive contains 77 entries; 76 manifest entries verified, ZIP integrity PASS. No train/public data or generated logs are included.
- Extracted smoke: work\rehydrated-smoke-P3-full-slot-evaluator; 63 tests run, 60 passed, 3 Git-dependent skips; exit 0.
- Post-build verification and external manifest: work\checkpoints\2026-11-15_P3_EVALUATOR_FULL_SLOTS\POST_BUILD_VERIFICATION.md and post_build_manifest.sha256.

## P3 evaluator input validation — 2026-11-15

- Evaluator now validates candidate/gold shapes and rejects missing required slots before scoring.
- Focused tests 5/5; full suite 64 run, 61 passed, 3 Git-dependent skips; exit 0.
- No parser change and no holdout rerun.
- Evaluator SHA-256: D5B3BD4F25483523230FEE3AFFFCFB2C813EF264EF39200A3F6969A5A481F193.
- Test SHA-256: E8CF2BC48E56087CA7E1BDCB9FFA802DB691EDB0BF599EE250D031DFE95B2044.
- Checkpoint: tools/checkpoints/2026-11-15_P3_EVALUATOR_INPUT_VALIDATION.md. P3 still NOT PASSED.
## P3 evaluator input-validation checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_evaluator-input-validation.zip
- SHA-256: d7ed0bce2dfce1ff86fadcb3d4ea3767d7d6765409a8fabe0170c5d78e022586; sidecar: work\checkpoints\2026-11-15_P3_EVALUATOR_INPUT_VALIDATION\archive.sha256.
- 77 archive entries; all 76 internal manifest hashes verified; ZIP integrity PASS. No data or generated logs included.
- Extracted smoke: work\rehydrated-smoke-P3-evaluator-input-validation; 64 tests run, 61 passed, 3 Git-dependent skips; exit 0.
- Full verification: work\checkpoints\2026-11-15_P3_EVALUATOR_INPUT_VALIDATION\POST_BUILD_VERIFICATION.md; external manifest PASS.

## P3 year-to-date comparison — 2026-11-15

- Added deterministic year-to-date vs same-period-prior-year scope, anchored to as_of_date with leap-day clamping.
- Before fix: two new synthetic regressions failed. After: timeparse 8/8, understanding 7/7, full 66 run / 63 pass / 3 Git-only skips; exit 0.
- timeparse.py SHA-256: E5C7732AA5CABDB525603D00AD6509DDBD5075B21A1847D2C2B6D2DF379252A7.
- test_timeparse.py SHA-256: 6A24962027D1A318137483A19DFF7CC0A90E76FC0F6C4941B1ED57F1F9F45D38.
- No holdout replay, no answer labels/public data access, no Git action.
- Evidence: tools/checkpoints/2026-11-15_P3_YTD_COMPARISON.md. P3 remains NOT PASSED.
## P3 year-to-date comparison checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_ytd-comparison.zip
- SHA-256: 42db858192e687608e2a61fae53a63ef7eab0149d388618d6c207bcaf9cbcad4; sidecar: work\checkpoints\2026-11-15_P3_YTD_COMPARISON\archive.sha256.
- Archive entries: 78; internal manifest entries: 77; all hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extracted smoke: work\rehydrated-smoke-P3-ytd-comparison; 66 tests run, 63 passed, 3 Git-dependent skips; exit 0.
- Post-build verification: work\checkpoints\2026-11-15_P3_YTD_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

## P3 evaluator entity-catalog support — 2026-11-15

- Evaluator passes optional per-candidate entity catalogs to RulePlanner, enabling entity slot scoring for unique and ambiguous aliases.
- Before fix: 2 synthetic failures. After: focused 7/7; full 68 run, 65 pass, 3 Git-only skips; exit 0.
- Evaluator SHA-256: 1936BF2A67212E2C9047B626CE80057869CBD6307393DA64CFF9E2572671D4AE.
- Test SHA-256: DF9E4E9A0E7BE45FE82FED9129B4AEE9F4C19E66E6F6DBDBA0A94B0E999132D8.
- No parser change, no holdout replay, no labels/public data read.
- Evidence: tools/checkpoints/2026-11-15_P3_ENTITY_CATALOG_EVALUATOR.md. P3 remains NOT PASSED.
## P3 entity-catalog evaluator checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_entity-catalog-evaluator.zip
- SHA-256: e71fa47f6a6888feec7be797360473c56d516522905c760b9d50f984afa32a5b; sidecar: work\checkpoints\2026-11-15_P3_ENTITY_CATALOG_EVALUATOR\archive.sha256.
- Archive entries: 79; 78 internal manifest hashes verified; ZIP integrity PASS; no train/public data or generated logs.
- Extracted smoke: work\rehydrated-smoke-P3-entity-catalog-evaluator; 68 tests run, 65 passed, 3 Git-dependent skips; exit 0.
- Post-build evidence: work\checkpoints\2026-11-15_P3_ENTITY_CATALOG_EVALUATOR\POST_BUILD_VERIFICATION.md; external manifest PASS.

## P3 completed-month comparison — 2026-11-15

- Added full previous-month vs previous-month-before comparison with year rollover; incomplete relative-month requests abstain.
- Focused timeparse tests 11/11; full 71 run, 68 passed, 3 Git-only skips; exit 0.
- Prior to fix two synthetic positive cases failed. First code attempt had over-escaped regex literals; corrected after the tests remained red.
- timeparse.py SHA-256: EC2343B7CA8520AE5DE50FD2EC2A0856E3850FFE7E940F04CEAE7DA234A77925.
- test_timeparse.py SHA-256: AAE30C8EA8EF30477149E95ED995CCBD3602DCA5F6261E26965766794ADD524E.
- No holdout replay, no answer/public labels, no Git action. Evidence: tools/checkpoints/2026-11-15_P3_MONTH_COMPARISON.md.
## P3 completed-month checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_month-comparison.zip
- SHA-256: c2bef2c81bbc1155d73de1e498dcc44eda872a24d23429fa0b0d556f7eab2805; sidecar: work\checkpoints\2026-11-15_P3_MONTH_COMPARISON\archive.sha256.
- Archive entries: 80; 79 internal manifest hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extract smoke: work\rehydrated-smoke-P3-month-comparison; 71 tests run, 68 passed, 3 Git-dependent skips; exit 0.
- Full verification: work\checkpoints\2026-11-15_P3_MONTH_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

## P3 completed-quarter comparison — 2026-11-15

- Added completed-quarter versus previous-quarter scope; Q1 rollover to prior-year Q4/Q3 tested; incomplete relative comparisons abstain.
- Focused timeparse 14/14; full 74 run, 71 passed, 3 Git-only skips; exit 0.
- timeparse.py SHA-256: E5588BAD3222C85C8BFB57A8459B04A260488708239E96BE93E1F5CAF9F9CB26.
- test_timeparse.py SHA-256: 21526C889B62E2D9D55F8DB1D48040ED17BBB2F09180462D1ABBC344F5917BB6.
- No holdout replay, no answer/public labels, no Git action. Evidence: tools/checkpoints/2026-11-15_P3_QUARTER_COMPARISON.md. P3 not passed.
## P3 completed-quarter checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_quarter-comparison.zip
- SHA-256: 8ff6ff3e64d2a3b49050fd882f4f65e94bf8020dd2b1791f090a85db4479c056; sidecar: work\checkpoints\2026-11-15_P3_QUARTER_COMPARISON\archive.sha256.
- Archive entries: 81; all 80 internal manifest hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extract smoke: work\rehydrated-smoke-P3-quarter-comparison; 74 tests run, 71 passed, 3 Git-dependent skips; exit 0.
- Post-build verification: work\checkpoints\2026-11-15_P3_QUARTER_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

## Latest P3 checkpoint — year-to-date scope precedence (2026-11-15)

- Fixed YTD scope recognition taking precedence over the endpoint phrase “hôm nay”; period end remains the business question's `as_of_date`.
- Synthetic regression was red before the fix; timeparse 15/15 and full suite 75 run / 72 passed / 3 Git-only skips, exit 0.
- Source hashes: `timeparse.py` EA890116E57AFB5885DCB7831ACABB2B96B4A943D03BF0E7AF5BC465AD8FD2C0; test AD49A26D70497F58DDCE3BE4B30FCE0FFF594FD53A2B053694EC37944F9B3BFB.
- Development records are question-only, ignored, and excluded from the archive. No answer labels, public-test content, holdout examples, or Git operations were used.
- P3 remains NOT PASSED; no independent full-slot metric currently supports the 81% gate. Detailed checkpoint: `tools/checkpoints/2026-11-15_P3_YTD_SCOPE_PRECEDENCE.md`.

## Latest P3 checkpoint — requested-unit precedence (2026-11-15)

- Explicit requested units after “một/mỗi/từng” now take precedence over packaging units elsewhere in product text; added the `tuýp` alias.
- Synthetic regression failed before fix (`viên` vs expected `tuýp`); query schema 6/6 and full suite 76 run / 73 passed / 3 Git-only skips, exit 0.
- Source hashes: `understanding.py` 463073091ADAB75FCB4FBA1958232E82E62DF52D0CBAA1935580E99807032B39; `test_query_schema.py` 2B2AD96C7E5BA2E90461ADAD6C69DDA0527E6D4D705C5345906483DA564AD332.
- No holdout, train answer labels, public-test data, or Git actions used. Detailed checkpoint: `tools/checkpoints/2026-11-15_P3_REQUESTED_UNIT_PRECEDENCE.md`. P3 remains NOT PASSED.

## Latest P3 checkpoint — percent revenue-share cue (2026-11-15)

- Added share-intent recognition when a percent-marked question includes revenue, an explicit contribution cue, and a subject/category term.
- Synthetic regression failed before fix (`revenue` predicted, `revenue_share` expected); understanding tests 8/8 and full suite 77 run / 74 passed / 3 Git-only skips, exit 0.
- Source hashes: `understanding.py` 1C8B9C94C6BE480C860C922F676C5FE83409E9E9CE80BF6BD574D2053389BE92; `test_understanding.py` 98CA80F037D2FF1320327647132B9927EF474B1DC4BB87F2DB46017F41F7E24C.
- No holdout, answer labels, public-test data, or Git actions. Details: `tools/checkpoints/2026-11-15_P3_REVENUE_SHARE_CUE.md`. P3 remains NOT PASSED.

## Latest P3 checkpoint — supplier-ranking QuerySpec (2026-11-15)

- Supplier purchase ranking now yields a structured non-executable spec instead of product sales ranking.
- Synthetic regression failed before fix (`sales_ranking` predicted); understanding tests 9/9 and full suite 78 run / 75 passed / 3 Git-only skips, exit 0.
- Source hashes: `understanding.py` C4721BF01AD10FF24262E103AF278EAA9B09237D700F67D0A346196CA420AB15; `test_understanding.py` 0A77476F9709834220903772E843DA7B99A3873BD6FB704EFF4B114C3D06D281.
- No holdout, answer labels, public-test data, or Git actions. Details: `tools/checkpoints/2026-11-15_P3_SUPPLIER_RANKING_SPEC.md`. P3 remains NOT PASSED.


## Active workspace checkpoint — P3 blind review packet (2026-11-15)

- Current writable project: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af990f97d408191a5847ca24785860f`; source snapshot: `work\rehydrated-2026-11-15-P3\source`. The snapshot represents `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e` and has no `.git`; do not report a live branch or current Git status from this extracted copy.
- User confirmed P1 and P2 complete. P1 is complete at L1 structural profile scope; P2 reconciliation remains 30/30 businesses, 128 files, 339/339 tables/sheets, 3,997,277 = 3,997,042 accepted + 0 rejected + 235 skipped, zero failures.
- P3 remains IN_PROGRESS / NOT PASSED. A question-only review packet is ready at `work\reviews\P3_HOLDOUT3`; 72 primary items across six fresh businesses, plus four disjoint no-explicit-time challenge items. Candidate question source only: `sources\train.zip::train/questions.jsonl`. No answer labels or public-test content were opened; the parser was not run on candidates.
- The four-item challenge is too small for a stable ambiguity-recall claim. No P3 percentage is claimed. Packet protocol and hashes are recorded in `work\reviews\P3_HOLDOUT3\freeze_manifest.json` and `tools/checkpoints/2026-11-15_P3_BLIND_REVIEW_PACKET.md`.
- P4–P8 have not started. Per playbook gates, continue after independent review/adjudication and one frozen P3 evaluation meets target; do not tune on that set.
- Current source test evidence before this documentation-only work: 78 tests, 75 passed, 3 Git-dependent hygiene skips, exit 0. Rerun after this checkpoint and record the result in the handoff.
- No source code, `sources/`, official checkout, or `main` was modified. No Git operation, commit, push, merge, reset, clean, ACL, or privilege change occurred.
- Exact next action: obtain independent annotations for the packet, adjudicate disagreements, freeze gold, then run `tools/evaluate_queryspec_holdout.py` once. P4 is gated on P3 acceptance.

- Post-checkpoint verification at 2026-11-15 20:23 Asia/Bangkok: `PYTHONPATH=src python -m unittest discover -s tests -v` exited 0; 78 run, 75 passed, 3 Git-dependent hygiene skips. Packet integrity passed (72+4, no overlap, 76 annotation rows, candidate hashes valid).
# Current user priority — submission-ready build (2026-11-15)

- User changed priority from completing every playbook phase to preparing the strongest valid submission today, with strict GO/NO-GO and one Test Solution attempt maximum.
- P0 repository/data state and P1 official interface/rules were checked; P1/P2 are user-confirmed complete. The active no-Git source snapshot is separate from the clean official checkout at `feature/offline-core` / `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Fixed answer persistence, log contract, and streamed question ingestion. Full unittest suite: 80 run / 77 passed / 3 Git-dependent skips. Twelve train-only questions passed end-to-end twice with deterministic JSONL and logs; no labels or public/private test data used.
- Strict status is **NO-GO**: no Docker-family CLI found, WSL status failed, and Docker build/GPU/offline runtime remain unverified. No artifact image/tar.gz, MD5, upload, or portal submission. No slot used.
- Final isolated Docker build context: `work/submission-build/context-final-verified-2026-11-15`. Per-file hashes are in its manifest; aggregate size and manifest checksum are in `work/submission-build/FINAL_ARTIFACT_RECORD.md`. It is not an image or upload artifact.
- Next action: validate the build context on a host with supported Docker/GPU, then decide whether to consume the Test Solution smoke attempt. Test Solution gives technical feedback, not a scored result. Recheck official portal details before submission.
- P3 independent review remains NOT COMPLETED / NOT PASSED; no annotations fabricated. See `tools/checkpoints/2026-11-15_SUBMISSION_PREFLIGHT.md` and `docs/NEXT_SESSION_HANDOFF.md`.
# Current task — Public Test JSONL candidate (2026-11-15)

- User asked to create sufficient submission artifacts. Screenshots distinguish Public Submissions (JSONL on public data) from Test Solution (Docker image URL + MD5); user has not requested portal upload in this turn.
- Work in `work/rehydrated-2026-11-15-P3/source` only. Official repo rechecked read-only: `feature/offline-core`, `24cfa0908bd20f6e5b210366e956cae0d665b56e`, clean. `sources/` is read-only.
- Starting one inference pass on `sources/public_test.zip` to make a candidate `submission.jsonl`; public labels are absent. Do not tune or rerun after inspecting public predictions. No accuracy claim.
- Docker image is separate and still blocked: no Docker-family CLI/runtime. No portal upload, image, tarball, MD5, or Test Solution submission.
- Details and exact next command: `tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_START.md`.
# Current state — public submission JSONL candidate (2026-11-15)

- P0 recheck: official checkout clean on feature/offline-core at 24cfa0908bd20f6e5b210366e956cae0d665b56e; origin URL verified. All current work remains in the no-Git isolated snapshot.
- P1/P2 remain user-confirmed complete with existing profile and reconciliation evidence.
- Public JSONL candidate is structurally VERIFIED: 1,000/1,000 question IDs and traces; validator exit 0; no runtime errors. 718 abstain / 282 answered; answer accuracy and PA are not measured. No public labels existed or were used; no tuning/rerun.
- Upload review package: work/submission-build/public-test-submission-2026-11-15. JSONL SHA-256 0de940823521e386477efeb76c26d6533e61cabf1977b5c0d9cbb6fd0d61e112; MD5 85b4acc0abf681c8b5a6a6a6812910ab; 44,806 bytes. Not uploaded.
- Public output is not a Test Solution image. Docker/Test Solution remains BLOCKED (no Docker-family runtime); no image/tar/Google upload/portal attempt.
- No local CI workflow or GitHub Actions run/build was found; no paid/remote builder was invoked.
- P3 remains NOT PASSED; P4–P8 and the full nine-workstream objective remain active. Details: tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_COMPLETE.md.


## 2026-11-16 20:35 GMT+7 — active targeted bugfix checkpoint

- User asked for evidence-based bug fixes only; no unrelated refactoring. Current source is the isolated snapshot at `work/rehydrated-2026-11-15-P3/source`, without `.git`. `sources/` is read-only; official checkout untouched.
- `metrics.py`: introduced inbound purchase ledger exclusion in revenue, daily-revenue line discovery, quantity/sales ranking/order count/cancellation source selection; prioritized normalized base quantity columns before raw/package quantity.
- `tests/test_pipeline.py`: 3 new regressions for purchase-ledger false positives and normalized quantity ranking.
- Focused pipeline tests: 56 passed. Full suite: 167 run, 164 passed, 3 Git-dependent hygiene skips, exit 0.
- Train replay v19 freeze: 3,000 predictions/traces, answer_labels_accessed=false at generation. Code manifest `0e341e7d913b4c4219d155724297bd9f403551428de177abfc1c6f7cc4dcd12f`; input manifest `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; prediction `5f168fe9b624a78c9b99e314020acbe28ae0e04677346a3f1750bd6676c73805`; trace `f8fdcad5b1e525fb58b8df574cca7d4b47c2bbb637eca9934ee6b70ac791c358`.
- After frozen replay validation, train evaluator scored 30 correct / 4 wrong / 2,966 abstain; PA 0.8667%, answered accuracy 88.24%, p95 21 ms, runtime errors 0. v18 was 28/10/2,962, PA 0.6%; improvement measured in-sample only. Errors: cancellation_rate 3, sales_ranking 1. Public labels were not read.
- Current public inference process: output under `work/submission-build/public-submission-2026-11-16-v19/`; finish, run submission validator, count answers/abstentions/runtime errors, hash and record artifact. No accuracy claim without labels.
- Source hashes: `metrics.py` SHA256 `C624C373FE31F90FD70DEA4F781CDFCFD3C6968394BCD3EA3CD53769A485BBBD`; `tests/test_pipeline.py` SHA256 `A65B5E4C25D448B87AD48B7EC6C213B18F32DA2131FB56557B651B87C120D566`.
- Checkpoint: `tools/checkpoints/2026-11-16T2035+07-00_P6_V19_PURCHASE_BASE_QUANTITY_FIX_TRAIN_COMPLETE.md`.



## Current state — 2026-11-17 — v26

- Full report: `docs/PROGRESS_REPORT_2026-11-17.md`; checkpoint: `tools/checkpoints/2026-11-17T0821+07-00_P6_V26_REPORT_SYNC.md`.
- Full suite: 189 run, 186 passed, 3 Git-dependent skips. Pipeline: 69/69 passed.
- Train v26: 237 correct, 6 wrong, 2,757 abstain / 3,000; 97.53% answered accuracy, 8.10% coverage, PA 7.70%, p95 756 ms, zero runtime errors. In-sample only.
- Remaining errors: 3 rankings and 3 cancellation-rate rule/label discrepancies. Keep cancellation semantics; do not hardcode or tune answers.
- Public labels not read. Existing source-root submission JSONL is stale (998 abstain / 2 number); no v26 output confirmed.
- Core v26 code/tests were verified to match GitHub `main`; this update only synchronizes reports/status/checkpoint.
- Next: fix sales rankings with evidence and tests; freeze and replay train; only then generate one structural public candidate without tuning from public questions.


## 2026-11-19 — Current working state: multi-bundle vertical slice

- Active repository: `pl2n/DataMate` (private fork); active branch: `feature/multi-bundle-query`.
- Upstream repository has not been modified.
- Added a bounded composite implementation for `financial_metric_comparison`: two components (`revenue`, `collected_amount`) share one explicit period and use existing metric logic.
- Component verification reuses the existing verifier. Any required component failure abstains the entire composite.
- Added synthetic tests and architecture documentation. CI workflow has been added; verification is pending.
- Known non-goals: arbitrary conjunction splitting, derived differences, cross-period comparisons, dynamic bundle discovery, and partial composite answers.


### CI status — 2026-11-19

- Implementation commit: `77dbd90e204356211c70a2cf56f7f52249cde01a`.
- GitHub Actions ran 197 tests. Composite and functional tests passed; 2 hygiene tests failed against pre-existing tracked `CODEX PROGRESS` (over 1 MB and matching secret-like regex). The file was not modified.
- Do not mark the branch verified until the archive/hygiene issue is resolved without weakening secret scanning, then the full suite passes.
- Workflow: https://github.com/pl2n/DataMate/actions/runs/44541834717


## 2026-11-19 — bounded Excel grouped-header support

- Added explicit two-row merged-group header recognition in XLSX ingestion.
- Preserved raw header rows and physical row numbers on `Table`; surfaced them in ingestion `profile()`.
- Tests cover grouped header mapping, source provenance, profile serialization, and rejecting a single merged report title as a grouped header.
- CI `44545450222`: 199 tests ran; 197 passed and 2 existing repository-hygiene tests failed on `CODEX PROGRESS` (size and secret-like regex). No hygiene rule was bypassed.
- See `tools/checkpoints/2026-11-19_EXCEL_GROUPED_HEADERS.md`.


## 2026-11-19 — semantic mapping CI result

- GitHub Actions run `44546168818`: 203 tests executed; 201 passed. The four semantic mapping tests passed.
- Two pre-existing repository-hygiene failures remain on tracked `CODEX PROGRESS` (size > 1 MB and secret-like regex match). Do not bypass the checks.
- Run: https://github.com/pl2n/DataMate/actions/runs/44546168818


## 2026-11-19 — relationship validation CI result

- GitHub Actions run `44546976679`: 210 tests executed; 208 passed. All relationship discovery tests passed.
- Two pre-existing repository-hygiene failures remain on tracked `CODEX PROGRESS` (size > 1 MB and secret-like regex match).
- Run: https://github.com/pl2n/DataMate/actions/runs/44546976679


## 2026-11-19 — bundle registry CI result

- GitHub Actions run `44547696247`: 216 tests executed; 214 passed. Bundle registry and composite tests passed.
- Two pre-existing repository-hygiene failures remain on `CODEX PROGRESS` (size > 1 MB and secret-like regex match). No security checks were weakened.
- Run: https://github.com/pl2n/DataMate/actions/runs/44547696247


## 2026-11-19 — bundle registry test result

- CI run `44547696247`: 216 tests executed; 214 passed. New bundle and composite tests passed.
- Two existing hygiene checks remain red because of tracked `CODEX PROGRESS`; no bypass was made.


## 2026-11-19 — schema catalog CI result

- GitHub Actions run `44548265235`: 219 tests executed; 217 passed. New schema catalog integration tests passed.
- Two pre-existing repository-hygiene failures remain on tracked `CODEX PROGRESS` (size and secret-like regex). No bypass was made.
- Run: https://github.com/pl2n/DataMate/actions/runs/44548265235


## 2026-11-19 — requirement extraction CI result

- Initial run found a stale `QueryRequirement` type reference after the model moved to `requirements.py`; fixed in commit `45330bc`.
- Follow-up run `44548881088`: 222 tests executed, no code/test errors, 220 passed. Two pre-existing `CODEX PROGRESS` hygiene checks remain red.
- Run: https://github.com/pl2n/DataMate/actions/runs/44548881088

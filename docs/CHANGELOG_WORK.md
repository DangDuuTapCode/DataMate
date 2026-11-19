# Work changelog

## 2026-11-16 — P6 daily revenue threshold day-count slice started

- Continued from validated v16 train diagnostics. Recorded a generic train error where a count-of-days-above-revenue-threshold question was routed to purchase quantity.
- Planned a fail-closed planner/executor feature using after-discount line revenue grouped by date, with synthetic tests before a new frozen train diagnostic.
- Start checkpoint: `tools/checkpoints/2026-11-16T1708+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_START.md`. No source changes or new replay yet; v16 preserved.

## 2026-11-16 — P6 daily revenue threshold day-count implemented

- Added explicit threshold intent parsing, QueryPlan threshold transfer, revenue-by-day aggregation, numeric verifier support, and fail-closed tests for ambiguous thresholds and sources.
- Fixed the payment status alias and ensured only settled payment events contribute to collected amount. Updated synthetic fallback revenue status defaults to exclude unsuccessful and in-transit rows while retaining fail-closed behavior for pending/unknown states and honoring explicit split rulebook clauses.
- Focused suite: 71 passed. Complete suite: 160 run, 157 passed, 3 Git-dependent skips, exit 0.
- Completion checkpoint: `tools/checkpoints/2026-11-16T1717+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_COMPLETE.md`. Next: new hash-frozen train replay v17; no public/private labels.
- Started v17 generation in a fresh output folder from the frozen metadata-complete train input; no labels are read by generation. Start checkpoint: `tools/checkpoints/2026-11-16T1718+07-00_P6_V17_TRAIN_REPLAY_START.md`.
- v17 completed and passed pre-evaluation freeze validation: 3,000 prediction/trace rows, 30 businesses, schema/order/ID and all hashes verified; rulebook/calendar included; `answer_labels_accessed=false`. Checkpoint: `tools/checkpoints/2026-11-16T1728+07-00_P6_V17_TRAIN_FREEZE_VALIDATED.md`. Proceeding to train-only evaluator, which revalidates first.
- Train-only v17 diagnostic: 26 correct, 3 wrong, 2,971 abstain; coverage 0.9667%, answered accuracy 89.66%, penalized accuracy 0.7667%, runtime errors 0, p95 22 ms. New threshold intent recognized the query but abstained for missing line/date join. Schema-only scan verified a unique invoice key and complete line-key coverage per README. Join start evidence: `tools/checkpoints/2026-11-16T1736+07-00_P6_DAILY_REVENUE_SAFE_JOIN_START.md`.
- Added a complete unique-key line-to-invoice join and synthetic tests; the real biz_124 smoke still abstained. Diagnosis found metrics ignored `Table.date_system` for numeric Excel serial dates (31,997 invoice rows). The workbook reader and strict normalizer already carry epoch support; propagation fix started. Evidence: `tools/checkpoints/2026-11-16T1742+07-00_P6_EXCEL_DATE_SYSTEM_PROPAGATION_START.md`.

## 2026-11-16 — P1 targeted competition-rule review

- Compared the supplied regulation, official Vietnamese regulation PDF, official DataMate portal, and current submission-related files. Confirmed that the architecture is aligned in concept but full compliance remains unverified.
- Recorded unresolved risks: external scenario-set rights and track permission, contest-data packaging, no-model category mismatch, incomplete image license inventory, and competition-time code sharing. The working copy currently has no training archive, but Dockerfile copies all of `training_code/`; do not add a dataset absent explicit official permission.
- No source code, dataset, public/private test labels, or submission artifact changed. Full scoped evidence and next steps: `tools/checkpoints/2026-11-16T1446+07-00_P1_TARGETED_COMPETITION_RULE_REVIEW.md`.

## 2026-11-16 — P6 v14 replay frozen and validated

- Generated 3,000 train predictions and traces with labels excluded. Source/code, input, prediction, trace, IDs/order, count, and output schema validation all passed before scoring; `answer_labels_accessed=false`.
- Input SHA-256 `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`; code SHA-256 `f88f6668768907c25467d91611525bfae5b4bbb088f6ce30b9a62dfbd2b94ee0`; predictions SHA-256 `1766014125e830ad93b6f9f19f889e015fd5f93ebcc88d4fcc270ce127c9f3e5`; trace SHA-256 `bf686f6ac857c7652bffe9c0ef11bbc715d52898d68fadbe61e71e8c1f7df5c9`.
- Next is train-only diagnostic evaluation through the evaluator, which repeats freeze validation before reading answers. Checkpoint: `tools/checkpoints/2026-11-16T1448+07-00_P6_V14_FREEZE_VALIDATED.md`.

## 2026-11-16 — P6 v14 replay fixture defect identified

- The v14 evaluator read train answers only after freeze validation, then reported all 3,000 as abstentions. Trace inspection confirmed every row failed with `RulebookError` because replay input omitted `rulebook.md`; `calendar.csv` was also absent.
- This makes the v14 score unusable as a system quality metric. Preserved the replay and report unchanged. No production code changed; no public/private labels accessed.
- Next: create a separate complete train input with only rulebook/calendar metadata, generate a new frozen replay, validate before any evaluation. Evidence: `tools/checkpoints/2026-11-16T1450+07-00_P6_V14_INCOMPLETE_INPUT_FINDING.md`.

## 2026-11-16 — P6 metadata-complete train replay v15 started

- Copied the existing train questions/business data into a new input root and added only `train/rulebook.md` and `train/calendar.csv`; original input and source archive remain unchanged. Metadata smoke passed (rulebook loaded, 1,461 calendar dates, Tết configured). An initial smoke-print typo was corrected; no implementation defect.
- Started a new 3,000-question replay. It remains active and must finish before freeze validation/scoring; do not launch a duplicate. No public/private labels accessed.
- Checkpoint: `tools/checkpoints/2026-11-16T1626+07-00_P6_COMPLETE_TRAIN_INPUT_V15_START.md`.

## 2026-11-16 — P6 replay input manifest integrity gap found

- v15 generated 3,000 predictions/traces with zero runtime errors and `answer_labels_accessed=false`, but was not scored. `build_input_manifest` hashes only questions and data files, omitting the loaded `rulebook.md` and `calendar.csv`; the v15 hash exactly matched v13 despite different metadata.
- Adding the split metadata files to the input manifest and focused hash-change tests is required before any train-label evaluation. Preserve v15 unchanged.
- Checkpoint: `tools/checkpoints/2026-11-16T1629+07-00_P6_REPLAY_METADATA_HASH_FIX_START.md`.

## 2026-11-16 — P6 replay metadata hashing fixed and tested

- Replay preflight now requires and hashes `rulebook.md` and `calendar.csv`. The integration fixture includes split rules/calendar and valid line identity; regressions prove that modifying either metadata file invalidates a frozen replay.
- Targeted replay evaluation tests: 3 passed. Initial run exposed an outdated synthetic fixture missing product identity (2 passed/1 failed); updated fake fixture, then 3/3 passed.
- v15 remains preserved and unscored due its incomplete manifest. Next generate v16 and ensure the manifest includes both split metadata files before train-only evaluation. Checkpoint: `tools/checkpoints/2026-11-16T1633+07-00_P6_REPLAY_METADATA_HASH_FIX_COMPLETE.md`.

## 2026-11-16 — P6 v16 replay started

- Started a fresh replay on metadata-complete inputs after the freeze-manifest fix and 3/3 targeted test pass. New output directory is isolated; no labels will be accessed until validation succeeds.
- Session `50250`; start checkpoint: `tools/checkpoints/2026-11-16T1635+07-00_P6_V16_METADATA_HASHED_REPLAY_START.md`.

## 2026-11-16 — P6 v16 metadata-hashed freeze validated

- Generated 3,000 train predictions/traces and validated the new manifest. It explicitly includes `rulebook.md` and `calendar.csv`; code/input/prediction/trace checksums, IDs/order, count, and schema passed. No train labels were opened.
- Input SHA-256 `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; code SHA-256 `44732108ea168b39d1e7984de4900c87b357f1a551c68013a35584801d275830`; prediction SHA-256 `639f650e8436ce64ef26466b55b4603dc37005494cfa090b71af0134755c4e81`; trace SHA-256 `26e7f504a7adf0c520c05a6b41616c521c2806741ac2ce20edde2a5f08ec2b18`.
- Next: evaluator may read train labels only after repeating validation. Checkpoint: `tools/checkpoints/2026-11-16T1642+07-00_P6_V16_METADATA_HASHED_FREEZE_VALIDATED.md`.

## 2026-11-16 — P6 v16 train-only diagnostic complete

- Evaluator revalidated v16 then read official train answers only. Results: 26/3,000 correct, 4 wrong, 2,970 abstain; 1% coverage, 86.67% answered accuracy, 13.33% false-answer rate, 0.733% penalized accuracy; 70/70 unanswerable abstentions correct; p95 18 ms; zero runtime errors.
- The result is in-sample and not acceptance; prior train question-only development prevents treating it as an independent holdout. Dominant abstention buckets: unsupported intent 1,169, ambiguous entity 783, missing column 658. Four wrongs: cancellation rate (2), quantity (1), sales ranking (1).
- Next: evidence-based error analysis/fixes using train labels only after freeze and synthetic regression. Full report/checkpoint: `tools/checkpoints/2026-11-16T1645+07-00_P6_V16_TRAIN_DIAGNOSTIC_EVALUATED.md`.

## 2026-11-16 — P6 restored rulebook/calendar planner wiring

- Restored `RulePlanner`'s `split_rules` argument and forwarding of the Tết lunar window and comparison support flag after a freeze-validation mismatch exposed that `main.run` passed an unsupported argument.
- Before fix: 39 focused tests passed and the Tết runner errored with `TypeError`. After fix: timeparse, understanding, and mounted-calendar runner checks passed 40/40.
- v13 predictions were preserved unevaluated and train labels were not opened. Next replay is v14, with freeze validation before scoring.
- Checkpoint: `tools/checkpoints/2026-11-16T1435+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_COMPLETE.md`.

## 2026-11-16 — P5 typed verifier gate (bounded slice completed)

- Added adversarial verification for empty and overlong ranking lists. Verified the existing gates for intent/output type, finite confidence, evidence shape, and fewer-than-k valid results.
- Focused tests: 5 passed. The verifier implementation already existed in the working copy; no production source was rewritten. P5 overall remains partial/not accepted.
- Checkpoint: `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`.

## 2026-11-16 — P4 split calendar and rulebook-driven Tết support (completed)

- Runtime now receives the active split's lunar calendar and rulebook. Tết dates are derived from the configured lunar-day interval and calendar; equal-length pre-Tết comparison is allowed only where the rulebook supports it. Gregorian periods remain unchanged and take precedence over “Tết” used in entity names.
- Fixed parser handling for the official Unicode minus `−` in `Y − 1` after a metadata smoke test found it.
- Focused tests: 19 time parser tests and 1 runner test passed. Read-only smoke on only `rulebook.md` and `calendar.csv` from train and public archives passed.
- Also recorded a preliminary compliance finding: external scenario data permission/provenance is unresolved; do not train on or package it without track-specific permission and rights evidence. No full suite or public-test question/answer access.
- Targeted compliance check: no model is declared, but portal categories shown in the user's screenshot are API/LLM/SLM; this needs track-specific confirmation. `openpyxl` and a vLLM base image are listed without a complete license/provenance inventory; section 4.5 is not yet evidenced.
- Checkpoint: `tools/checkpoints/2026-11-16T1408+07-00_P4_SPLIT_CALENDAR_TET_SUPPORT_COMPLETE.md`.

## 2026-11-16 — P4/P5 competition-rule conformance correction (completed)

- Added split-specific `rulebook.md` loading, line-level after-discount revenue selection, rulebook status/date defaults, cancellation-rate numerator, ranking metric/tie-break handling, and safe fewer-than-k serialization.
- The verifier now checks intent/type compatibility, confidence/evidence shape, and ranking cardinality without rejecting valid short results when the split has fewer candidates.
- Focused regression set passed 16/16 across two targeted commands. Full suite was intentionally not run under the user's time constraint. Checkpoint: `tools/checkpoints/2026-11-16T1344+07-00_P4_COMPETITION_RULEBOOK_CONFORMANCE_COMPLETE.md`.

## 2026-11-16 — P4 VND and million-suffix normalization (completed)

- Start checkpoint: `tools/checkpoints/2026-11-16T1310+07-00_P4_VND_CURRENCY_SEPARATOR_START.md`.
- Fixed explicit VND grouping plus Vietnamese `tr`/`triệu` suffixes; bare `10.000` and ambiguous `1,156tr` remain fail-closed without column evidence. Parsed all values in biz_127/129 documented after-discount detail columns in a read-only audit.
- Detail/order reconciliation exact: biz_127 9,605/33,874; biz_129 11,587/38,499, so no join/source substitution was made. Focused normalization+ingestion 25 passed; full suite 142 run, 139 passed, 3 Git-only skips. v12 predictions/hash match v11. Checkpoint: `tools/checkpoints/2026-11-16T1325+07-00_P4_VND_MILLION_NORMALIZATION_COMPLETE.md`.

## 2026-11-16 — P4/P5 no-data reason coverage (completed)

- Start checkpoint: `tools/checkpoints/2026-11-16T1255+07-00_P4_NO_DATA_REASON_INTENT_COVERAGE_START.md`.
- Added synthetic coverage across four more intents, malformed dates, and zero collection. Added explicit regression for user-confirmed revenue exclusions (canceled, returned, failed delivery).
- Recorded D10 in decisions and the business coverage contract. Focused pipeline: 40 passed; full suite: 140 run, 137 passed, 3 Git-only skips. Source code did not change. Evidence: `tools/checkpoints/2026-11-16T1300+07-00_P4_NO_DATA_REASON_INTENT_COVERAGE_COMPLETE.md`.

## 2026-11-16 — P4/P5 no-data versus zero (completed)

- Added internal `no_data` reason for an empty in-period source while retaining numeric zero when matching data sums to zero.
- Focused tests 48/48; full suite 136 run, 133 passed, 3 Git-dependent skips.
- Frozen v11 replay validated 3,000 predictions/traces before labels were accessed by the evaluator. Predictions and score match v10: 40 correct, 44 wrong, 2,916 abstain, PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 37 ms, runtime errors 0. `no_data` was absent from train traces and is verified synthetically.
- Added `docs/VERIFIER_REASON_CODES.md`. Full completion evidence and hashes: `tools/checkpoints/2026-11-16T1248+07-00_P4_NO_DATA_ZERO_SEMANTICS_COMPLETE.md`.

## 2026-11-16 — P5 order-status abstention reasons

- Added trace reason codes for missing, unknown, and conflicting order statuses while preserving output JSONL schema.
- Focused pipeline/API suite: 47 passed; full suite: 135 run, 132 passed, 3 Git-dependent skips.
- Full v10 train replay validated and evaluated after freeze: 3,000 predictions/traces, byte-identical prediction JSONL to v9; 40 correct, 44 wrong, 2,916 abstain, PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 18 ms, no runtime errors. New codes did not occur in train traces; their behavior is verified synthetically.
- Start/completion evidence: `tools/checkpoints/2026-11-16T1224+07-00_P5_ORDER_STATUS_TRACE_REASON_START.md` and `tools/checkpoints/2026-11-16T1232+07-00_P5_ORDER_STATUS_TRACE_REASON_COMPLETE.md`.

## 2026-11-16 — shared unsuccessful-order statuses

- Added a non-mutating status classifier that keeps cancellation, return, and failed delivery distinct while counting all three in the unsuccessful-order-rate numerator; pending and in-transit remain separate.
- Switched order status discovery to exact documented headers, including `Kết quả` and `Ghi chú TT`, avoiding substring matches into customer/e-invoice fields. Unknown/missing statuses, conflicting per-order classes, and missing exact status fields abstain; raw status values are retained.
- Added five pipeline regressions. Focused suite: 35 passed. Read-only train data checks (without labels) covered all 4 raw statuses in biz_101 and all 7 in biz_116; both produced whole-period diagnostics.
- Full suite: 132 run, 129 passed, 3 Git-only skips. Frozen v9 evaluation (3,000 train questions) after hash validation: 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 42 ms, runtime errors 0. Cancellation-rate answers scored 2 correct/12 wrong among 14 versus v8 12/2; recorded as mismatch with the train references, not as permission to override the user rule. In-sample diagnostic only.
- Full provenance: `tools/checkpoints/2026-11-16T1154+07-00_UNSUCCESSFUL_ORDER_STATUS_RULE_COMPLETE.md`.

## 2026-11-16 — P7 matrix refresh from v9

- Corrected stale `v7` and `0/30` hardcoded scope text in the coverage-matrix builder; added a regression proving version-neutral replay labels and calculated L5 denominators.
- Regenerated `docs/BUSINESS_COVERAGE_V9.md` and `work/evaluation/business-coverage-matrix-train-v2-2026-11-16.json` from the v9 evaluation report without reopening labels. L1/L2/L4 30/30; L3/L5 0/30.
- Focused tests: 4 passed; full suite: 133 run, 130 passed, 3 Git-dependent skips, exit 0. Start and completion evidence: `tools/checkpoints/2026-11-16T1156+07-00_P7_MATRIX_REFRESH_START.md` and `tools/checkpoints/2026-11-16T1156+07-00_P7_MATRIX_REFRESH_COMPLETE.md`.

## 2026-11-16 — P6 current-code v7 train replay

- Froze predictions for 3,000 train questions/30 businesses with `answer_labels_accessed=false`; checksum validation passed before the evaluator read train labels.
- Metrics: PA `0.00333`; 47 correct, 37 wrong, 2,916 abstain; 2.80% coverage; 55.95% answered accuracy; 44.05% false-answer rate; 70/70 unanswerable cases correctly abstained; p95 18 ms; runtime errors `{}`.
- Compared with v6b: 4 more correct and 9 fewer wrong. The source change bundle includes generic interpretation guards and failed/nonfinal status exclusions, so do not attribute the aggregate change to one rule. It is still an in-sample diagnostic and below all acceptance targets.
- 30 remaining wrong revenue answers are numeric-vs-numeric and concentrated in biz_127/129. Source amount semantics and order/detail reconciliation remain unresolved; no answer-specific tuning performed.
- Full hashes, metrics and next actions: `tools/checkpoints/2026-11-16T1018+07-00_P6_CURRENT_CODE_REPLAY_COMPLETE.md`.

## 2026-11-16 — P4 incomplete-order status firewall

- Excluded explicit failed-delivery and nonfinal statuses (`không giao được`, `đang vận chuyển`, `failed`, `shipping`, `in transit`, `pending`) from revenue, quantity, and ranking aggregation; canceled/returned handling remains.
- Added a synthetic pipeline regression for completed vs failed/in-transit/pending orders.
- Focused pipeline suite: 26 passed. Latest full suite: 116 run, 113 passed, 3 Git-only skips, exit 0.
- No replay was run for this change. v6b remains an in-sample baseline and does not score the current code. P4 remains partial pending authoritative source/amount/join semantics.
- Evidence: `tools/checkpoints/2026-11-16T1010+07-00_P4_NONFINAL_STATUS_FIREWALL_COMPLETE.md`.

## 2026-11-16 — P3/P5 interpretation safety and P6 v6b evaluation

- Added generic detection for named product filters including `món`, `tiền bán`, and `bán <name>`; added unimplemented product/channel/payment breakdowns including counter service; structured revenue-share and best-sales-day handling for common spelling noise/English `revenue`; average revenue no longer falls through to total revenue.
- Scalar revenue execution now returns `invalid_unit` when the QuerySpec explicitly asks for a non-currency unit such as percent. Submission record schema is unchanged.
- Added seven synthetic regressions across interpretation, unsupported breakdowns, scalar unit verification, and false-positive protection. Focused understanding/pipeline/schema tests: 48/48 passed. Full suite: 115 run, 112 passed, 3 Git-only skips, exit 0.
- Frozen v6b train replay: PA `-0.001`, 43 correct, 46 wrong, 2,911 abstain, 2.97% coverage, 48.31% answered accuracy, 51.69% false-answer rate, p95 44 ms. Compared with v5: 14 fewer wrong and 2 fewer correct. In-sample diagnostic, not independent acceptance; last product/channel follow-up is not covered by v6b.
- The remaining 39 wrong revenue predictions are all numeric-vs-numeric, concentrated in biz_127/129/116. Source schemas contain different gross/paid/balance meanings and statuses; no aggregation change was made without an authoritative contract. Exact provenance and limitations are in `tools/checkpoints/2026-11-16T1004+07-00_P3_P6_REVENUE_ANALYSIS_COMPLETE.md`.
- User skipped P3 reviewer; P3 remains NOT VERIFIED / NOT PASSED. The incomplete first v6 output is retained unevaluated. No label-specific logic, public-test tuning, official checkout writes, Git operations, Docker, or source archive mutation.

## 2026-11-16 — P5 structured executor reasons

- Added `Executor.execute_with_reason()` and wired its diagnostics into internal traces. `missing_column`, `invalid_unit`, and `join_unsafe` now reflect required schema, unsupported unit conversion, and product-key joins that cannot be performed safely.
- Preserved the external submission JSONL schema. Added pipeline and API tests for all three reason codes and abstention serialization.
- Full suite: 108 run, 105 passed, 3 Git-only skips. Frozen v5 full train replay: 3,000 questions, PA `-0.005`, 45 correct, 60 wrong, 2,895 abstentions, 3.5% coverage, 42.86% answered accuracy, 57.14% false-answer rate, p95 97 ms. This is an in-sample diagnostic, not acceptance.
- P5/P6 remain partial; revenue mistakes remain the largest error group (53/60). No label-specific or business-ID-specific fixes were added. No Git/data archive/Docker/official checkout changes.
- Evidence: `tools/checkpoints/2026-11-16T0933+07-00_P5_EXECUTOR_REASON_CODES_COMPLETE.md` and the external evaluation report under `work/evaluation/p6-train-replay-v5-full-2026-11-16/`.

## 2026-11-16 — P4 order/payment and product-column safety

- Added table-role exclusions for payment/receipt and delivery evidence in sales/order metrics; added precise order ID matching, including documented `Mã GD`; removed broad `don` matching that confused `Đơn vị tính` with an order ID.
- Replaced unsafe broad product substring matching with descriptive product headers, including `Hàng bán`; ranking rejects date/code labels and inventory-ledger sources.
- Added cancellation/canceled English status support. Added eight regression tests across payment splits, order deduplication, delivery rows, false order IDs, false product columns, inventory evidence, and cancellation statuses.
- Focused pipeline tests: 21/21. Complete suite: 102 run, 99 passed, 3 Git-only skips.
- Full train replay v3 is an in-sample diagnostic and worsened versus v2: PA `-0.01267`, 40 correct, 78 wrong, 2,882 abstentions. Post-freeze comparison exposed the unit-header false positive and omitted `Hàng bán`; a targeted v4 replay then checked seven affected businesses separately. Do not claim P4 acceptance or use these train results as an independent score.
- Remaining large error area: revenue semantics/source selection in biz_127/biz_129. Investigate schema and generic operators, no answer hardcoding. No Git/source archive/official checkout mutation; Docker is out of scope.
- Evidence: `tools/checkpoints/2026-11-16T0902+07-00_P4_ORDER_PAYMENT_PRODUCT_SAFETY_START.md` and `tools/checkpoints/2026-11-16T0920+07-00_P4_ORDER_PAYMENT_PRODUCT_SAFETY_COMPLETE.md`.

## 2026-11-16 — P3 filter firewall status

- Added fail-closed unresolved entity/group/payment filter handling and noisy ranking spelling recognition, with schema and synthetic regression coverage.
- User explicitly skipped the independent-review wait. P3 remains **NOT VERIFIED / NOT PASSED**; there are no reviewer annotations or ≥81% claim.
- Evidence: `tools/checkpoints/2026-11-16T0920+07-00_P3_FILTER_FIREWALL_COMPLETE.md`.

## 2026-11-16 — P5 trace reason codes

- Added a stable abstention reason-code allowlist and a backward-compatible verifier result API.
- Runtime traces now include verification status/reason and the versioned QuerySpec; submission JSONL retains the existing record schema.
- Synthetic tests cover missing-time abstention, insufficient evidence, missing source, ingestion parse failure, trace metadata and output-schema preservation.
- Focused API/verifier tests: 20/20. Full suite: 90 run, 87 passed, 3 Git-dependent skips, exit 0.
- P5 remains partial: missing-column, invalid-unit and unsafe-join codes are not emitted yet; false-answer and full verification gates remain unmeasured. P3 remains NOT VERIFIED / NOT PASSED per user direction to skip its reviewer.
- Evidence: `tools/checkpoints/2026-11-16T0817+07-00_P5_TRACE_REASON_CODES_COMPLETE.md`.

## 2026-11-16 — P4 fail-closed executor slice

- User directed us to skip the independent-review wait for P3 and continue. P3 remains NOT VERIFIED / NOT PASSED; no reviewer results or acceptance percentage are claimed.
- `metrics.py` now abstains on multiple matching fact tables, nonblank rows with invalid dates, invalid numeric values, empty period matches, missing order IDs, and conflicting statuses for one order.
- Added five synthetic pipeline regressions. Focused tests: 11 passed. Full suite: 85 run, 82 passed, 3 Git-dependent skips, exit 0.
- This is a bounded P4 safety improvement, not full P4 acceptance. P4 still lacks broader operator contracts, safe declared joins, business-rule evidence and supported-scope replay.
- Docker is out of scope. No labels, public/private test content, official checkout, or Git history was touched; no commit or push occurred.
- Evidence: `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_COMPLETE.md`.

## 2026-11-15 — Curated source sync to GitHub

- Copied only the 38 reviewed files from the verified Source Release into the clean real checkout on `feature/offline-core`.
- The full target-checkout suite passed (80 tests); `git diff --check` passed; repository hygiene tests found no data/weight files, large files, or secret-like strings.
- Pushed commit `3b0bf3b66e9a78fa68fa29e8b97a23787bac2f0a`, parent `24cfa0908bd20f6e5b210366e956cae0d665b56e`. Post-push fetch confirmed local and origin refs match, worktree clean, and `main` unchanged.
- Excluded all competition data/result files, public submission JSONL, local reports, internal checkpoints, logs, credentials, and Docker image/archive. Docker remains unbuilt; P3 remains not passed.

## 2026-11-15 — Public Test JSONL candidate

- Generated a one-pass Public Test candidate from the isolated feature snapshot; no source application code was changed in this work item.
- Validated 1,000 unique ordered question IDs, answer record schema, and 1,000 matching trace records; runtime error records: 0.
- Candidate location, hashes, limitations, and model declaration are recorded in the external workspace artifact record and submission package validation report.
- Public questions were not used for tuning. No labels were available or read, so accuracy and Penalized Accuracy remain unmeasured.
- The separate Docker image/Test Solution deliverable remains blocked because no Docker-family runtime is installed.
- Read-only CI investigation found no local workflow files and zero GitHub Actions runs; no remote or paid builder was invoked.

## 2026-11-16 — P7 business coverage matrix

- Profiled all 30 train business directories: 30 READMEs, 128 files, 339 tables/sheets, zero profiling errors; no questions or answer labels were supplied to the profiler.
- Added `tools/build_business_coverage_matrix.py`, 3 unit tests, `docs/BUSINESS_COVERAGE.md`, and a machine-readable train-only matrix under `work/evaluation/`.
- L1 structural profile: 30/30; L2 replay without runtime errors: 30/30 (not row-census reconciled); L3 mapped intent tests: 0/30; L4 frozen train replay: 30/30; L5 release-supported: 0/30. P7 remains NOT ACCEPTED; 0% supported coverage is below 81%.
- v7 train-only replay: PA 0.33%, 2.80% question-weighted coverage, 55.95% answered accuracy; 47 correct, 37 wrong, 2,916 abstentions; p95 18 ms; no runtime errors. Diagnostic only.
- Full suite: 119 run, 116 passed, 3 Git-dependent hygiene skips, exit 0. P3 reviewer was skipped; P3 remains NOT VERIFIED / NOT PASSED.
- User defined revenue as after-discount order value by default; collected/paid amounts are a separate metric; abstain if the requested metric cannot be established.
- Evidence and exact commands: `tools/checkpoints/2026-11-16T1037+07-00_P7_BUSINESS_COVERAGE_MATRIX_COMPLETE.md`.

## 2026-11-16 — separate after-discount revenue from collected money

- Implemented the user's business rule: order value after discounts is default revenue; explicit received/paid wording maps to a distinct `collected_amount` QuerySpec/plan.
- Revenue prefers order-total/receivable columns. Collected amount requires one payment-event table with exact receipt-date and amount headers; it uses the event date and fails closed on missing/ambiguous evidence. It does not substitute order totals, debt, or paid-balance snapshots.
- Added regressions for Vietnamese/English intent cues, QuerySpec serialization, split payments, receipt-period filtering, pending status, missing/ambiguous payment sources, subtotal versus order-total priority, and multi-metric requests.
- Full suite: 127 run, 124 passed, 3 Git-only skips, exit 0. biz_127/biz_129 real-data smoke selected `don_hang` and `thanh_toan` respectively without printing answer amounts.
- Frozen v8 train replay had the same prediction hash as v7 and unchanged quality: 47 correct, 37 wrong, 2,916 abstain; PA 0.33%, coverage 2.80%, answered accuracy 55.95%, runtime errors 0, p95 35 ms. In-sample only; no score improvement is claimed.
- Checkpoint and hashes: `tools/checkpoints/2026-11-16T1103+07-00_REVENUE_COLLECTION_CONTRACT_COMPLETE.md`.


## 2026-11-19 — Composite financial query vertical slice

- Added `CompositePlanner`, requirement/component/composite-plan models, and all-or-nothing composite verification.
- Routed the recognized revenue + collected-amount question through two independent existing metric executions.
- Added synthetic tests for shared period context, unsupported cases, successful table output, and component failure abstention.
- Added ingestion and multi-bundle architecture documentation plus a GitHub Actions test workflow. CI verification pending.


### CI follow-up — 2026-11-19

- The feature-branch workflow ran 197 tests. The newly added composite tests and functional tests passed; two repository-hygiene checks failed on the pre-existing `CODEX PROGRESS` file (size limit and secret-like pattern match).
- No attempt was made to weaken the hygiene checks or remove the pre-existing file. See the checkpoint for details.


## 2026-11-20 — relationship path candidate-bound hardening

- Fixed an off-by-one condition in `resolve_relationship_path`: reaching exactly `max_candidates` is no longer treated as overflow. The resolver now observes one additional path before reporting that the configured bound was exceeded.
- Invalid limits (non-positive, boolean, or non-integer) and malformed/blank table identities now fail closed as `invalid_request` instead of raising comparison/type errors or creating weak graph nodes.
- Added six synthetic regressions: exact candidate limit, candidate-limit overflow, reverse-direction fanout, hop-limit enforcement, invalid limits, and cycle handling.
- This remains discovery-only; no JOIN execution or metric enablement was added.
- Commits: `4212165cece5a9167095984865aca98ae6362890` (resolver fix), `fe799c55ac9757a64007fbe03ef0a9028e6ff1f2` (tests).
- CI pending for this commit range. No local checkout or local test execution was used.


## Follow-up verification — 2026-11-20

- The first added edge-case run exposed two incorrect test fixtures (cardinality direction and an assertion that expected a longer path despite a direct edge). The fixtures were corrected in commit `2522abbafdccb6bb930d3f79f9f0f13af8302d4f`; no production-code change was needed for those fixture failures.
- GitHub Actions run `44580683573` on `2522abb` executed 299 tests. 297 passed, including all relationship-path tests. The only two failures are the inherited repository-hygiene checks for the pre-existing `CODEX PROGRESS` artifact.
- Run: https://github.com/pl2n/DataMate/actions/runs/44580683573
- The existing upstream PR #1 is open from `pl2n/DataMate:feature/multi-bundle-query` into `DangDuuTapCode/DataMate:main`. It was not created or modified in this work item. GitHub currently reports `mergeable=false`; this should be rechecked before any merge decision.


## Fact join contract structural prototype (2026-11-20)

- Added `src/datamate/join_contracts.py` with `FactJoinContract` and a fail-closed builder over a unique validated relationship path.
- Contract records exact source-qualified fact/target tables, declared fact grain, measure field and physical measure index, aggregation stage, join type, and exact path hops/key indices.
- Builder rejects fanout, unknown cardinality, ambiguous paths, endpoint mismatch, disconnected/repeated nodes, malformed composite key indices, invalid measure index, missing grain/measure declarations, unsupported join types, and pre-join aggregation.
- Added synthetic tests in `tests/test_join_contracts.py` and documentation in `docs/FACT_JOIN_CONTRACT.md`.
- This is a structural prototype only. It is not wired into planner/Executor and does not execute joins or enable a new metric. Grain/measure meaning still requires reviewed query-specific evidence.
- Code commits: `bad2dcda57a71d8c78d7e49a2c84b969e3008071`, `2136219d904b5ce99671e3c3d285d5b60a638aae`, `f5b476972f779b5abe02bf14f8ca438ac143c90f`, `085284c1562af575d55bf12f80715de6b331e3b3`.
- Documentation commit: `d87b325e158da97ab11f21380cb177e36d3ed680`.
- CI verification pending. No local checkout or local test execution was used.


## CI verification — fact join contract prototype

- Latest checked Actions run: `44581612778`, head `77460ea68fcb1750b8a534e87727cb7e99d8e52f`.
- 310 tests executed; 308 passed. All relationship-path and fact-join-contract feature tests passed.
- The only two failures remain `test_no_large_files` and `test_no_secret_like_strings`, both reporting the pre-existing `CODEX PROGRESS` artifact.
- Run: https://github.com/pl2n/DataMate/actions/runs/44581612778
- Existing PR #1 remains open against upstream `main`, head updated with this branch. GitHub reports `mergeable=false`; no merge or PR mutation was performed.


## 2026-11-20 — PR merge and FactJoinContract hardening

- Confirmed upstream PR #1 merged at `99478a179919a7b5121b00072f90522c50117aba`; upstream `main` is identical to the merge commit.
- Created fork continuation branch `feature/query-specific-join-execution` from merged PR head `15430b417d650e6145ed4e64cb637ebe2a00677c`.
- Hardened `build_fact_join_contract` against forged candidate counts and malformed path-hop structures; added four focused regression cases.
- Commits: `5c04d9b8498133e28170108ed3ba7fe8ec58301a`, `783631e99ed584fee284564c126b1275ca453edf`.
- No runtime JOIN behavior was enabled. CI verification is pending for this continuation branch.


### Follow-up

- Hardened malformed cardinality handling and added a list-valued cardinality regression.
- Commits: `101a5089d1bd71c45b17516f5753a2e01f06f151`, `4e073e4f1a35a216179094ff0d63389f27829775`.


### CI trigger coverage

- Expanded the Python test workflow to cover all `feature/**` push branches and PRs targeting `main` or `feature/**`.
- Commit: `e74d43413c3966d7d80e6fbe8f985fb5b6ac4de9`.
- Workflow result not yet verified.

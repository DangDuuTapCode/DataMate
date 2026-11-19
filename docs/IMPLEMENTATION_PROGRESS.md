# CURRENT SUMMARY — 2026-11-16

## P6 — daily revenue threshold day-count fix (started 17:08 GMT+7)

- v16 train-only diagnostic exposed a generic error: a question asking how many days reached at least a stated revenue threshold was routed to purchase quantity and answered `4291` instead of train reference `8`.
- Started a bounded change to detect only explicit day-count + revenue + threshold requests, sum eligible line revenue by distinct date, and count dates meeting the threshold. Strict normalization and abstention are required for ambiguous thresholds/evidence.
- Start checkpoint: `tools/checkpoints/2026-11-16T1708+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_START.md`. No code change or new replay yet; v16 remains preserved. No public/private labels.
- Completed: added an allowlisted threshold-count intent; preserved currency grouping for strict parsing; propagated the numeric threshold to the plan; summed eligible after-discount line revenue by date; added verifier type and ambiguity/evidence gates. Regression confirms distinct-day aggregation, inclusive threshold equality, unsuccessful status exclusions, and abstention on unclear amounts or multiple sources.
- A focused test also exposed a pre-existing undefined payment status alias and pending-payment handling issue; these were fixed in the same unit. Fallback synthetic rules exclude known unsuccessful and in-transit rows; unknown/pending status remains fail-closed, and explicit split-rulebook inclusion still applies.
- Focused test result: 71 passed. Full suite: 160 run, 157 passed, 3 Git-dependent skips, exit 0. Details: `tools/checkpoints/2026-11-16T1717+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_COMPLETE.md`.
- Next: fresh v17 train replay and freeze validation before train-only evaluation. v16 stays immutable; no public/private labels.
- v17 generation started against the unchanged metadata-complete train input. Use only the new output directory and validate its freeze before scoring. Start record: `tools/checkpoints/2026-11-16T1718+07-00_P6_V17_TRAIN_REPLAY_START.md`.
- v17 completed and `validate_frozen_replay` passed for 3,000 prediction/trace rows. Both metadata files are in the hash manifest; source/input/output checksums, ID/order/schema checks passed; generator confirms no answer labels opened. See `tools/checkpoints/2026-11-16T1728+07-00_P6_V17_TRAIN_FREEZE_VALIDATED.md`. Next evaluator uses only official train labels and repeats validation.
- v17 score after freeze revalidation: 26 correct, 3 wrong, 2,971 abstain; 0.9667% coverage, 89.66% answered accuracy, 0.7667% penalized accuracy; 70/70 unanswerable abstentions correct; 0 runtime errors, p95 22 ms. It is in-sample only. The new intent parsed the biz_124 case but abstained because no direct table had line amount + date/status.
- Structural-only source review found README-supported line-to-invoice keys; invoice IDs are unique/nonblank and every line key matches. Checkpoint: `tools/checkpoints/2026-11-16T1736+07-00_P6_DAILY_REVENUE_SAFE_JOIN_START.md`. Next: add strict unique/complete join plus synthetic tests, then a new frozen replay.
- Safe join is implemented with unique invoice IDs, complete match coverage, exact duplicate-line collapse, rulebook date/status filtering and separate evidence for both tables. Synthetic join tests passed. Real biz_124 smoke found 31,997 numeric Excel date serials; executor was discarding the workbook `date_system` that ingestion already records, so it abstained. Fix start: `tools/checkpoints/2026-11-16T1742+07-00_P6_EXCEL_DATE_SYSTEM_PROPAGATION_START.md`.

## P1 — targeted competition-rule review (14:46 GMT+7)

- Technical direction aligns in concept with DataMate's structured Vietnamese Q&A task, but full entry compliance is not verified. Read the supplied regulations, official Vietnamese PDF, official DataMate portal page, and read-only package metadata.
- Key unresolved blockers: outside scenario-test provenance/track permission; whether any contest dataset may be packaged; no-model system does not match the portal's API/LLM/SLM choices; full dependency/base-image licensing evidence; code-sharing restriction during the competition. The supplied §4.5 contains additional evidence wording absent from the linked PDF; follow the stricter version pending clarification.
- The working copy currently has no archive in `training_code/`, but adding the README-proposed `train.zip` would be copied into Docker by the current Dockerfile. Keep contest data out of the image unless official DataMate guidance explicitly requires and permits it.
- Evidence/next actions: `tools/checkpoints/2026-11-16T1446+07-00_P1_TARGETED_COMPETITION_RULE_REVIEW.md`. No source/data files changed; no public/private test labels accessed.

## P6 — current-code train replay (in progress, 14:15 GMT+7)

- Started a versioned replay after the split-rulebook and lunar-calendar changes. Input root was verified to contain `questions.jsonl` and `data/` with no `answers.jsonl`; predictions will be generated and hash-frozen before the evaluator reads train labels.
- v13 generated 3,000 predictions/traces with labels excluded, but freeze validation failed before scoring: `understanding.py` had a different hash after generation. The output is preserved unevaluated; no labels were opened. The cause of that post-freeze file change is unresolved, so do not overwrite the file.
- Focused tests found the concrete runtime break: `main.run` passes `split_rules`, but the current `RulePlanner` constructor no longer accepts it. 39 understanding/time tests passed; the mounted Tết runner failed with `TypeError`. A minimal, checkpointed wiring correction is in progress.
- Restored the previously checkpointed rulebook/calendar forwarding in `understanding.py`; focused timeparse/understanding/Tết-runner tests now pass 40/40. v13 remains unevaluated. Next is a v14 freeze with validation before scoring.
- The prior v9 report is in-sample and predates recent changes. Current replay remains diagnostic only and cannot establish independent acceptance.
- Start checkpoint: `tools/checkpoints/2026-11-16T1415+07-00_P6_CURRENT_RULEBOOK_CALENDAR_REPLAY_START.md`.
- Failure checkpoint: `tools/checkpoints/2026-11-16T1433+07-00_P6_REPLAY_FREEZE_MISMATCH.md`.
- Fix start checkpoint: `tools/checkpoints/2026-11-16T1434+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_START.md`.
- Fix completion checkpoint: `tools/checkpoints/2026-11-16T1435+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_COMPLETE.md`.
- v14 generated for 3,000 train questions with `answer_labels_accessed=false`; all frozen source/input/prediction/trace hashes and JSONL order/schema validated before any label access. Checkpoint: `tools/checkpoints/2026-11-16T1448+07-00_P6_V14_FREEZE_VALIDATED.md`. Next: evaluator may read train answers only after it repeats validation; diagnostic score only.
- The v14 evaluation is preserved but not a quality result: all 3,000 rows abstained on `rulebook_unavailable` because its replay root omitted `rulebook.md` and `calendar.csv`. No code changed. The train archive contains both metadata members; only the train answer member was used for scoring. Corrected input/replay must use a new path. Details: `tools/checkpoints/2026-11-16T1450+07-00_P6_V14_INCOMPLETE_INPUT_FINDING.md`.
- Corrected train input now contains the preserved question/data files plus only `rulebook.md` and `calendar.csv`. v15 replay is active on a new path; wait for it to finish, verify `answer_labels_accessed=false` and all checksums, then score train only. Checkpoint: `tools/checkpoints/2026-11-16T1626+07-00_P6_COMPLETE_TRAIN_INPUT_V15_START.md`.
- v15 completed with no runtime errors, but must not be evaluated: `build_input_manifest` omitted split metadata, and v15's input hash is identical to v13's despite the added rulebook/calendar. No labels were opened. Fix this integrity gap and add focused tests before a fresh replay. Checkpoint: `tools/checkpoints/2026-11-16T1629+07-00_P6_REPLAY_METADATA_HASH_FIX_START.md`.
- Fixed replay freeze integrity: input roots must include `rulebook.md` and `calendar.csv`, both included in the manifest. Added mutation regressions; `PYTHONPATH=src python -m unittest tests.test_replay_eval -v` passed 3/3. Initial failure was caused by the old fake sales fixture missing product identity; fixture was corrected. Next generate and validate v16 in a new directory before train-only scoring. Evidence: `tools/checkpoints/2026-11-16T1633+07-00_P6_REPLAY_METADATA_HASH_FIX_COMPLETE.md`.
- v16 replay is active in session `50250` at a fresh output path. Wait for completion; require metadata inclusion and complete freeze validation before evaluating train labels. Start checkpoint: `tools/checkpoints/2026-11-16T1635+07-00_P6_V16_METADATA_HASHED_REPLAY_START.md`.
- v16 completed; metadata manifest and all source/input/prediction/trace, count/order, and schema checks passed for 3,000 rows. No labels accessed. Exact hashes and validation command evidence: `tools/checkpoints/2026-11-16T1642+07-00_P6_V16_METADATA_HASHED_FREEZE_VALIDATED.md`. Next: evaluator may read train answers only; it revalidates the freeze.
- Train-only diagnostic completed after evaluator revalidated the freeze: 26 correct, 4 wrong, 2,970 abstain; 1.00% coverage, 86.67% answered accuracy, 13.33% false-answer rate, 0.733% penalized accuracy; p95 18 ms, zero runtime errors. This is in-sample, not acceptance; 70/70 unanswerable train cases abstained correctly. Wrong intents and reason counts are recorded in `tools/checkpoints/2026-11-16T1645+07-00_P6_V16_TRAIN_DIAGNOSTIC_EVALUATED.md`. Next analyze train errors/abstentions and fix generic high-impact gaps.

## P4 — split calendar and rulebook-driven Tết periods (completed, 14:08 GMT+7)

- Connected split `rulebook.md` Tết window and comparison permission with the mounted `calendar.csv`. Fixed parsing of the official mathematical minus sign in `Y − 1`; preserved Gregorian behavior and explicit-month/entity precedence.
- Focused checks: 19 time parser tests and 1 runner test passed. Read-only smoke parsed only calendar/rulebook metadata from train and public archives; both resolved Tết 2026 to 2026-02-10–2026-02-26.
- Compliance read of the supplied general regulation: no blanket answer for whether DataMate permits the separate outside scenario file. Its provenance/rights and track-specific permission remain unverified; it must stay out of training and the submission package pending evidence. This is not whole-entry compliance certification.
- Targeted manifest check: no model is declared; the user-provided portal screenshot lists API/LLM/SLM categories, so the valid submission category for a deterministic rule engine needs track-specific confirmation. `openpyxl==3.1.5` and a vLLM base image are present, but no complete third-party license/provenance inventory was found; section 4.5 is not yet evidenced.
- Checkpoint: `tools/checkpoints/2026-11-16T1408+07-00_P4_SPLIT_CALENDAR_TET_SUPPORT_COMPLETE.md`.

## P5 — typed verifier gate (bounded slice completed, 14:12 GMT+7)

- Verified the existing intent/output-type, confidence, evidence, and ranking-cardinality checks. Added cases for empty and overlong top-k lists; shorter nonempty results remain valid when fewer candidates are available.
- Focused verifier tests: 5 passed. No full suite was run. P5 overall remains partial/not accepted.
- Checkpoint: `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`.

## P4 — Tết support start checkpoint (superseded by 14:08 completion)

- Start record: `tools/checkpoints/2026-11-16T1354+07-00_P4_SOLAR_LUNAR_TIME_SUPPORT_START.md`.
- Implementation and verification are recorded in `tools/checkpoints/2026-11-16T1408+07-00_P4_SPLIT_CALENDAR_TET_SUPPORT_COMPLETE.md`.

## P4/P5 — competition-rule conformance correction, completed 2026-11-16 13:44 GMT+7

- Corrected a contest-critical mismatch using the official rules text supplied by the user: runtime now loads the active split's `rulebook.md`; revenue selects identified line-level after-discount amounts and the rulebook date/status defaults, never order totals or receipts; cancellation rate follows the rulebook numerator; rankings use the explicit metric/default, code tie-break, and allow fewer than k available candidates.
- The earlier D10 revenue/status convention is explicitly superseded for contest inference. A missing/unsupported rulebook or an order state the executor cannot interpret fails closed as abstain.
- Focused tests for rule parsing, line-vs-order revenue, status handling, cancellation-rate semantics, ranking ties/top-k, type verification, runtime rulebook loading, and empty-period reason: 16 passed. Actual `train/rulebook.md` parse smoke: supported; default revenue date/status, ranking criterion, tie-break, and cancellation numerator extracted. Full suite was not run, per the user's time constraint.
- Checkpoint: `tools/checkpoints/2026-11-16T1344+07-00_P4_COMPETITION_RULEBOOK_CONFORMANCE_COMPLETE.md`.

## P5 typed verifier gate start checkpoint (superseded by 14:12 completion)

- Start record: `tools/checkpoints/2026-11-16T1330+07-00_P5_TYPED_ANSWER_VERIFICATION_START.md`.
- Completion and focused evidence: `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`.

## P4 — VND and million-suffix amount normalization, completed 2026-11-16 13:25 GMT+7

- Fixed parsing for explicit VND grouped amounts (`10.000đ`) and Vietnamese million forms (`1tr`, `1tr040`, `1,04tr`). Three-digit tails remain ambiguous unless column evidence or an explicit policy resolves them; a bare `10.000` remains ambiguous.
- Source-only audit parsed 131,192/131,192 after-discount `Amount` values for biz_127 and 145,479/145,479 `Tiền bán` values for biz_129. README-key reconciliation was exact for only 9,605/33,874 and 11,587/38,499 orders respectively, so no detail/order join or source change was introduced.
- Focused normalization+ingestion tests: 25 passed. Full suite: 142 run, 139 passed, 3 Git-only skips. v12 was frozen/validated before labels; prediction hash and in-sample score match v11. Full evidence: `tools/checkpoints/2026-11-16T1325+07-00_P4_VND_MILLION_NORMALIZATION_COMPLETE.md`.

## P4/P5 — no-data reason coverage across intents, completed 2026-11-16 13:00 GMT+7

- Added empty-period reason tests for collected amount, order count, unsuccessful-order rate, and ranking; malformed dates remain `insufficient_evidence`; a zero payment row answers numeric 0. Added regression that excludes canceled, returned-after-delivery, and failed-delivery order totals from revenue, per the user's confirmation.
- Recorded the rule in `docs/decisions.md` and `docs/BUSINESS_COVERAGE.md`. Runtime source code did not change.
- Focused suite: 40 passed. Full suite: 140 run, 137 passed, 3 Git-only skips, exit 0. Completion checkpoint: `tools/checkpoints/2026-11-16T1300+07-00_P4_NO_DATA_REASON_INTENT_COVERAGE_COMPLETE.md`.

## P4/P5 — no-data versus zero, completed 2026-11-16 12:48 GMT+7

- Added an internal `no_data` reason for an empty requested period in a unique supported source. Matching rows with a valid zero aggregate still answer numeric `0`; the external submission record is unchanged. See `docs/VERIFIER_REASON_CODES.md`.
- Focused tests: 48 passed. Full suite: 136 run, 133 passed, 3 Git-only skips, exit 0.
- v11 full train replay was freeze-validated (3,000 predictions/traces) before evaluator label access. Predictions are byte-identical to v10. Score stayed at 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 37 ms, no runtime errors. `no_data` appeared in 0 traces, so its occurrence path is covered synthetically only.
- Revenue remains the largest observed error group (30/44) in an in-sample train diagnostic. See checkpoint `tools/checkpoints/2026-11-16T1248+07-00_P4_NO_DATA_ZERO_SEMANTICS_COMPLETE.md`; this is not phase acceptance evidence.

## P5 structured order-status trace reasons — 2026-11-16 12:32 GMT+7

- Added separate trace codes for missing, unrecognized, and conflicting order-status evidence. These codes are internal; organizer-facing abstain JSONL schema is unchanged.
- Focused pipeline/API tests: 47 passed. Full suite: 135 run, 132 passed, 3 Git-only skips, exit 0.
- v10 freeze validation passed for 3,000 predictions and traces before evaluator-only train label access. Prediction SHA is byte-identical to v9; train score is unchanged: 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 18 ms, 0 runtime errors. The three new statuses were exercised synthetically but did not occur in v10 train traces.
- P5 remains partial and not accepted; broader source, denominator, reconciliation, and false-answer controls remain incomplete. P3 reviewer stays skipped and P3 remains **NOT VERIFIED / NOT PASSED**. Checkpoint: `tools/checkpoints/2026-11-16T1232+07-00_P5_ORDER_STATUS_TRACE_REASON_COMPLETE.md`.

## Shared unsuccessful-order status convention — 2026-11-16 11:54 GMT+7

- Implemented the user-approved global outcome model: cancellation, post-delivery return, and failed delivery are separate classes that all contribute to the unsuccessful-order rate. Pending and in-transit remain distinct; unknown/missing status or conflicting order states produce abstention. Raw source statuses are not rewritten.
- Status headers now use exact documented aliases, including `Kết quả` and `Ghi chú TT`; customer and e-invoice status fields do not qualify. `Đổi trả` maps to returned and `Không giao được` to delivery failed.
- Five new pipeline regressions; focused suite 35/35 passed. Read-only train data smoke classified every observed status in biz_101 (4 variants) and biz_116 (7 variants); full-period diagnostic rates 4.60% and 2.47%, respectively. No answer labels were accessed for these checks.
- Full suite passed: 132 run, 129 passed, 3 Git-dependent skips. Frozen v9 (3,000 train questions) was checksum-validated before evaluation: 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 42 ms, no runtime errors. Cancellation-rate has 2 correct and 12 wrong among 14 answers, compared with v8's 12/2. The train reference mismatch is recorded; no label tuning was done and the user-approved business rule remains in force.
- P3 reviewer stays skipped and P3 remains **NOT VERIFIED / NOT PASSED**. v9 is in-sample and no phase meets its acceptance claim from this result. Evidence and hashes: `tools/checkpoints/2026-11-16T1154+07-00_UNSUCCESSFUL_ORDER_STATUS_RULE_COMPLETE.md`.
- Refreshed the P7 matrix with v9 in `docs/BUSINESS_COVERAGE_V9.md` and `work/evaluation/business-coverage-matrix-train-v2-2026-11-16.json`. Fixed stale v7/0-of-30 hardcoding. Focused tests: 4 passed; full suite: 133 run, 130 passed, 3 Git-dependent skips; exit 0. L1/L2/L4 30/30, L3/L5 0/30. Details: `tools/checkpoints/2026-11-16T1156+07-00_P7_MATRIX_REFRESH_COMPLETE.md`.

## Revenue versus collected-money contract — 2026-11-16 11:03 GMT+7

- User-defined revenue contract implemented: order value after discounts is default revenue; explicit collected/paid questions use a distinct `collected_amount` intent. Collection uses one unambiguous payment-event table by receipt/payment date and transaction amount; missing evidence abstains.
- The executor prefers documented order-total/receivable headers over subtotals and continues to exclude payment tables from revenue. It does not treat debt or an order's paid-balance snapshot as money collected during a period.
- Added parser, QuerySpec serialization, execution, multi-metric fail-closed and real-data regressions. Full suite: 127 run, 124 passed, 3 Git-only skips; exit 0. biz_127/biz_129 data smoke selected the expected order and payment tables.
- Frozen v8 train replay: prediction hash unchanged from v7; 47 correct, 37 wrong, 2,916 abstentions; PA 0.33%, coverage 2.80%, answered accuracy 55.95%; no runtime errors, p95 35 ms. This change adds semantic handling but did not change train predictions.
- v8 is an in-sample diagnostic below acceptance. P3 reviewer remains skipped and P3 NOT VERIFIED / NOT PASSED. Full provenance: `tools/checkpoints/2026-11-16T1103+07-00_REVENUE_COLLECTION_CONTRACT_COMPLETE.md`.

## P7 — train-only business structural coverage, 2026-11-16 10:37 GMT+7

- Completed the L1 structural profile and generated a 30-business coverage matrix using the frozen v7 train replay. 30/30 profiles have READMEs; 128 files and 339 tables/sheets were inventoried; no profile errors or question inputs.
- Evidence levels: L1 30/30; L2 replay exercised without runtime errors 30/30 (no complete row census); L3 declared business-intent tests 0/30; L4 replay metrics 30/30; L5 release-supported 0/30. P7 remains **IN PROGRESS / NOT ACCEPTED** because 0% L5 is below the 81% target.
- v7 train replay: PA 0.33%, answer coverage 2.80%, answered accuracy 55.95%; 47 correct, 37 wrong, 2,916 abstain; p95 18 ms; no runtime errors. Macro PA 1.05%, macro coverage 3.58%, macro answered accuracy 55.30% across 8 businesses with answers. In-sample diagnostic only.
- Added `tools/build_business_coverage_matrix.py` and 3 tests; all 119 tests passed except 3 Git-dependent repository-hygiene skips (116 passed, exit 0). Matrix: `docs/BUSINESS_COVERAGE.md`; machine-readable form: `work/evaluation/business-coverage-matrix-train-v1-2026-11-16.json`.
- Profile contains README and structural metadata only; derived matrix omits README prose, question text, answer labels, and row/cell values. Candidate join/header categories are hints only.
- Revenue definition clarified by user: order value after discounts is default revenue; collected/paid cash is a separate metric; abstain when the requested measure cannot be established.
- P3 reviewer remains skipped; P3 stays **NOT VERIFIED / NOT PASSED**. Checkpoint: `tools/checkpoints/2026-11-16T1037+07-00_P7_BUSINESS_COVERAGE_MATRIX_COMPLETE.md`.

## Latest slice — P4 status firewall and v7 evaluation, 2026-11-16 10:18 GMT+7

- User explicitly skipped the P3 reviewer. P3 remains **NOT VERIFIED / NOT PASSED**; no review evidence or ≥81% result is claimed.
- Generic QuerySpec recognizes product filters/groupings, payment/channel breakdowns, natural-language revenue shares, best-sales-day typos/English `revenue`, and average-revenue intent. Follow-up catches product names after `món`, `tiền bán`, or `bán`; also catches `tại quầy`. Scalar revenue with a percent unit abstains internally as `invalid_unit`; external JSONL is unchanged.
- Added a source-grounded fail-closed status rule: failed delivery, returns/cancellations, pending, and in-transit orders no longer contribute to revenue/quantity/ranking. Focused pipeline: 26 passed. Latest full suite: 116 run, 113 passed, 3 Git-only skips, exit 0.
- P3 understanding/pipeline/schema focused suite before this P4-only status update: 48/48 passed; those regressions are included in the latest full-suite run.
- Frozen v7 current-code train replay: 3,000/30, PA `0.00333`; 47 correct, 37 wrong, 2,916 abstain; coverage 2.80%, answered accuracy 55.95%, false-answer rate 44.05%, p95 18 ms, no runtime errors. Versus v6b, 4 more correct and 9 fewer wrong; versus v5, 23 fewer wrong. In-sample only and still far below acceptance.
- At 10:18, source schemas showed distinct gross/receivable and paid/balance columns, while revenue semantics were unresolved. The user later defined the metric and the bounded implementation is recorded at `tools/checkpoints/2026-11-16T1103+07-00_REVENUE_COLLECTION_CONTRACT_COMPLETE.md`.
- Reviewer skip is honored; P3 remains **NOT VERIFIED / NOT PASSED** and P4/P5/P6 remain partial. No public-test tuning, commit, push, official checkout/source archive mutation, or Docker work.
- Full metrics/provenance and next actions: `tools/checkpoints/2026-11-16T1004+07-00_P3_P6_REVENUE_ANALYSIS_COMPLETE.md`, `tools/checkpoints/2026-11-16T1010+07-00_P4_NONFINAL_STATUS_FIREWALL_COMPLETE.md`, and `tools/checkpoints/2026-11-16T1018+07-00_P6_CURRENT_CODE_REPLAY_COMPLETE.md`.

## P4/P5 reliability slices — 2026-11-16

P3 independent review was skipped at the user's direction. P3 remains **NOT VERIFIED / NOT PASSED**. P1/P2 retain prior verified status; those checks were not repeated. Docker work is out of scope.

P4 received a synthetic fail-closed executor change: ambiguous tables, invalid dates/numbers, no matching rows, missing order IDs and conflicting statuses now abstain. P5 adds internal trace status/reason codes and a validated QuerySpec snapshot while preserving the external submission JSONL record. Focused P5 API/verifier tests: 20/20. Complete suite after both slices: 90 run, 87 passed, 3 Git-dependent hygiene skips, exit 0.

These are partial reliability improvements, not P4/P5 acceptance. P4 still lacks complete operator/join contracts, sourced business rules and supported-scope replay. P5 still lacks source/denominator/reconciliation gates, false-answer measurement and structured `missing_column`, `invalid_unit`, and `join_unsafe` production. No ≥81%/≥85% claim is made. Details: `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_COMPLETE.md` and `tools/checkpoints/2026-11-16T0817+07-00_P5_TRACE_REASON_CODES_COMPLETE.md`.

## P4 executor hardening — 2026-11-16

The user directed us to skip the independent-review wait for P3 and continue implementation. P3 remains **NOT VERIFIED / NOT PASSED**; no independent review or acceptance percentage is claimed. Previously verified P1/P2 evidence is retained without rerunning those checks.

P4 is **IN PROGRESS**, not accepted. The allowlisted executor change now fails closed when more than one table matches, when a nonblank row has an unparseable date, when a selected-period amount/quantity is invalid, when no rows match the period, when an order ID is missing, or when one order has conflicting statuses. Five synthetic regressions cover these conditions. Focused pipeline tests: 11 passed. Full suite: 85 run, 82 passed, 3 Git-dependent hygiene skips, exit 0. This narrow slice does not establish the complete P4 operator/business-rule rubric or an accuracy threshold.

Docker work is out of scope by user direction. P5–P8 remain open and have not been re-audited. No source data, answer labels, Public Test content, official checkout, or Git history was changed. No commit/push occurred. The working source remains the isolated no-Git snapshot. Evidence: `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_COMPLETE.md`.

## GitHub synchronization — 2026-11-15

Synced 38 reviewed source-release files to `origin/feature/offline-core` in commit `3b0bf3b66e9a78fa68fa29e8b97a23787bac2f0a` (parent `24cfa0908bd20f6e5b210366e956cae0d665b56e`). Target checkout suite passed 80 tests; `git diff --check` passed. Post-push fetch verified remote and local HEAD match and the working tree is clean. No data archive, question/answer JSONL, logs, secrets, internal checkpoints, public output, or Docker image was pushed. `main` is unchanged. P3 remains NOT PASSED; P4–P8 remain incomplete.

## Emergency Docker build checkpoint — 2026-11-15

The Source Release and prepared Docker context were inspected against the 10-page official guide. The build context is verified, but **no Docker image was built**. The connected GitHub tools could not inspect/provision Codespaces or dispatch a build; browser access was disabled; the repository was public and no protected/private upload destination was confirmed. At that investigation checkpoint the checkout was at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; it was later advanced by the reviewed release sync commit recorded above. The Source Release ZIP and frozen Public JSONL hashes still match the release report. No local Docker retry, public inference rerun, or portal submission occurred. See `work/docker-build-investigation-2026-11-15/DOCKER_BUILD_INVESTIGATION.md` for the Docker blocker. P3 remains NOT PASSED; P4–P8 remain incomplete.

Public Test JSONL candidate prepared and format/runtime verified; not uploaded. Candidate: work/submission-build/public-test-submission-2026-11-15/submission.jsonl, 1,000 records; 71.8% abstentions; accuracy/PA not measured. Docker/Test Solution remains blocked without a Docker runtime. P3 is NOT PASSED; P4–P8 remain. See the latest checkpoint tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_COMPLETE.md. This summary supersedes older status headings below where dates/status conflict; historical records are retained.

# Implementation progress

## Current continuation — 2026-11-16

- The user directed us to skip the P3 independent reviewer and continue. P3 remains **NOT VERIFIED / NOT PASSED**; no review annotations or ≥81% acceptance result are claimed.
- P4 now contains regression-backed safety for order totals versus payment transactions, order IDs versus generic unit headers, sales orders versus delivery records, product names versus dates/codes, and English cancellation states. The complete suite passed: 102 run, 99 passed, 3 Git-only repository-hygiene skips.
- P5 now reports `missing_column`, `invalid_unit`, and `join_unsafe` from the execution trace while preserving submission JSONL. The full suite passed: 108 run, 105 passed, 3 Git-only skips.
- The latest frozen full-train v5 diagnostic covers 3,000 questions/30 businesses and scored PA `-0.005` (45 correct, 60 wrong, 2,895 abstentions), coverage `3.5%`, answered accuracy `42.86%`, false-answer rate `57.14%`. It improved versus v3 but remains in-sample and far below acceptance. Revenue errors are 53/60 wrong answers, concentrated in biz_127 and biz_129. Full report: `work/evaluation/p6-train-replay-v5-full-2026-11-16/evaluation_report.json`.
- The earlier targeted v4 replay covered 7 businesses/592 questions after generic header corrections; it is diagnostic only and individual reports remain under external `work/evaluation/`.
- Remaining high-impact issue: revenue inference remains wrong for many biz_127/biz_129 train questions; support for joins, filter handling, and precise revenue semantics is incomplete. Keep those outputs diagnostic only and do not encode labels/business-specific values.
- P4/P5/P6 are partial. Docker is out of scope. P1/P2 were already verified and were not rerun. No official checkout, GitHub, `main`, or source archive was changed.
- Evidence: `tools/checkpoints/2026-11-16T0920+07-00_P3_FILTER_FIREWALL_COMPLETE.md`, `tools/checkpoints/2026-11-16T0920+07-00_P4_ORDER_PAYMENT_PRODUCT_SAFETY_COMPLETE.md`, and `tools/checkpoints/2026-11-16T0933+07-00_P5_EXECUTOR_REASON_CODES_COMPLETE.md`.

Updated: 2026-11-14 (GMT+7)

## Repository state at this checkpoint

- Branch: `feature/offline-core`
- Starting commit: `01d86f0168a7572d60896aae5125106934a99322`
- Starting working tree: clean and aligned with `origin/feature/offline-core`
- Local checkout: created from the remote branch for this session. The separate local repository under `Documents` was on `main` and was not changed.

## DF-1 - scalar normalization and ingestion provenance

Status: stopped early at the user's request to save and push the current work. The implementation is intentionally partial and must not be described as the full Stage 2 Data Foundation.

### Completed work

- Added `datamate.normalization` with explicit `ParseResult` and `ParseStatus` values: `ok`, `empty`, `invalid`, and `ambiguous`.
- Added strict decimal handling for common decimal/grouping forms. A value such as `1.234` remains ambiguous unless a caller supplies a separator policy; no punctuation is removed blindly.
- Added strict date handling for Python dates, ISO dates, Vietnamese `ngày tháng năm` forms, configurable numeric day/month policy, and explicit Excel 1900/1904 serial-date conversion. Excel serial 60 is rejected because it represents Excel's fictitious 1900-02-29.
- Added `SourceLocation` and additive row provenance to `Table`. Existing positional construction of `Table(name, headers, rows, source)` remains valid.
- Changed CSV reading to consume the header and records incrementally instead of first creating a duplicate full-file list. Ragged or malformed CSV input now raises `IngestionError`.
- Added row provenance to XLSX and SQLite table rows. XLSX exposes the workbook date system and rejects incomplete/multi-row/merged headers instead of silently inventing a merged schema.
- Updated executor helper parsing to use the new normalizers. The date helper applies an explicit day-first Vietnamese policy.

### Files modified or created

- `src/datamate/types.py`
- `src/datamate/normalization.py`
- `src/datamate/ingest.py`
- `src/datamate/metrics.py`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `tools/STATE.md`

### Verification completed

- `PYTHONPATH=src python -m unittest discover -s tests -v` - 17 passed.
- A direct normalization smoke test passed for `12.5`, `1,5`, `1.234,56`, `1,234.56`, negative VND, ambiguous decimal/date inputs, and Excel serial dates 60 and 61.
- `git diff --check` passed before the stop request.

### Not completed

- New persistent parser integration tests were not added before the user requested a stop and push.
- `read_business()` and `Table.rows` still materialize rows because the executor depends on list semantics. A streaming descriptor/iterator migration needs a separate compatibility checkpoint.
- There is no source-specific header configuration yet. Ambiguous XLSX headers fail closed.
- The executor does not yet surface parse-result details to the verifier; it continues to use `None` for unsupported scalar values.
- README test command, Rulebook/README loading, Data Discovery, and Docker runtime changes are out of scope for DF-1.

## Exact next task

Create `tests/test_normalization.py` and `tests/test_ingest.py` using only synthetic temporary data. Cover CSV normal/empty/malformed/large inputs, multi-sheet XLSX, explicit ambiguous-header failure, SQLite read-only ingestion, numeric/date parser status and raw/source preservation, and compatibility with the executor. Then reassess a backward-compatible streaming table descriptor for DF-2.

## Resume commands

```powershell
Set-Location <repository-root>
git status --short --branch
git log -1 --oneline
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests -v
git diff --check
```

## P0 — repository audit and recovery checkpoint (2026-11-15)

This section supersedes the earlier resume metadata above for the active implementation run. The earlier `01d86f0` entry describes an older checkpoint and is not the base of this working copy.

- Verified repository: `C:\Users\Admin\Documents\PROJECT ZALO\datamate`; remote: `https://github.com/DangDuuTapCode/DataMate.git`.
- At the successful read-only audit: branch `feature/offline-core`, HEAD `24cfa0908bd20f6e5b210366e956cae0d665b56e`, clean, tracking `origin/feature/offline-core`. Cached feature refs match; `main`/`origin/main` are `6be6997015a1d394ab8ed0eadd0141407ea1a1da`; feature is 3 commits ahead, 0 behind. A live fetch has not been confirmed in this process.
- Official checkout suite passed 17/17 at P0. Snapshot suite ran 17: 14 passed and 3 Git-dependent hygiene tests skipped because this copy intentionally has no `.git`.
- New isolated working copy: `work/feature-offline-core-24cfa`, copied from this exact branch snapshot without `.git`; 39 files / 116,869 bytes and all paths/SHA-256 hashes match. The official checkout, older working copy, archives, and `sources/` remain untouched.
- Prior external working copy is based on `01d86f0`, so it is reference only; do not overlay wholesale or use its metrics as current-branch evidence.
- Archive inventory only: `train.zip` has 194 members (162 files), 3,000 questions / 30 businesses; answer file exists but no answer rows were read. `public_test.zip` has 113 members (97 files), 1,000 questions / 14 businesses, no answer file. No public tuning. Archives were not extracted.
- P1–P9 remain **NOT MEASURED**; no ≥81% claim.
- Current process is `ADMIN-PC\CodexSandboxOffline`; official checkout owner is `ADMIN-PC\Admin`. Git now blocks with `fatal: detected dubious ownership`; no safe-directory exception, ACL change, or elevation was attempted. Live remote state remains unverified.

### Commands and evidence

- `Get-ChildItem -Force | Select-Object Mode,Name,FullName` — workspace inventory.
- `rg --files` — official checkout file inventory.
- `Get-Content` on README, docs, source, tests, tools, packaging — source and documentation inspection.
- PowerShell snapshot and `Get-FileHash -Algorithm SHA256` comparison — 39/39 match.
- `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v` — snapshot: 17 run, 14 pass, 3 Git-dependent skips; exit 0.
- Earlier official checkout baseline: 17 passed, 0 failed.
- `whoami` — `admin-pc\codexsandboxoffline`.
- `git -C 'C:\Users\Admin\Documents\PROJECT ZALO\datamate' rev-parse --show-toplevel` — blocked by Git ownership guard.

### Files changed and next

Changed only in the isolated copy: this progress doc, `docs/NEXT_SESSION_HANDOFF.md`, `tools/STATE.md`, and `tools/checkpoints/2026-11-15_P0_REPOSITORY_AUDIT.md`. No source or test files have changed. Next: synthetic parser and ingestion regression tests, evidence-based fixes, focused and full tests; checkpoint each bounded work unit. See the P0 checkpoint for detailed scope and known risks.

## P1 — normalization and ingestion (2026-11-15)

- Added strict normalization and ingestion regression coverage, safe XLSX report-preamble detection, shared header validation, OOXML relationship handling, conservative decimal-policy inference, out-of-range Excel serial handling, and XML row-node cleanup.
- Focused tests: 20/20 pass. Full suite: 37 run, 34 passed, 3 Git-dependent hygiene checks skipped because the working snapshot has no `.git`.
- Train-only structural loader census: 30/30 businesses (100%), 128 structured source files, 339 tables/sheets, 3,997,042 rows, zero load failures. Four businesses with legacy ZIP filename metadata were separately re-extracted using UTF-8 metadata and revalidated 4/4 (14 files, 62 tables, 434,097 rows). Reports are in ignored `logs/`.
- This meets the P1 **structural business-load** gate (100% ≥81%). It is not a claim that every normalized value or question answer is semantically correct. No train labels were loaded; public data was not used.
- Detailed commands, initial failures, causes, fixes, file list and limits: `tools/checkpoints/2026-11-15_P1_NORMALIZATION_INGESTION.md`.
- Next at the time of this entry: P2 query understanding/time planning. P2–P9 remain NOT MEASURED.

## Playbook-aligned checkpoint — 2026-11-15

The Master Implementation Playbook numbers P1 as multi-business audit/profiles, P2 as ingestion hardening, and P3 as QuerySpec/understanding. Earlier entries used a different numbering; they remain historical. From this checkpoint onward, progress uses the playbook's phase names and gates.

### P3 Query understanding — IN_PROGRESS, not verified

- Added structured `QuerySpec`/`TemporalScope`, intent parsing, period/as-of/comparison handling, and explicit non-executable states for unsupported work.
- Train-question diagnostics: 2,843 / 3,000 interpreted = **94.77% coverage**; 1,620 / 3,000 executable = **54.0% coverage**. These are not accuracy metrics.
- Full suite: 48 run, 45 passed, 3 Git-dependent checks skipped in the no-`.git` working copy.
- The playbook requires a versioned schema and ≥81% on a reviewed holdout, plus schema-validity and ambiguity metrics. No reviewed gold holdout or confusion/slot metrics exist, so P3 is **IN_PROGRESS** and must not be marked passed.
- Detailed commands, limits and next action: `tools/checkpoints/2026-11-15_P3_QUERY_UNDERSTANDING_PARTIAL.md`.
- P1 business profiling remains incomplete. The earlier 30/30 loader census is structural ingestion evidence, not a business support matrix.

### P1 Multi-business audit and profiles — VERIFIED at L1 structural scope

- Generated full structural profiles for 30/30 train businesses: 128 source files, 339 tables/sheets with headers, 3,997,042 census rows, and all 30 README texts (75,751 characters). The corrected UTF-8 filename extracts were used for biz_112, biz_115, biz_118, and biz_130.
- Added per-business train-question intent and unsupported-taxonomy diagnostics. Rule interpretation coverage is 2,843/3,000 (94.77% micro; 95.08% business macro); executable plan coverage is 1,620/3,000 (54.0%). These are coverage diagnostics only, not accuracy or support claims.
- The 30-business matrix marks each business L1 structural only. Candidate joins use header-name matches and require review before execution. Higher support levels remain unverified.
- Full suite after profile changes: 49 run, 46 passed, 3 Git-dependent skips; exit 0.
- Detailed evidence/errors/commands: `tools/checkpoints/2026-11-15_P1_MULTI_BUSINESS_PROFILE_COMPLETE.md`; matrix: `docs/BUSINESS_COVERAGE_MATRIX.md`; ignored machine report: `logs/train_business_profiles.json`.
- P1 phase is complete at L1 structural-profile scope; its later P2 handoff was completed and verified. Business-support coverage remains a separate P7 metric.

## P2 Ingestion hardening — VERIFIED at structural reconciliation scope (2026-11-15)

- Added per-table accepted/rejected/skipped/header counters, scan-completeness status, typed ingestion error codes, error collection across files, and preserved row provenance for CSV/XLSX/SQLite.
- Final train-only census: 30/30 businesses loaded; 128 structured files; 339 tables/sheets; 3,997,042 accepted, 0 rejected, 235 skipped. Reconciled source records: 3,997,277 = 3,997,042 + 0 + 235; every scan completed; no source failures.
- Ingestion tests: 13/13 pass. Full suite after final code: 52 run, 49 passed, 3 Git-only hygiene tests skipped in the isolated no-`.git` copy; exit 0.
- P2 structural reconciliation: **100% PASS**, above the 81% gate. This does not establish semantic-value accuracy or answer quality.
- Machine report: ignored `logs/train_ingestion_reconciliation.json`. Full evidence and file list: `tools/checkpoints/2026-11-15_P2_INGESTION_RECONCILIATION_COMPLETE.md`.
- Next: P3 QuerySpec schema and reviewed business-held-out evaluation. Current P3 coverage counts are not accuracy; keep held-out items out of tuning.

### P2 reconciliation re-audit — 2026-11-15

- Re-ran the current evaluator against the train business-data snapshot: 30/30 loaded, 128 files, 339/339 tables/sheets reconciled; 3,997,277 source = 3,997,042 accepted + 0 rejected + 235 skipped; zero failures.
- Per-business and per-table report validation passed. Machine report SHA-256: `6AE9AC53F6BF2CF932DEC9BE71976A54B34CCA7B45E6DFB451E8DB097DCD6D09` at ignored `logs/p2_reaudit_2026-11-15.json`.
- P1 and P2 are complete as confirmed by the user. P1 is L1 structural profile completion; P7 supported-business coverage is separate. P2 is structural reconciliation, not semantic or answer accuracy.
- No train answers or public-test data were accessed. Full details: `tools/checkpoints/2026-11-15_P2_INGESTION_REAUDIT.md`.

## P3 QuerySpec schema and first holdout — IN_PROGRESS (2026-11-15)

- Added versioned QuerySpec v1 JSON Schema, serializer, and validator. All 2,843 generated train QuerySpecs validate (100%); this is structural validity, not correctness. Full-train intent coverage remains 94.77%; executable coverage 54.0%.
- Added missing schema context fields and generalized top-K extraction to all ranking intents.
- First agent-reviewed holdout: 48 questions across six held-out businesses (`biz_107`–`biz_112`). Intent accuracy 41/48 (85.42%); slot exact match 23/48 (47.92%); slot micro-F1 84.21%; schema-valid 45/45 generated outputs (100%). Slot score covers metric, full time scope, top-K, dimensions, sort, and ambiguity flags; entity/unit/filter accuracy is not scored.
- Ambiguity recall is not measurable because the holdout has zero positive ambiguity cases. Gold annotations are agent-reviewed, not independently reviewed. P3 is **NOT PASSED**: exact match is below 81% and ambiguity evidence is missing. Do not tune against this holdout.
- Full suite after these changes: 55 run, 52 passed, 3 Git-dependent hygiene checks skipped in this no-`.git` snapshot; exit 0.
- Details, commands, checksums, risks, and next action: `tools/checkpoints/2026-11-15_P3_QUERY_SCHEMA_HOLDOUT_PARTIAL.md`.

### P3 development checkpoint — isolated regression fixes (2026-11-15)

- On separate development examples from `biz_125`–`biz_130`, fixed two intent gaps: `dthu` now retains the average-order-value intent and the daily-revenue ranking path; “đắt nhất” is recognized as ranking language.
- Regression sequence established both cases failing, exposed the remaining ranking synonym defect, then passed the focused understanding suite 7/7.
- Full suite: 56 run, 53 passed, 3 Git-only hygiene skips; exit 0. The prior 48-question holdout was not rerun and remains frozen evidence for the earlier parser version only.
- Current parser SHA-256 and exact commands: `tools/checkpoints/2026-11-15_P3_SLOT_DEVELOPMENT.md`. P3 remains NOT PASSED; continue with separate dev examples and ambiguity/entity/unit/time slots, then prepare a new reviewed holdout.

### P3 relative-time alias — VERIFIED regression fix (2026-11-15)

- Added `hnay` recognition to period and point-date parsing; dates still anchor to the question record's `as_of_date`.
- Regression was confirmed failing before the fix and passes after it. Focused timeparse/understanding suite: 13/13; full suite: 57 run, 54 passed, 3 Git-only skips; exit 0.
- Did not replay the inspected holdout or full-train diagnostics after this change. P3 remains NOT PASSED; evidence and hash: `tools/checkpoints/2026-11-15_P3_RELATIVE_ALIAS.md`.

### P3 explicit unit extraction — VERIFIED unit (2026-11-15)

- QuerySpec now normalizes explicitly stated currency, percent, volume, mass and count units; omitted units remain null.
- Four explicit-unit regressions failed before implementation; all pass after. Focused schema tests 4/4; understanding/time 13/13; full suite 58 run, 55 pass, 3 Git-only skips; exit 0.
- Holdout not rerun; P3 remains not passed. Evidence: `tools/checkpoints/2026-11-15_P3_UNIT_EXTRACTION.md`.

### P3 catalog-grounded entity slot — VERIFIED unit (2026-11-15)

- Optional business alias catalog now resolves one canonical entity only for a unique normalized alias match. Multiple matches produce null plus `entity_unresolved`; no catalog never guesses.
- Schema updated for the ambiguity flag. Tests: QuerySpec schema group 5/5; full suite 59 run, 56 passed, 3 Git-only skips; exit 0.
- No holdout replay or label access. P3 remains NOT PASSED pending independent, fresh holdout and full slot/ambiguity metrics. Checkpoint: `tools/checkpoints/2026-11-15_P3_ENTITY_SLOT.md`.

### P3 ambiguity metrics — VERIFIED evaluator unit (2026-11-15)

- Added ambiguity TP/FP/FN, precision, recall, and F1; absent denominators produce null plus an explicit reason.
- Synthetic metric tests include TP/FP/FN and no-positive denominator: focused 2/2. Full suite 61 run, 58 pass, 3 Git-only skips; exit 0.
- No benchmark labels/holdout rerun. P3 remains NOT PASSED pending fresh business-held-out evaluation. Evidence: `tools/checkpoints/2026-11-15_P3_AMBIGUITY_METRICS.md`.

### P3 fresh business-held-out candidate evaluation — diagnostic only (2026-11-15)

- Evaluated 50 question-only candidates across biz_113–biz_118 after freezing parser hash AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C.
- Results: intent 44/50 (88.00%); core slot exact 40/50 (80.00%, below the 81% gate); slot micro-F1 91.84%; schema validity 48/48 interpreted (100%). Ambiguity TP/FP/FN = 1/2/1, precision 33.33%, recall 50%, F1 40%, based on two subjective positive annotations.
- Per-business results are uneven: biz_117 intent 77.78% / slot exact 66.67%; biz_118 66.67% / 66.67%; biz_115 slot exact 75%. P3 remains NOT PASSED.
- Annotation was by one agent, not independent review; earlier train-question coverage diagnostics may have seen these questions. Treat results as diagnostic only and do not tune on this holdout. Entity, unit, filters, and answer correctness are not measured.
- Full suite: 61 run, 58 pass, 3 Git-only hygiene skips; exit 0. No source/test changes in this unit; no answer labels or public-test data read.
- Detailed evidence: tools/checkpoints/2026-11-15_P3_HOLDOUT2_DIAGNOSTIC.md. Exact candidate/gold/report files remain local under ignored logs/ and are excluded from checkpoint archives.
## Archive verification — P3-HOLDOUT-2 diagnostic

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_holdout2-diagnostic.zip
- Archive SHA-256: e30fac0110e145d6e561974433c1a72527c0a1a969357365615024ff3b623b13 (external sidecar: work\checkpoints\2026-11-15_P3_HOLDOUT2_DIAGNOSTIC\archive.sha256; kept outside the ZIP to avoid self-reference).
- Archive entries: 76; internal manifest entries: 75; every SHA-256 verified; ZIP integrity PASS.
- Excluded: local logs, question candidates, gold annotations, train/public data, and generated smoke copies.
- Extracted smoke: work\rehydrated-smoke-P3-holdout2; 61 tests run, 58 passed, 3 Git-dependent skips; exit 0.
- Full post-build evidence: work\checkpoints\2026-11-15_P3_HOLDOUT2_DIAGNOSTIC\POST_BUILD_VERIFICATION.md.

### P3 evaluator coverage expanded — VERIFIED synthetic unit (2026-11-15)

- The holdout evaluator now scores nine slots: metric, time, top_k, dimensions, sort, ambiguity flags, entity, unit, and filters. It separately reports time exact and dimensions exact.
- Synthetic evaluator tests: 4/4 pass. Full suite: 63 run, 60 passed, 3 Git-dependent hygiene checks skipped; exit 0.
- Parser behavior is unchanged. P3-HOLDOUT-2 was not rerun; its prior 80% result covers only the earlier six-field evaluator and remains diagnostic. Do not compare it to a future nine-field exact score.
- Evidence and hashes: tools/checkpoints/2026-11-15_P3_EVALUATOR_FULL_SLOTS.md. P3 remains NOT PASSED pending independent gold, full-slot holdout metrics, and per-business gate evidence.
## P3 full-slot evaluator checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_full-slot-evaluator.zip
- SHA-256: 9b68864ee4eb3ccf25482ff0ba681daff711186c3143d0c51888196890325416; sidecar: work\checkpoints\2026-11-15_P3_EVALUATOR_FULL_SLOTS\archive.sha256.
- Archive contains 77 entries; 76 manifest entries verified, ZIP integrity PASS. No train/public data or generated logs are included.
- Extracted smoke: work\rehydrated-smoke-P3-full-slot-evaluator; 63 tests run, 60 passed, 3 Git-dependent skips; exit 0.
- Post-build verification and external manifest: work\checkpoints\2026-11-15_P3_EVALUATOR_FULL_SLOTS\POST_BUILD_VERIFICATION.md and post_build_manifest.sha256.

### P3 evaluator input validation — VERIFIED synthetic unit (2026-11-15)

- Candidate and gold rows are now validated before scoring; missing required full-slot fields produce a clear ValueError.
- Focused evaluator tests: 5/5. Full suite: 64 run, 61 passed, 3 Git-dependent hygiene skips; exit 0.
- Parser unchanged; P3-HOLDOUT-2 not rerun. No train answers or public-test content read.
- Evidence: tools/checkpoints/2026-11-15_P3_EVALUATOR_INPUT_VALIDATION.md.
## P3 evaluator input-validation checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_evaluator-input-validation.zip
- SHA-256: d7ed0bce2dfce1ff86fadcb3d4ea3767d7d6765409a8fabe0170c5d78e022586; sidecar: work\checkpoints\2026-11-15_P3_EVALUATOR_INPUT_VALIDATION\archive.sha256.
- 77 archive entries; all 76 internal manifest hashes verified; ZIP integrity PASS. No data or generated logs included.
- Extracted smoke: work\rehydrated-smoke-P3-evaluator-input-validation; 64 tests run, 61 passed, 3 Git-dependent skips; exit 0.
- Full verification: work\checkpoints\2026-11-15_P3_EVALUATOR_INPUT_VALIDATION\POST_BUILD_VERIFICATION.md; external manifest PASS.

### P3 same-period year comparison — VERIFIED synthetic unit (2026-11-15)

- Added explicit year-to-date versus same elapsed period in the previous year. The prior period clamps to a valid day in non-leap years.
- Regression was observed before implementation: 2 synthetic cases failed. After fix: timeparse 8/8, understanding 7/7, full suite 66 run / 63 pass / 3 Git-dependent skips; exit 0.
- No holdout replay or label access. Prior P3-HOLDOUT-2 result does not apply to this parser hash; P3 remains NOT PASSED.
- Evidence: tools/checkpoints/2026-11-15_P3_YTD_COMPARISON.md.
## P3 year-to-date comparison checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_ytd-comparison.zip
- SHA-256: 42db858192e687608e2a61fae53a63ef7eab0149d388618d6c207bcaf9cbcad4; sidecar: work\checkpoints\2026-11-15_P3_YTD_COMPARISON\archive.sha256.
- Archive entries: 78; internal manifest entries: 77; all hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extracted smoke: work\rehydrated-smoke-P3-ytd-comparison; 66 tests run, 63 passed, 3 Git-dependent skips; exit 0.
- Post-build verification: work\checkpoints\2026-11-15_P3_YTD_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

### P3 evaluator entity catalog — VERIFIED synthetic unit (2026-11-15)

- Evaluator now passes an optional candidate entity catalog to RulePlanner, so full-slot metrics can measure unique entity resolution and ambiguous-alias flags.
- Two synthetic tests failed before the change and pass after. Focused evaluator tests 7/7; full suite 68 run, 65 passed, 3 Git-dependent skips; exit 0.
- No parser change and no holdout replay. P3 remains NOT PASSED.
- Evidence: tools/checkpoints/2026-11-15_P3_ENTITY_CATALOG_EVALUATOR.md.
## P3 entity-catalog evaluator checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_entity-catalog-evaluator.zip
- SHA-256: e71fa47f6a6888feec7be797360473c56d516522905c760b9d50f984afa32a5b; sidecar: work\checkpoints\2026-11-15_P3_ENTITY_CATALOG_EVALUATOR\archive.sha256.
- Archive entries: 79; 78 internal manifest hashes verified; ZIP integrity PASS; no train/public data or generated logs.
- Extracted smoke: work\rehydrated-smoke-P3-entity-catalog-evaluator; 68 tests run, 65 passed, 3 Git-dependent skips; exit 0.
- Post-build evidence: work\checkpoints\2026-11-15_P3_ENTITY_CATALOG_EVALUATOR\POST_BUILD_VERIFICATION.md; external manifest PASS.

### P3 completed-month comparison — VERIFIED synthetic unit (2026-11-15)

- Added full previous-month versus month-before scope, including year rollover; incomplete comparisons fail closed.
- Baseline suite 8/8; two new positive cases failed before the fix; regex escaping was corrected after the first attempt remained red. Added negative incomplete-period cases.
- Focused timeparse suite 11/11; full suite 71 run, 68 passed, 3 Git-only skips; exit 0.
- No holdout or labels used. P3 remains NOT PASSED. Evidence: tools/checkpoints/2026-11-15_P3_MONTH_COMPARISON.md.
## P3 completed-month checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_month-comparison.zip
- SHA-256: c2bef2c81bbc1155d73de1e498dcc44eda872a24d23429fa0b0d556f7eab2805; sidecar: work\checkpoints\2026-11-15_P3_MONTH_COMPARISON\archive.sha256.
- Archive entries: 80; 79 internal manifest hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extract smoke: work\rehydrated-smoke-P3-month-comparison; 71 tests run, 68 passed, 3 Git-dependent skips; exit 0.
- Full verification: work\checkpoints\2026-11-15_P3_MONTH_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

### P3 completed-quarter comparison — VERIFIED synthetic unit (2026-11-15)

- Added complete previous-quarter versus quarter-before scope, including Q1 year rollover; incomplete comparisons fail closed.
- Two synthetic positive cases failed before the fix; focused timeparse suite 14/14 and full suite 74 run / 71 passed / 3 Git-only skips; exit 0.
- No holdout or labels used. P3 remains NOT PASSED.
- Evidence: tools/checkpoints/2026-11-15_P3_QUARTER_COMPARISON.md.
## P3 completed-quarter checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_quarter-comparison.zip
- SHA-256: 8ff6ff3e64d2a3b49050fd882f4f65e94bf8020dd2b1791f090a85db4479c056; sidecar: work\checkpoints\2026-11-15_P3_QUARTER_COMPARISON\archive.sha256.
- Archive entries: 81; all 80 internal manifest hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extract smoke: work\rehydrated-smoke-P3-quarter-comparison; 74 tests run, 71 passed, 3 Git-dependent skips; exit 0.
- Post-build verification: work\checkpoints\2026-11-15_P3_QUARTER_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

### P3 year-to-date scope precedence — 2026-11-15

- Fixed a precedence bug where “năm nay ... đến hết hôm nay” became a one-day scope instead of Jan 1 through the row's `as_of_date`.
- A new synthetic regression failed before the fix. Afterward, focused time parsing passed 15/15; full suite passed 72/75 with 3 Git-only hygiene skips (exit 0).
- No holdout replay or label/public-test access. P3 remains NOT PASSED; no 81% claim is made.
- Details and hashes: `tools/checkpoints/2026-11-15_P3_YTD_SCOPE_PRECEDENCE.md`.

### P3 requested-unit precedence — 2026-11-15

- Fixed unit extraction so an explicit requested unit such as “một tuýp” wins over a different packaging unit in the product description; added the `tuýp` alias.
- The synthetic regression failed before the fix (`viên` predicted for a `tuýp` price question). Query schema tests pass 6/6; full suite 73/76 passed with 3 Git-only hygiene skips (exit 0).
- No holdout replay or label/public-test access. P3 remains NOT PASSED.
- Details and hashes: `tools/checkpoints/2026-11-15_P3_REQUESTED_UNIT_PRECEDENCE.md`.

### P3 percent revenue-share cue — 2026-11-15

- Fixed percent-marked questions with an explicit contribution cue and category being classified as total revenue instead of `revenue_share`.
- Synthetic regression failed before the fix; understanding tests pass 8/8 and the full suite passes 74/77 with 3 Git-only skips (exit 0).
- No holdout replay or label/public-test access. P3 remains NOT PASSED.
- Details and hashes: `tools/checkpoints/2026-11-15_P3_REVENUE_SHARE_CUE.md`.

### P3 supplier-ranking QuerySpec — 2026-11-15

- Fixed supplier-purchase ranking questions being interpreted as product sales rankings. The planner now emits a structured, non-executable `supplier_ranking` spec with supplier dimension and purchase metric.
- Synthetic regression failed before the fix; understanding tests pass 9/9 and the full suite passes 75/78 with 3 Git-only skips (exit 0).
- Execution remains intentionally unsupported until purchase-source semantics are verified. P3 remains NOT PASSED.
- Details and hashes: `tools/checkpoints/2026-11-15_P3_SUPPLIER_RANKING_SPEC.md`.


## Active workspace update — P3 blind review packet (2026-11-15)

- Rehydrated the verified feature snapshot at base `24cfa0908bd20f6e5b210366e956cae0d665b56e` into the current writable project. The extracted copy has no `.git`; the real checkout was not accessed or changed.
- Created a frozen, question-only independent-review packet: 72 primary candidates (12 each across `biz_101`–`biz_106`) and 4 disjoint no-explicit-time challenge candidates. Only `sources/train.zip::train/questions.jsonl` was read. No train answers or public-test contents were opened and the parser was not run on candidates.
- The selected fresh businesses contain only four no-explicit-time questions. The challenge is retained as a small separate diagnostic set and cannot support a stable ambiguity-recall claim by itself. The primary full-slot gold must be independently annotated and adjudicated before P3 scoring.
- P3 remains IN_PROGRESS / NOT PASSED; no ≥81% claim. P4–P8 remain gated in sequence until P3 acceptance.
- Packet: `work/reviews/P3_HOLDOUT3`; manifest SHA-256 `c8fb19220e50fe7348b8de3308a5c90e3f9a06da24dff51038b5637dc17f9621`. Detailed evidence: `tools/checkpoints/2026-11-15_P3_BLIND_REVIEW_PACKET.md`.
- Source-code changes this work item: none. Latest suite before this documentation update: 78 run, 75 passed, 3 Git-dependent skips, exit 0; rerun is recorded in the next checkpoint.

- Post-update suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — exit 0, 78 run / 75 passed / 3 Git-dependent hygiene skips. Packet integrity check passed: 72 primary, 4 challenge, zero overlap, 76 annotation rows, candidate hashes valid.
# Submission-priority checkpoint — 2026-11-15

Today's submission preflight has been completed as far as the available machine allows. Critical runner fixes now flush each answer immediately, stream question JSONL with line-numbered errors, and serialize organizer-required trace fields. The full suite passed: 80 run, 77 passed, 3 Git-only hygiene skips. A 12-question, train-only smoke was deterministic across two runs and produced schema-valid outputs/logs; no labels or public/private test data were used.

**GO/NO-GO: NO-GO.** Docker/Podman/Buildah/Nerdctl are unavailable and WSL status failed, so Docker build, target-GPU compatibility, and network-disabled inference remain unverified. No portal attempt or submission was made. Final candidate build context: `work/submission-build/context-final-verified-2026-11-15`. This is not an uploadable Docker image. P3 review remains NOT COMPLETED / NOT PASSED; no annotations or independent validation are claimed. Exact artifact checksum and inventory: `work/submission-build/FINAL_ARTIFACT_RECORD.md`. Details and exact next actions: `tools/checkpoints/2026-11-15_SUBMISSION_PREFLIGHT.md`.

# Public submission artifact work — 2026-11-15

The portal screenshots show a JSONL Public Submission flow separate from Docker Test Solution. A single public-data inference pass is being prepared in an isolated output directory. It is for submission review only; public questions will not be used for tuning, and no accuracy will be reported because the archive contains no labels. The Docker image remains a separate, unverified deliverable. Pre-work record: `tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_START.md`.
# Public Test JSONL candidate — 2026-11-15

Generated once from the frozen isolated snapshot for the portal's Public Submissions flow. It contains 1,000 valid ordered records for 1,000 questions across 14 businesses; the project validator passed, 1,000 trace records matched, and no per-question runtime exceptions were logged. The engine abstained on 718 questions (71.8%), so answer accuracy/PA is unknown and this output is only format/runtime verified. Public questions were not used for tuning and no labels were present.

Review package: work/submission-build/public-test-submission-2026-11-15. JSONL SHA-256 0de940823521e386477efeb76c26d6533e61cabf1977b5c0d9cbb6fd0d61e112; MD5 85b4acc0abf681c8b5a6a6a6812910ab; 44,806 bytes. It has not been uploaded. This is separate from the Docker Test Solution artifact, which remains blocked. P3–P8 are still incomplete; see tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_COMPLETE.md.


## Latest update — 2026-11-17 — v26

- Full project history, phase status, and current risks: `docs/PROGRESS_REPORT_2026-11-17.md`.
- v26 train-only replay (3,000 questions): 237 correct, 6 wrong, 2,757 abstain; answered accuracy 97.53%, coverage 8.10%, PA 7.70%, 0 runtime errors. In-sample diagnostic only; not a Public Test score.
- Current tests: 189 run, 186 passed, 3 Git-dependent skips; focused pipeline 69/69 passed.
- P3 remains NOT VERIFIED / NOT PASSED because independent review was skipped. Public labels remain unopened. Source-root public JSONL is stale (998 abstain / 2 number), not v26.
- Main v26 implementation and primary regression files match the validated snapshot; this update changes tracking documents only.
- Next: investigate remaining sales-ranking errors generically, preserve the rulebook cancellation definition, then replay train from a new frozen output before public inference.


## 2026-11-19 — Multi-bundle vertical slice

- Added a first composite path for same-period side-by-side `revenue` + `collected_amount` questions.
- Existing single-metric executors and verifier are reused per component; composite verification is all-or-nothing.
- Added synthetic regression coverage and a feature-branch GitHub Actions test workflow.
- CI verification is pending; no local test execution is claimed. See `tools/checkpoints/2026-11-19_MULTI_BUNDLE_VERTICAL_SLICE.md`.


### CI result — commit `77dbd90e204356211c70a2cf56f7f52249cde01a`

- GitHub Actions executed 197 tests. The new composite tests and other functional tests passed; the job failed only in two existing repository-hygiene checks.
- Both failures identify the pre-existing tracked file `CODEX PROGRESS`: it exceeds the 1,000,000-byte hygiene limit and contains strings matching the repository's secret-like regex scan.
- The file predates this implementation and was not modified. Do not weaken the secret scan or delete the file as a shortcut. Resolve its archival/storage policy separately, then rerun the complete suite.
- Workflow: https://github.com/pl2n/DataMate/actions/runs/44541834717


## 2026-11-19 — XLSX grouped-header ingestion

- Added conservative support for two-row Excel headers when the first row contains at least two distinct horizontal merged groups and the next physical row contains complete leaf labels.
- Canonical display headers use `Group / Field`; original raw header rows and physical row numbers are preserved on `Table` and exposed by `profile()`.
- A single merged report title is not interpreted as a grouped header. Unsupported/ambiguous layouts retain the existing one-row fallback or fail closed.
- Synthetic tests cover grouped headers, original-header preservation, row provenance, profile output, and single-title false-positive avoidance.
- GitHub Actions run `44545450222`: 199 tests ran; both new grouped-header tests passed. 197 tests passed; 2 pre-existing hygiene tests failed on tracked `CODEX PROGRESS` (size limit and secret-like regex). No hygiene check was weakened.
- Checkpoint: `tools/checkpoints/2026-11-19_EXCEL_GROUPED_HEADERS.md`.


## 2026-11-19 — initial semantic column mapping

- Added `src/datamate/semantic.py` with exact alias mapping for a small set of canonical fields.
- Grouped Excel headers can use group-plus-leaf evidence, e.g. `Thanh toán / Giá trị` maps to a payment-event amount, while standalone `Giá trị` remains unresolved.
- Duplicate source columns targeting the same canonical field are marked ambiguous; no column is selected.
- This is a metadata-only layer and does not change executor behavior or join data.
- Added synthetic tests for exact mapping, contextual mapping, generic ambiguous labels, collisions, and unknown columns.
- Checkpoint: `tools/checkpoints/2026-11-19_SEMANTIC_COLUMN_MAPPING.md`.


### CI result — semantic mapping commit `5ae3742308a236152210f12cec726cdf75c85de8`

- GitHub Actions run `44546168818` executed 203 tests. The four new semantic mapping tests passed; 201 tests passed overall.
- The only two failures remain the pre-existing hygiene checks on tracked `CODEX PROGRESS` (over 1 MB and matching a secret-like regex). No security checks were weakened.
- Run: https://github.com/pl2n/DataMate/actions/runs/44546168818


## 2026-11-19 — initial relationship validation

- Added `src/datamate/relationships.py` to discover relationship candidates only through shared, unambiguous canonical key mappings.
- Exact string key matching preserves leading zeroes and avoids implicit numeric conversion.
- Cardinality checks validate complete child-to-unique-parent coverage; partial, blank, unmatched, and many-to-many cases remain non-executable.
- The module is metadata-only and does not perform joins.
- Added synthetic tests for many-to-one, unmatched keys, duplicate parents, partial overlap, blank keys, unmapped labels, and leading-zero preservation.
- Checkpoint: `tools/checkpoints/2026-11-19_RELATIONSHIP_VALIDATION.md`.


### CI result — relationship validation

- GitHub Actions run `44546976679` executed 210 tests. All relationship discovery tests passed; 208 tests passed overall.
- The only two failures remain pre-existing hygiene assertions on tracked `CODEX PROGRESS` (size limit and secret-like regex). No security checks were weakened.
- Run: https://github.com/pl2n/DataMate/actions/runs/44546976679


## 2026-11-19 — declarative metric bundle registry

- Added `src/datamate/bundles.py` with explicit metric-to-bundle definitions, executor intent, output type, required capability labels, and rule-profile labels.
- Updated `CompositePlanner` to resolve the current revenue/collection pair through the registry instead of embedding bundle IDs in the planner.
- Unknown or duplicate metric requirements fail closed. Existing executor and verifier behavior is retained.
- Added registry validation tests. This does not yet generalize question parsing beyond the fixed first financial pair.
- Checkpoint: `tools/checkpoints/2026-11-19_BUNDLE_REGISTRY.md`.


### CI result — bundle registry and composite integration

- GitHub Actions run `44547696247` executed 216 tests. The registry tests and composite regressions passed; 214 tests passed overall.
- The only two failures remain pre-existing hygiene assertions on tracked `CODEX PROGRESS` (size limit and secret-like regex). No hygiene check was bypassed.
- Run: https://github.com/pl2n/DataMate/actions/runs/44547696247


### CI result — bundle registry (latest constrained composite planner)

- GitHub Actions run `44547696247` executed 216 tests. All bundle registry and composite tests passed; 214 tests passed overall.
- Two existing repository-hygiene checks still fail against tracked `CODEX PROGRESS` (size limit and secret-like regex). No test was disabled.
- Run: https://github.com/pl2n/DataMate/actions/runs/44547696247


## 2026-11-19 — business schema catalog

- Added `src/datamate/schema_catalog.py` to combine table-level semantic mappings and relationship evidence into a versioned catalog.
- Duplicate table names can be resolved by source file; ambiguous lookups return no result.
- Catalog serialization retains per-column mapping evidence and relationship cardinality/coverage evidence.
- No joins or metric execution are performed.
- Added synthetic integration tests for mapped fields, validated relationships, duplicate table names, and generic-label abstention.
- Checkpoint: `tools/checkpoints/2026-11-19_SCHEMA_CATALOG.md`.


### CI result — business schema catalog

- GitHub Actions run `44548265235` executed 219 tests. All catalog integration tests passed; 217 tests passed overall.
- The only two failures remain the pre-existing hygiene checks against tracked `CODEX PROGRESS` (size limit and secret-like regex). No checks were disabled.
- Run: https://github.com/pl2n/DataMate/actions/runs/44548265235


## 2026-11-19 — requirement extraction layer

- Added `src/datamate/requirements.py` to translate recognized composite QuerySpec intents into explicit metric requirements.
- The first rule maps only `financial_metric_comparison` to revenue and collected-amount requirements.
- `CompositePlanner` now consumes the extraction result and resolves each requirement through the bundle registry.
- Single intents, unknown intents, unresolved bundles, non-numeric output types, and unsupported comparison modes fail closed.
- No arbitrary conjunction splitting or new metric execution was introduced.
- Added extraction tests for resolved, unsupported, and unresolved cases.
- Checkpoint: `tools/checkpoints/2026-11-19_REQUIREMENT_EXTRACTION.md`.


### CI result — requirement extraction

- Initial run `44548728199` exposed a stale type annotation after moving the requirement model; fixed in commit `45330bc6accdc30e38eff31217422c3f01121253`.
- Follow-up run `44548881088` executed 222 tests with no import/runtime/test errors. 220 passed; the only two failures remain the pre-existing hygiene assertions against tracked `CODEX PROGRESS` (size and secret-like regex).
- Run: https://github.com/pl2n/DataMate/actions/runs/44548881088


## 2026-11-19 — versioned requirement extraction contract

- Added `schemas/requirement_extraction.v1.schema.json`.
- Added JSON-native serialization and validation for requirement extraction payloads.
- Added cross-field checks: resolved composites need at least two unique requirements and no failure reason; unresolved/unsupported results cannot carry executable requirements and must explain why.
- Composite planning now validates the requirement contract before compiling component plans.
- Added tests for valid payloads, duplicate metrics, unresolved payloads, and status/reason mismatch.
- Checkpoint: `tools/checkpoints/2026-11-19_REQUIREMENT_SCHEMA.md`.


### CI result — versioned requirement schema

- GitHub Actions run `44549585604` executed 226 tests with no code/test errors. 224 passed.
- The only two failures remain pre-existing hygiene assertions against tracked `CODEX PROGRESS` (size limit and secret-like regex). No checks were disabled.
- Run: https://github.com/pl2n/DataMate/actions/runs/44549585604


## 2026-11-19 — composite rule registry

- Replaced the fixed intent-to-metric dictionary in `RequirementExtractor` with an explicit `CompositeRuleRegistry`.
- Rules declare a recognized QuerySpec intent, an ordered list of metric IDs, and a supported comparison type.
- The default registry still contains only `financial_metric_comparison` → `revenue` + `collected_amount`.
- `CompositePlanner` now compiles any explicitly registered intent; unregistered intents still fail closed. No arbitrary conjunction parsing was added.
- Added tests for registry uniqueness, invalid rule definitions, custom allowlisted metric composition, and unknown-intent abstention.
- Checkpoint: `tools/checkpoints/2026-11-19_COMPOSITE_RULE_REGISTRY.md`.


### CI result — composite rule registry

- GitHub Actions run `44550215128` executed 230 tests with no code/test errors. 228 passed.
- The only two failures remain the pre-existing hygiene assertions against tracked `CODEX PROGRESS` (size limit and secret-like regex). No checks were disabled.
- Run: https://github.com/pl2n/DataMate/actions/runs/44550215128


## 2026-11-19 — composite shared-context safety gate

- Composite planning now rejects any populated QuerySpec filters, non-metric dimensions, sorting, or top-k options instead of clearing them while creating component specs.
- The existing `metric` dimension marker is allowed; other dimensions are not silently discarded.
- Added synthetic tests for explicit filters, unsupported dimensions, and ranking options.
- Checkpoint: `tools/checkpoints/2026-11-19_COMPOSITE_CONTEXT_GUARD.md`.


### CI result — composite context guard

- GitHub Actions run `44550780980` executed 232 tests with no code/test errors. 230 passed.
- The only two failures remain the pre-existing hygiene assertions against tracked `CODEX PROGRESS` (size limit and secret-like regex). No checks were disabled.
- Run: https://github.com/pl2n/DataMate/actions/runs/44550780980


### Repository hygiene baseline clarified — 2026-11-19

- The two recurring CI failures are inherited from upstream `DangDuuTapCode/DataMate` `main`; the fork contains the identical `CODEX PROGRESS` blob (SHA `1190ffbe02bd0081e84786f6fb4f09ee5d7f588f`).
- The file is 2,058,368 bytes, causing the existing 1 MB hygiene limit to fail.
- The configured secret-like regex has one match inside a Google search URL's `mstk` query parameter in that file; the surrounding context identifies it as a search URL parameter, not an API-key field. The other configured credential patterns have no matches.
- No credential value is copied into this note. The file and hygiene tests were not changed because this is an inherited upstream artifact, not part of the feature work.

## 2026-11-19 — bundle capability resolution

- Extended bundle definitions with exact required canonical fields and declarative required relationship shapes.
- Added BundleCapabilityResolver to check mapped fields, ambiguous mappings, missing/rejected relationships, and unverified business-rule capability labels against BusinessSchemaCatalog.
- Required fields must co-occur in at least one source table; unrelated tables cannot collectively satisfy one bundle's field set.
- CompositePlanner accepts an optional schema catalog and fails closed when any required bundle capability is unavailable.
- Collection declares its exact required fields (payment-event amount and payment date). Revenue deliberately has no flat required-field list yet: the executor supports alternative direct-line and detail-to-order source shapes, which a simple same-table field tuple cannot represent accurately. Both default bundles remain unavailable under catalog-gated planning until source-role/business-rule evidence is modeled and verified.
- No automatic joins or changes to existing metric calculations.
- Added synthetic tests for available/missing/ambiguous/co-location field checks, validated/missing/rejected relationships, planner gating, and unverified default rule capabilities.
- Design note: docs/BUNDLE_CAPABILITY_RESOLUTION.md.
- Checkpoint: tools/checkpoints/2026-11-19_BUNDLE_CAPABILITY_RESOLUTION.md.
- CI pending at checkpoint creation.

### CI result — bundle capability resolution

- GitHub Actions run 44554164419 executed 241 tests.
- 239 tests passed; the only two failures were the known inherited repository-hygiene checks against CODEX PROGRESS (file-size limit and secret-like regex).
- No import/runtime errors or feature-test failures were reported. The new bundle capability and planner integration tests passed.
- Run: https://github.com/pl2n/DataMate/actions/runs/44554164419
- Executor inspection corrected the initial bundle declarations: revenue has no flat required-field list yet because the executor accepts direct line-grain and detail-to-order source shapes. Collection requires payment-event amount and payment date; payment-role and status policy remain unverified. The production pipeline now builds a per-business BusinessSchemaCatalog and passes it to CompositePlanner.

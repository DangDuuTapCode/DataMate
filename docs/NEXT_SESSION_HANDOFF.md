# RESUME HERE — 2026-11-16

## Active slice — daily revenue threshold day count (started 17:08 GMT+7)

- Continue from `tools/checkpoints/2026-11-16T1708+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_START.md`.
- Evidence: v16 wrong case for biz_124 was misclassified as `quantity`; it answered 4,291 from purchase quantity for a request counting days with revenue >= 15,000,000 VND (train reference 8). Do not hardcode this value or business ID.
- Implement a strict generic intent and aggregate after-discount eligible revenue by date, then count dates meeting the explicit parsed threshold. Preserve unsuccessful-order exclusions. Add synthetic tests before replay.
- If tests pass, generate a fresh hash-frozen train replay at a new directory and evaluate train only after validation. Keep v16 immutable; no public/private labels.
- Maintain reviewer status as skipped/not verified/not passed. Do not touch sources, official checkout, Docker, or Git synchronization.
- Completion correction: this slice is implemented and all tests passed. Read `tools/checkpoints/2026-11-16T1717+07-00_P6_DAILY_REVENUE_THRESHOLD_COUNT_COMPLETE.md`. Focused 71/71; full suite 160 run, 157 pass, 3 Git-dependent skips. Source is now modified in `work/rehydrated-2026-11-15-P3/source`; do not assume the replay was rerun.
- Immediate next action: check replay CLI arguments, then freeze a fresh v17 in a new output directory using `work/evaluation/train-inputs-2026-11-16-with-split-metadata`. Confirm manifest includes rulebook/calendar and validates code/input/predictions/traces before train-only evaluation. Preserve all v16 files.
- Correction: replay CLI checked. v17 generation has started using `tools/replay_predictions.py`; output is `work/evaluation/p6-train-replay-v17-daily-revenue-threshold-2026-11-16/`. Read `tools/checkpoints/2026-11-16T1718+07-00_P6_V17_TRAIN_REPLAY_START.md`; do not launch a duplicate. Validate freeze before evaluator.
- Correction: generation is complete and `validate_frozen_replay` passed. Read `tools/checkpoints/2026-11-16T1728+07-00_P6_V17_TRAIN_FREEZE_VALIDATED.md`. 3,000 predictions/traces, 30 businesses, matching IDs/order, rulebook/calendar hashed, labels not accessed. Safe next step is evaluator on the official train archive only; it revalidates the freeze before reading labels.
- v17 was scored: 26 correct, 3 wrong, 2,971 abstain, 0 runtime errors, p95 22 ms; in-sample only. The threshold intent recognizes the target but currently abstains `missing_column` because detail lines and invoice date/status are separate. Train-only structural scan confirmed README-documented relation, unique invoice IDs, and full line-key coverage. Continue from `tools/checkpoints/2026-11-16T1736+07-00_P6_DAILY_REVENUE_SAFE_JOIN_START.md`; add only the validated fail-closed join, test, then replay to a new v18 path. Do not score until freeze validation passes.
- Join synthetic tests passed. Correction: real biz_124 smoke still abstains because many invoice dates are numeric Excel serials and `_period` drops the workbook epoch. Read `tools/checkpoints/2026-11-16T1742+07-00_P6_EXCEL_DATE_SYSTEM_PROPAGATION_START.md`; propagate `Table.date_system` into date parsing and the temporary joined table, add strict tests, rerun, then replay in a fresh path. Do not claim the target works yet.

## P1 — targeted competition-rule review (14:46 GMT+7)

- Read `tools/checkpoints/2026-11-16T1446+07-00_P1_TARGETED_COMPETITION_RULE_REVIEW.md`.
- Technical concept is aligned, but compliance is not certified. Before artifact release, resolve: outside scenario-set rights/track permission; whether any contest data is allowed/required in the image; correct portal category for a rule-only solution; complete image license inventory; and §8.2 restrictions on GitHub sharing during the competition.
- Current `training_code/` contains no dataset. Do not add `train.zip` while Dockerfile copies all of `training_code/`; runtime consumes mounted `/data`. Keep outside scenario/public/private test materials out of training and submission artifacts.
- The user-pasted §4.5 is stricter than the linked Vietnamese PDF; follow the stricter wording pending organizer clarification. Do not claim compliance based on this targeted review.

## Active P6 — frozen current-code train replay, 14:15 GMT+7

- Read `tools/checkpoints/2026-11-16T1415+07-00_P6_CURRENT_RULEBOOK_CALENDAR_REPLAY_START.md`.
- v13 output was generated but is invalid for scoring: freeze validation caught a post-generation hash change in `src/datamate/understanding.py`; no labels were opened. Read `tools/checkpoints/2026-11-16T1433+07-00_P6_REPLAY_FREEZE_MISMATCH.md` and preserve the v13 output.
- The regression was fixed by restoring the previously checkpointed `split_rules` forwarding in `RulePlanner`; 40 focused tests passed. See `tools/checkpoints/2026-11-16T1435+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_COMPLETE.md`.
- v13 output directory (preserve, unevaluated): `work/evaluation/p6-train-replay-v13-current-rulebook-calendar-2026-11-16/`. Generate v14 in a fresh directory and validate its freeze/input/code checksums before scoring.
- v14 is now generated at `work/evaluation/p6-train-replay-v14-current-rulebook-calendar-2026-11-16/` and passed freeze validation for 3,000 questions. No labels were accessed. Read `tools/checkpoints/2026-11-16T1448+07-00_P6_V14_FREEZE_VALIDATED.md`, then run evaluator on v14 only; it revalidates before opening train answers.
- Correction: v14 scoring found an incomplete replay fixture, not an answer-quality result. All 3,000 traces abstain because `rulebook.md` is missing; both split metadata files were absent from its frozen input. Keep v14/report intact and do not cite its score as system quality. Read `tools/checkpoints/2026-11-16T1450+07-00_P6_V14_INCOMPLETE_INPUT_FINDING.md`; create a distinct input root with train `rulebook.md` + `calendar.csv`, regenerate to a new replay directory, validate, then score train only.
- The distinct metadata-complete root has been created, and v15 replay is currently running to `work/evaluation/p6-train-replay-v15-with-split-metadata-2026-11-16/`. Read `tools/checkpoints/2026-11-16T1626+07-00_P6_COMPLETE_TRAIN_INPUT_V15_START.md`. Wait for the existing process; do not start a duplicate. No label access until freeze validation passes.
- Correction: v15 finished, but its input manifest omitted `rulebook.md` and `calendar.csv`; its hash matches v13 despite the different root. Do not evaluate it. Fix manifest hashing and test before a new replay. See `tools/checkpoints/2026-11-16T1629+07-00_P6_REPLAY_METADATA_HASH_FIX_START.md`.
- Completed the fix and targeted tests (3/3 passed). Replay input preflight now requires both metadata files and hashes them; tests reject rulebook/calendar changes after freeze. Read `tools/checkpoints/2026-11-16T1633+07-00_P6_REPLAY_METADATA_HASH_FIX_COMPLETE.md`; create v16 in a new output directory and verify the manifest includes both metadata files before scoring train answers.
- v16 is now running in exec session `50250`, output `work/evaluation/p6-train-replay-v16-metadata-hashed-2026-11-16/`. Read `tools/checkpoints/2026-11-16T1635+07-00_P6_V16_METADATA_HASHED_REPLAY_START.md`; poll the same session and do not restart. Validate the explicit rulebook/calendar entries plus all freeze checks before train-only scoring.
- Correction: v16 finished and `validate_frozen_replay` passed. The manifest lists both split metadata files; all 3,000 prediction/trace rows and checksums match; no labels were opened. Read `tools/checkpoints/2026-11-16T1642+07-00_P6_V16_METADATA_HASHED_FREEZE_VALIDATED.md`, then run evaluator with v16 + the exact metadata-complete input + official train archive only.
- Correction: v16 was scored after evaluator revalidated. It is an in-sample train diagnostic: 26 correct, 4 wrong, 2,970 abstain; 1% coverage; answered accuracy 86.67%; penalized accuracy 0.733%; p95 18 ms; no runtime errors. The dominant problem is coverage, not runtime. Read `tools/checkpoints/2026-11-16T1645+07-00_P6_V16_TRAIN_DIAGNOSTIC_EVALUATED.md`; inspect the four errors and top abstention buckets, then implement generic fixes with synthetic tests and a new freeze. Do not claim acceptance; no public/private labels.
- After reporting metrics, continue the highest-impact unverified Playbook workstream. Preserve all compliance uncertainties recorded below; no public-test data/labels, Git, Docker, `sources/` writes, or official checkout changes.

## Latest completion — split calendar and Tết periods, 14:08 GMT+7

- Read `tools/checkpoints/2026-11-16T1408+07-00_P4_SPLIT_CALENDAR_TET_SUPPORT_COMPLETE.md`.
- `main.run` now supplies both split rules and calendar to `RulePlanner`; Tết period comes from configured lunar window and calendar mapping. Tết comparison is enabled only by its explicit rulebook clause. Explicit Gregorian month phrases still win over “Tết” in product names.
- Verification: `PYTHONPATH=src python -m unittest tests.test_timeparse -v` (19 passed); `PYTHONPATH=src python -m unittest tests.test_api.ApiTests.test_runner_uses_the_mounted_lunar_calendar_for_tet -v` (1 passed); read-only smoke checked only `rulebook.md` and `calendar.csv` in both official archives and resolved the same 2026 dates.
- General regulation review is preliminary, not a whole-entry compliance certification. Whether the DataMate track allows the separate outside scenario set, and that file's provenance, rights, and personal-data status, remain unverified. Keep it out of training and packaged artifacts until documented. No public-test questions/labels were read.
- Additional submission risks: current `models/manifest.json` declares no model, while the portal screenshot offers only API/large-model/small-model categories; confirm the valid selection with track rules/organizer and never mislabel. `openpyxl==3.1.5` plus the vLLM base image need a complete third-party license/provenance inventory; none was found in the repository, so regulation §4.5 is not evidenced. Outside data rights and the allowed track category are unresolved.
- Next: continue with the next unverified high-impact Playbook requirement; the bounded P5 typed-gate completion is recorded below. Do not revisit P0–P2, run a full suite, use Docker, modify `sources/`, or touch Git/official checkout.

## Latest bounded P5 completion — typed verifier gate, 14:12 GMT+7

- Read `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`.
- Five focused tests passed for type compatibility, confidence/evidence validation, and ranking cardinality. Empty/overlong lists abstain; short nonempty lists can answer when fewer candidates exist. P5 overall remains partial/not accepted.
- Next: choose the next unverified high-impact Playbook requirement from the existing handoff/checkpoints; do not repeat P0–P2 or rerun the full suite unless required by the changed slice. Keep the outside scenario set out of training/submission until the track rule and provenance/license are verified.

## Latest handoff — competition-rule conformance correction, 13:44 GMT+7

- Read `tools/checkpoints/2026-11-16T1344+07-00_P4_COMPETITION_RULEBOOK_CONFORMANCE_COMPLETE.md` first.
- Runtime now loads split `rulebook.md`; revenue uses after-discount line amounts and the split's stated date/status rules. Cancellation-rate numerator and ranking defaults/ties are also read from the rulebook. The earlier D10 order-total and grouped-unsuccessful convention is superseded for contest inference.
- Focused changed-code regressions passed 16/16 across two targeted commands; the train rulebook parser smoke passed. The complete suite was not run per user's time constraint.
- Risks: parser intentionally accepts only recognized clauses and abstains if required clauses are unsupported. This slice does not implement all rulebook topics, multi-file joins, or split-specific time parsing. Do not claim overall competition compliance based on this slice alone.

## P5 typed verifier gate start checkpoint — completed at 14:12 GMT+7

- Start record: `tools/checkpoints/2026-11-16T1330+07-00_P5_TYPED_ANSWER_VERIFICATION_START.md`.
- Completion: `tools/checkpoints/2026-11-16T1412+07-00_P5_TYPED_VERIFIER_GATE_COMPLETE.md`; the bounded gate tests passed, but this does not establish full P5 acceptance.

## Resume here — VND and million-suffix normalization complete, 13:25 GMT+7

- Completion checkpoint: `tools/checkpoints/2026-11-16T1325+07-00_P4_VND_MILLION_NORMALIZATION_COMPLETE.md`.
- Current parser supports explicit VND grouping and `tr`/`triệu` million notation while preserving ambiguity absent sufficient evidence. Full suite 142 run / 139 passed / 3 Git-dependent skips. v12 replay is frozen/evaluated, prediction-identical to v11; no score improvement claim.
- Read-only source audit parsed all values in two README-documented after-discount detail columns. Exact detail/order totals disagree for most orders, so do not add a join or replace the order total without a documented reconciliation rule.
- Preserve user-confirmed revenue rule (exclude canceled, returned-after-delivery, failed-delivery). Continue with remaining generic P4/P5 evidence-backed criteria; no Public Test tuning, label-specific logic, Git, Docker, `sources/`, or official checkout writes. P3 reviewer skipped / P3 NOT VERIFIED / NOT PASSED.

## Resume here — P4/P5 no-data reason tests completed, 13:00 GMT+7

- Completion checkpoint: `tools/checkpoints/2026-11-16T1300+07-00_P4_NO_DATA_REASON_INTENT_COVERAGE_COMPLETE.md`.
- Current suite: 140 run, 137 passed, 3 Git-dependent skips. Last unit changed tests/docs only; production source and frozen v11 replay remain current.
- User confirmed revenue excludes canceled, returned-after-delivery, and failed-delivery order totals. This rule is in `docs/decisions.md` and `docs/BUSINESS_COVERAGE.md` and has a synthetic regression.
- Continue with generic P4/P5 reliability work and documented source contracts. Keep P3 reviewer skipped / P3 NOT VERIFIED / NOT PASSED; do not tune on Public Test or hardcode IDs. Stay in the isolated source copy; no Git, Docker, source archive, or official checkout changes.

## Resume here — P4/P5 no-data versus zero completed, 2026-11-16 12:48 GMT+7

Start with `tools/checkpoints/2026-11-16T1248+07-00_P4_NO_DATA_ZERO_SEMANTICS_COMPLETE.md` and the internal reason contract in `docs/VERIFIER_REASON_CODES.md`.

- Working copy: `work/rehydrated-2026-11-15-P3/source`; isolated/no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`. Do not touch the official checkout or `sources/`.
- `no_data` means a unique supported source has zero raw records in the requested period; valid matching rows that aggregate to zero remain numeric `0`. External abstain serialization is unchanged.
- Tests for this code state: focused 48 passed; full suite 136 run / 133 passed / 3 Git-dependent skips, exit 0.
- v11 was freeze-validated and evaluated; predictions match v10 byte-for-byte. Score: 40 correct, 44 wrong, 2,916 abstain, PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 37 ms, no runtime errors. `no_data` did not occur in train traces; synthetic tests cover its branch. Revenue is 30/44 wrong in this in-sample diagnostic.
- Continue with a generic revenue source-selection/aggregation defect supported by evidence and the user's definition (after-discount order total). Do not hardcode business or question IDs; do not tune on Public Test. Freeze and validate predictions before any evaluator label read.
- P3 reviewer remains skipped; P3 is NOT VERIFIED / NOT PASSED. P4/P5 remain in progress/not accepted. No Git, public-test tuning, Docker, source archive edits, commit, or push.

## Latest P5 slice — order-status trace reasons, 2026-11-16 12:32 GMT+7

Start with `tools/checkpoints/2026-11-16T1232+07-00_P5_ORDER_STATUS_TRACE_REASON_COMPLETE.md`.

- Added `missing_order_status`, `unknown_order_status`, and `conflicting_order_status` to internal trace decisions for unsuccessful-order-rate abstentions. Submission JSONL remains backward-compatible.
- Focused pipeline/API suite 47/47; full suite 135 run, 132 passed, 3 Git-dependent skips.
- v10 full train replay at `work/evaluation/p6-train-replay-v10-status-trace-2026-11-16` validated 3,000 predictions/traces before labels were read by the evaluator. Predictions are byte-identical to v9; 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 18 ms; 0 runtime errors. New reason codes are only synthetically exercised because train traces did not contain those cases.
- Resume the remaining safe Playbook workstreams. Preserve the status/revenue contracts, do not tune on labels, and keep P3 reviewer skipped / P3 **NOT VERIFIED / NOT PASSED**. Docker is out of scope.

## Latest handoff — shared order-outcome convention, 2026-11-16 11:54 GMT+7

Start with `tools/checkpoints/2026-11-16T1126+07-00_UNSUCCESSFUL_ORDER_STATUS_RULE_START.md` and the shared convention in `docs/BUSINESS_COVERAGE.md`.

- Work in `work/rehydrated-2026-11-15-P3/source`, isolated/no-Git, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`. Do not touch official checkout or `sources/`.
- User-approved rate rule: cancellation, return after delivery, and failed delivery are distinct raw statuses but all count in the unsuccessful-order numerator. Pending/in-transit are separate; use unique order IDs; abstain if any relevant order status is unknown/missing, conflicting, or unavailable via an exact documented header. `Đổi trả` currently maps to returned. Never infer from customer/e-invoice status.
- Implemented classifier/header matching and five regressions. Focused suite passed 35/35; full suite passed 132 total, 129 passed, 3 Git-only skips. Real source smoke recognized 4/4 biz_101 statuses and 7/7 biz_116 statuses; derived full-period rates were 4.60% and 2.47%.
- v9 predictions were frozen and validated (3,000 records/traces) before evaluation. Report: `work/evaluation/p6-train-replay-v9-order-outcomes-2026-11-16/evaluation_report.json`; 40 correct, 44 wrong, 2,916 abstain; PA -0.13%, coverage 2.80%, answered accuracy 47.62%, p95 42 ms, 0 runtime errors. Cancellation-rate train answers: 2 correct/12 wrong among 14 answers, vs v8 12/2. This signals train-reference mismatch with the user-approved definition. Do not tune the convention to labels; investigate only with an explicit semantic basis.
- Next: resume safe remaining Playbook workstreams and focus generic coverage gaps; P7 L5 remains 0/30. Revisit acceptance thresholds honestly; no P3 reviewer work.
- Latest P7 matrix refresh: `docs/BUSINESS_COVERAGE_V9.md`, JSON `work/evaluation/business-coverage-matrix-train-v2-2026-11-16.json`. L1/L2/L4 30/30, L3/L5 0/30. Generator is replay-version-neutral; focused tests 4/4, full suite 133 run/130 passed/3 skips; see `tools/checkpoints/2026-11-16T1156+07-00_P7_MATRIX_REFRESH_COMPLETE.md`.
- P3 reviewer remains skipped; P3 is **NOT VERIFIED / NOT PASSED**. Docker out of scope. No Git operation, official checkout write, label-driven tuning, or source archive mutation.

## Earlier handoff — revenue/collection slice complete, 2026-11-16 11:03 GMT+7

Start with `tools/checkpoints/2026-11-16T1103+07-00_REVENUE_COLLECTION_CONTRACT_COMPLETE.md`; P7 profile/matrix evidence is in `tools/checkpoints/2026-11-16T1037+07-00_P7_BUSINESS_COVERAGE_MATRIX_COMPLETE.md`.

- Continue in `work/rehydrated-2026-11-15-P3/source`; isolated no-Git snapshot at base `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`. Do not touch official checkout or `sources/`.
- User explicitly skipped P3 reviewer. Do not conduct the reviewer workflow; P3 remains **NOT VERIFIED / NOT PASSED**, with no fabricated annotations or acceptance claim.
- Revenue defaults to after-discount order value. Explicit received/collected/paid requests use `collected_amount` from one payment-event table with a clear event date and amount. Insufficient/ambiguous evidence abstains. Do not substitute receivable totals, debt, or order-level paid snapshots for period receipts.
- Latest full suite: 127 run, 124 passed, 3 Git-dependent hygiene skips; exit 0. Real-data biz_127/biz_129 smoke selected `don_hang` for revenue and `thanh_toan` for collected money.
- v8 frozen train report: `work/evaluation/p6-train-replay-v8-revenue-collection-2026-11-16/evaluation_report.json`. Prediction hash equals v7; 47 correct, 37 wrong, 2,916 abstain; PA 0.33%, coverage 2.80%, answered accuracy 55.95%, p95 35 ms; no runtime errors. In-sample only; semantic code change did not improve score.
- Next: analyze only the already-frozen train evaluation for generic error categories; then address the highest-impact generalizable cause. Continue remaining Playbook phases without redoing verified P0–P2. P7 has L5 coverage 0/30, so it is not accepted.
- Docker remains out of scope. No commit, push, branch operation, ACL change, or official checkout write.

## Latest handoff — P7 matrix complete, 2026-11-16 10:37 GMT+7

Start with `tools/checkpoints/2026-11-16T1037+07-00_P7_BUSINESS_COVERAGE_MATRIX_COMPLETE.md` and the P7 pre-work checkpoint `tools/checkpoints/2026-11-16T1028+07-00_P7_BUSINESS_COVERAGE_PROFILE_START.md`.

- Active source copy: `work/rehydrated-2026-11-15-P3/source`; isolated and no `.git`; base `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`. Official checkout and `sources/` remain untouched.
- P3 reviewer was skipped as directed. P3 is still **NOT VERIFIED / NOT PASSED**; do not resume reviewer work or claim annotations/≥81% unless the user changes that instruction.
- P7 outputs: `docs/BUSINESS_COVERAGE.md`, `tools/build_business_coverage_matrix.py`, `tests/test_business_coverage.py`, and `work/evaluation/business-coverage-matrix-train-v1-2026-11-16.json`. The profile covers 30/30; L5 supported coverage is 0/30, so P7 is not accepted.
- Latest full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 119 run, 116 passed, 3 Git-dependent skips; exit 0.
- Continue with remaining Playbook workstreams. Do not repeat P0–P2 or work on Docker. Apply the revenue contract: after-discount order value is default revenue; explicit collected/paid questions use a distinct metric; abstain if data cannot establish the requested metric. Do not inspect or tune on Public Test labels/data.
- Next bounded task: inspect existing revenue selection/execution against that contract, add a generic regression-backed fix where evidence is sufficient, then checkpoint and update STATE, progress, handoff, and changelog.

## Latest work — continue from 10:04 GMT+7

User says skip P3 independent reviewer. Reviewer wait is skipped, but P3 stays **NOT VERIFIED / NOT PASSED**; do not invent annotations or ≥81% acceptance.

Current source changes: `src/datamate/understanding.py`, `src/datamate/metrics.py`, `src/datamate/rules.py`, `tests/test_understanding.py`, and `tests/test_pipeline.py`. Synthetic safety catches product names after `món`/`tiền bán`/`bán`, unsupported product/channel/payment breakdowns including `tại quầy`, natural-language revenue shares, misspelled/English best-sales-day questions, and average revenue. Explicit percent unit on scalar revenue yields internal `invalid_unit`. Failed-delivery and nonfinal statuses no longer contribute to revenue/quantity/ranking. Full suite: 116 run, 113 pass, 3 Git-only hygiene skips; focused pipeline 26/26, P3 understanding/pipeline/schema 48/48 before the last status-only change.

Latest current-code v7 report: `work/evaluation/p6-train-replay-v7-current-code-2026-11-16/evaluation_report.json`. It scored PA `0.00333` (47 correct, 37 wrong, 2,916 abstain), 2.80% coverage, 55.95% answered accuracy, 44.05% false-answer rate, p95 18 ms. It is in-sample, not independent acceptance, and remains far below playbook gates. There are 30 wrong numeric revenue answers (21 biz_127, 9 biz_129); their QuerySpecs have no filters/dimensions. The incomplete `p6-train-replay-v6-revenue-firewall-2026-11-16` remains preserved and unevaluated.

Historical note: the source/revenue contract and read-only line-item reconciliation were open at the time of the earlier P6 checkpoint. The user has since defined revenue, and the 11:03 checkpoint records the safe `collected_amount` slice. V8 now supersedes v7 for current-code train diagnostics; neither is an independent acceptance result.

## Latest action — P5 trace reason codes

Read `tools/checkpoints/2026-11-16T0817+07-00_P5_TRACE_REASON_CODES_COMPLETE.md`. Internal traces now record answered/abstained status, a stable reason code for abstentions, and the validated QuerySpec; submission records retain their existing organizer-facing schema. Focused API/verifier tests pass 20/20. Complete suite: 90 run, 87 passed, 3 Git-only hygiene skips.

P5 remains partial: missing-column/unit/join reasons are not yet mapped from structured execution failures, and verification gates/false-answer metrics are incomplete. Continue to P6 evaluation in a clean two-stage train replay: generate predictions from questions/data, hash and freeze them, then let an evaluator read train answer labels. Never feed labels into generation or tune on public questions. P3 remains **NOT VERIFIED / NOT PASSED** because the user chose to skip independent review; do not claim a P3 metric. P4/P5 are not accepted. P1/P2 were already verified; skip those checks. Docker is out of scope. No GitHub sync or official checkout write occurred.

## Latest action — P4 fail-closed executor slice

Continue in `work/rehydrated-2026-11-15-P3/source`, the isolated no-Git snapshot. Read `tools/checkpoints/2026-11-16T0811+07-00_P4_FAIL_CLOSED_EXECUTOR_COMPLETE.md`. Five regressions now cover ambiguous source tables, malformed date rows, invalid numeric values, no in-period rows, and conflicting order statuses. Focused suite: 11 passed; full suite: 85 run, 82 passed, 3 Git-only hygiene skips. P4 remains IN PROGRESS: safe joins, full operator contracts, business-specific rule evidence and supported-scope replay have not been completed.

The user explicitly said to skip the P3 independent-review wait and move ahead. Keep P3 status **NOT VERIFIED / NOT PASSED**; do not fabricate review annotations or metrics. P1/P2 remain complete by prior evidence, and those checks need not be repeated. Docker work is out of scope by user direction. Do not access answer labels or public/private test content for implementation. No GitHub sync or official checkout changes were made for this slice.

**Next exact action:** continue P4 with one bounded synthetic executor contract slice (row filters and aggregation null/zero semantics) or move to P5 stable abstention reason codes; keep unsupported operations fail-closed. Add focused tests, then full suite and checkpoint. Do not claim P4 acceptance until all P4 criteria have evidence.

## Latest action — GitHub source sync complete

The verified Source Release was synchronized to the real `feature/offline-core` branch. Commit `3b0bf3b66e9a78fa68fa29e8b97a23787bac2f0a`, parent `24cfa0908bd20f6e5b210366e956cae0d665b56e`. It contains 38 curated source, test, manifest, and release-documentation files. The target checkout ran 80/80 tests and passed `git diff --check`; post-push fetch confirmed origin and local HEAD match with a clean worktree. `main` was untouched. Public/Private data, JSONL outputs, logs, secrets, Docker image, and internal checkpoints were not pushed. Continue P3 from this isolated snapshot; current P3 is NOT PASSED and P4–P8 remain incomplete.

## Latest Docker build investigation — 2026-11-15

Read `work/docker-build-investigation-2026-11-15/DOCKER_BUILD_INVESTIGATION.md` for the Docker audit. The verified context is at `work/release-final-2026-11-15/output/DataMate_Docker_Test_Solution/build_context/`; it is not an image. No Docker build ran. The GitHub connection cannot inspect/create Codespaces or dispatch a workflow; local browser use is disabled. The source sync commit does not claim Docker success. To continue Docker work, obtain an authorized Linux/amd64 Docker host or Codespaces API access and establish a private/protected build destination. Then build the existing context, run network-disabled/repeatability/runtime checks, inspect platform and image size, export/import-test, and calculate archive hashes. Report each actual outcome; do not claim a pass in advance.

The broader Playbook remains active: P3 NOT PASSED; P4–P8 incomplete. Resume the next P3 evidence task in this isolated copy after the Docker access blocker is recorded. Preserve `sources/`, the original checkout, and the frozen Source Release/Public JSONL.

Continue in work/rehydrated-2026-11-15-P3/source (isolated no-Git copy); preserve sources/ and the official checkout. Official checkout recheck: feature/offline-core, 24cfa0908bd20f6e5b210366e956cae0d665b56e, clean. Public JSONL candidate is structurally ready but not uploaded: work/submission-build/public-test-submission-2026-11-15/submission.jsonl. It has 1,000 rows, 71.8% abstentions, no accuracy score, and must not be tuned against. Docker/Test Solution is blocked by absent local runtime and no CI workflows/runs. P3 remains NOT PASSED; P4–P8 remain active. Read tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_COMPLETE.md, then continue P3 with synthetic/separate train-development cases and honest evidence.

# Next session handoff

## RESUME HERE — 2026-11-16

Continue in `work/rehydrated-2026-11-15-P3/source`, the isolated no-Git copy based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`. This note supersedes older handoff text that says work must wait for a P3 reviewer: the user explicitly chose to skip that reviewer. Keep P3 **NOT VERIFIED / NOT PASSED** because no ≥81% acceptance evidence exists. P1/P2 were previously verified; do not repeat them. Docker is out of scope.

Latest code/test state: `metrics.py`, `rules.py`, `verify.py`, `main.py`, `tests/test_pipeline.py`, and `tests/test_api.py` were updated. Focused tests passed before the final trace additions; the full suite after all changes passed 108 run / 105 passed / 3 Git-only skips. P4/P5 remain partial. The latest frozen full 3,000-question v5 train diagnostic scored PA `-0.005` (45 correct, 60 wrong, 2,895 abstentions), coverage 3.5%, answered accuracy 42.86%, false-answer rate 57.14%; it is in-sample, not acceptance. See `work/evaluation/p6-train-replay-v5-full-2026-11-16/evaluation_report.json`. Earlier targeted v4 outputs are separately preserved for biz_101, biz_114, biz_116, biz_123, biz_125, biz_127, and biz_129.

**Next exact actions:**

1. Use the frozen v8 report to categorize the 37 remaining wrong answers generically. Do not add business IDs, question IDs, or answer values to inference. Train labels may only be opened by the evaluator after prediction freeze.
2. Continue the unfinished non-Docker Playbook workstreams and measure each against its actual acceptance criteria; P3 reviewer is skipped, but P3 is not passed.
3. Docker remains out of scope. After each bounded change, run relevant tests and the full suite, checkpoint, and update STATE/progress/handoff/changelog. Do not commit or push unless the user asks.

Read `tools/checkpoints/2026-11-16T0933+07-00_P5_EXECUTOR_REASON_CODES_COMPLETE.md` for exact hashes and replay identifiers, then read the P4 completion checkpoint for the source-selection tests and remaining revenue risks.

Updated: 2026-11-14 (GMT+7)

## Resume point

The active branch is `feature/offline-core`. This checkpoint started from `01d86f0168a7572d60896aae5125106934a99322`. The user requested that work stop and the current verified state be pushed before starting any more feature work.

The current change is **DF-1: scalar normalization and ingestion provenance**. It is a bounded partial Stage 2 checkpoint, not a claim that all Data Foundation requirements are complete.

## What changed

`src/datamate/normalization.py` now provides:

- `ParseStatus`: `ok`, `empty`, `invalid`, `ambiguous`.
- `ParseResult`: retains `raw`, normalized `value`, status, error text, and optional `SourceLocation`.
- `parse_decimal`: strict decimal/grouping parsing. It requires an explicit `decimal_separator` policy for a lone separator with exactly three following digits.
- `parse_date` and `parse_excel_date`: strict date parsing with explicit `day_first` and Excel `1900`/`1904` policies. Serial 60 fails because Excel's 1900 leap day is not a real calendar date.

`Table` received only optional fields at the end of its dataclass signature: `row_locations`, `date_system`, and `issues`. Existing executor tests construct the original four arguments and remain compatible.

`ingest.py` now records a `SourceLocation` for every retained CSV, XLSX, or SQLite row. CSV uses `csv.reader(..., strict=True)`, avoids its former `list(csv.reader(...))` copy, and raises `IngestionError` for malformed/ragged records. XLSX retains raw XML values, records workbook date system, and fails closed for uncertain headers rather than guessing a generic merge. SQLite remains opened with `mode=ro`.

`metrics.py` now calls the strict parser helpers. The helper for dates explicitly sets `day_first=True` because this is a Vietnamese-data policy; the general parser remains strict by default.

## Evidence and known limitations

- Baseline suite: `PYTHONPATH=src python -m unittest discover -s tests -v` passed 17 tests.
- Direct smoke checks passed for the documented decimal formats, ambiguous values, and Excel serials 60/61.
- No new durable parser/ingestion tests exist yet because the stop request arrived after implementation and before the planned test file work.
- The executor's use of `Table.rows` means rows still materialize. Do not change `rows` to an iterator without a migration plan and executor tests.
- XLSX multi-row headers currently return an explicit `IngestionError`; do not add an automatic generic header merger. Implement an explicit per-source/header policy in DF-2.
- The user supplied and the session visually reviewed `zac2026_DataMate_docker_guideline_final.pdf`. Key later work: write every result immediately, use integer `elapsed_ms`, package full offline inference/training assets, and target Linux/amd64 with network disabled. These Docker changes are not part of DF-1.

## Required next actions

1. Verify the pushed commit and clean working tree; do not trust this file alone.
2. Add synthetic unit/integration tests for the new normalizer and readers before widening scope.
3. Run all existing and new tests, inspect the diff, and update this handoff/progress file after the next checkpoint.
4. Resume Data Foundation only after the tests establish the current parser behavior. The next likely checkpoint is iterator/descriptor design plus configurable XLSX header policies.

## Commands

```powershell
Set-Location <repository-root>
git status --short --branch
git log -1 --oneline
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests -v
git diff --check
```

## Active handoff — 2026-11-15 P0 complete

Continue in `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`. This is a no-Git snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; do not initialize Git. At the successful P0 audit the official checkout was clean. Cached refs: feature `24cfa0908bd20f6e5b210366e956cae0d665b56e`, main `6be6997015a1d394ab8ed0eadd0141407ea1a1da`, feature +3/-0. No live fetch has been confirmed.

The prior external workcopy is stale (`01d86f0` base); do not overlay it wholesale. Read `tools/checkpoints/2026-11-15_P0_REPOSITORY_AUDIT.md` for audit, copy verification, tests, dataset inventory, and Git error. Current identity `ADMIN-PC\CodexSandboxOffline` differs from repo owner `ADMIN-PC\Admin`; Git blocks on dubious ownership. Do not add `safe.directory`, change ACLs, or elevate.

Snapshot baseline: 17 tests, 14 passed, 3 Git-dependent hygiene tests skipped because there is no `.git`. Earlier official checkout baseline: 17/17 passed. No application files changed yet. P1–P9 are not measured. Keep `sources/` read-only; do not use public data for tuning; generate predictions before loading train labels for evaluation.

Immediate next: add synthetic tests for normalization and CSV/XLSX/SQLite ingestion, establish failures, make narrow fixes, run focused and full suite, and update `STATE.md`, progress, handoff, plus an append-only checkpoint after each bounded change group. No Git actions are available or authorized in this snapshot.

## Active handoff — P1 complete for structural ingestion, 2026-11-15

Work in `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`, a no-Git snapshot of branch `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`. P0 base/ownership constraints remain in `tools/checkpoints/2026-11-15_P0_REPOSITORY_AUDIT.md`.

P1 structural load coverage: 30/30 train businesses, 128 files, 339 tables/sheets, 3,997,042 rows; 20/20 synthetic parser/ingestion tests pass. Full suite: 37 run, 34 passed, 3 Git-dependent hygiene tests skipped. The 81% structural ingestion gate is met at 100%. Semantic date/number quality and answer accuracy are still unmeasured. Evidence reports are ignored local files in `logs/`; data copies are in ignored `data/train/` and `data/train_utf8/`. Neither archive questions nor answers were extracted/read; no public data was used.

For exact failure analysis and file changes see `tools/checkpoints/2026-11-15_P1_NORMALIZATION_INGESTION.md`. New files: `tests/test_normalization.py`, `tests/test_ingest.py`, `tools/evaluate_ingestion.py`; modified: `src/datamate/normalization.py`, `src/datamate/ingest.py`, plus the three status docs and checkpoints.

That earlier handoff used a phase numbering different from the Master Implementation Playbook. Use the playbook numbering below for current work.

## Active handoff — 2026-11-15, playbook-aligned

Resume in `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`. The source snapshot is `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`, without `.git`. Do not initialize Git or modify `sources/`, official checkout, or `main`; preserve the ownership guard and no-commit/push/merge limits.

Read `tools/checkpoints/2026-11-15_P3_QUERY_UNDERSTANDING_PARTIAL.md` first. Current P3 is IN_PROGRESS: 2,843/3,000 train questions produce a QuerySpec (94.77% coverage), while only 1,620/3,000 compile to the current executable allowlist (54.0%). This is question coverage, not reviewed accuracy. Full suite: 48 run, 45 passed, 3 Git-only hygiene checks skipped. No answer labels/public-test content were read.

**P1 now verified at L1 structural profile scope.** See `tools/checkpoints/2026-11-15_P1_MULTI_BUSINESS_PROFILE_COMPLETE.md` and `docs/BUSINESS_COVERAGE_MATRIX.md`. Profiles cover 30/30 READMEs, 128 files, 339 tables/sheets, and 3,997,042 census rows. This does not imply L2+ business support.

**Next exact action:** implement the playbook P2 ingestion reconciliation: per-file accepted/rejected/intentionally skipped rows, typed errors, provenance, and a reproducible format matrix. Do not treat the existing whole-business row total as per-file reconciliation. After P2, return to P3: add a versioned QuerySpec schema and a business-held-out human-reviewed gold subset; report intent accuracy, slot exact match/F1, schema-validity, and ambiguity recall. Do not tune against the eventual holdout.

## Active handoff — P2 complete, resume P3 (2026-11-15)

Continue in `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`. This remains an isolated snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`, without `.git`. Do not initialize Git or touch `sources/`, original archives, the official checkout, or `main`; no commit/push/merge/reset/ACL changes.

P2 is **VERIFIED at structural reconciliation scope**. The final train-only census reported 30/30 businesses loaded, 128 files, 339 tables/sheets, 3,997,042 accepted rows, 0 rejected, 235 intentionally skipped, and 3,997,277 source records. Every table's scan completed and reconciled; no ingestion errors. Report: ignored `logs/train_ingestion_reconciliation.json`; evidence: `tools/checkpoints/2026-11-15_P2_INGESTION_RECONCILIATION_COMPLETE.md`.

Final code tests: `PYTHONPATH=src python -m unittest discover -s tests -v` — 52 run, 49 passed, 3 Git-dependent hygiene checks skipped because this copy has no `.git`; exit 0. Focused ingestion suite: 13/13 pass. Do not describe these as answer-accuracy results. No train answers or public-test data were read.

Next exact task: resume P3. Add a versioned JSON Schema for `QuerySpec`, then establish a business-held-out reviewed gold subset and a one-time evaluation reporting intent accuracy, slot exact match/F1, schema validity, and ambiguity recall. Keep holdout items out of tuning; no answer labels may be read until predictions are fixed. Existing 94.77% QuerySpec coverage and 54.0% executable coverage are diagnostics, not accuracy. Update `STATE.md`, progress, and this handoff after the next bounded unit.

## Active handoff — P3 schema complete; holdout below gate (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_QUERY_SCHEMA_HOLDOUT_PARTIAL.md` before resuming. P3 schema v1 exists and 2,843/2,843 generated train QuerySpecs validate. A first agent-reviewed holdout across six businesses scored 41/48 intent accuracy (85.42%), 23/48 core slot exact match (47.92%), 84.21% core slot micro-F1, and 45/45 schema-valid among interpreted items. There were no positive ambiguity cases, so ambiguity recall is not measurable. P3 is **not passed**.

Do not tune against or reuse `logs/queryspec_holdout_candidates.jsonl` / `logs/queryspec_holdout_gold.jsonl`; the holdout has been inspected. Use separate development examples, add synthetic ambiguity-recall coverage, improve time/dimension/intent slots, and then create a new held-out evaluation split before making further claims. Entity, unit, and filter accuracy are not currently scored. No train answers or public-test content were read.

The final full suite at this checkpoint: 55 run, 52 passed, 3 Git-dependent hygiene skips in the no-`.git` working copy; exit 0. Current work remains in the isolated snapshot at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no Git repository was initialized and no official checkout/main changes were made.

## Latest checkpoint — P3 development fixes, 2026-11-15

Read `tools/checkpoints/2026-11-15_P3_SLOT_DEVELOPMENT.md`. The parser was updated after the first holdout to recognize abbreviated revenue in average-order-value/best-sales-day queries and the “đắt nhất” ranking phrase. Focused tests pass 7/7; full suite is 56 run, 53 passed, 3 Git hygiene skips. Do not treat the earlier 48-question holdout score as a score for this updated parser; do not rerun/tune against that inspected set.

Next exact action: continue P3 using a separate development set and synthetic ambiguity tests; improve entity, unit, temporal and dimension extraction. Freeze a new reviewed business-held-out subset with positive ambiguity cases before evaluation. P3 remains **NOT PASSED**; entity/unit/filter accuracy is not measured. Continue in the isolated snapshot and leave the official checkout/main untouched.

## Latest checkpoint — relative-time alias (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_RELATIVE_ALIAS.md`. The `hnay` alias now resolves as the record's `as_of_date`; regression tests pass. Latest full suite: 57 run, 54 passed, 3 Git hygiene skips. No holdout replay was run after this change.

Next: continue P3 with separate development questions to add safe explicit unit/entity/dimension handling and positive ambiguity tests. Keep `biz_107`–`biz_112` holdout frozen; create a new held-out set only after parser changes are frozen. P3 is still below the slot exact-match gate.

## Latest checkpoint — explicit units (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_UNIT_EXTRACTION.md`. QuerySpec now extracts explicitly stated units and leaves absent units null. Focused schema suite 4/4; understanding/time 13/13; full suite 58 run, 55 pass, 3 Git-only skips. Prior holdout was not rerun.

Next: conservative entity-slot extraction with null/ambiguous cases on synthetic/dev examples. Preserve the inspected `biz_107`–`biz_112` holdout; create a new held-out review with positive ambiguity cases after parser freeze. No answers/public labels; no Git or official checkout actions.

## Latest checkpoint — entity slot, 2026-11-15

Read `tools/checkpoints/2026-11-15_P3_ENTITY_SLOT.md`. Entity extraction is grounded only in an optional alias catalog: unique match returns canonical entity; multiple matches abstain and flag `entity_unresolved`; absent catalog leaves entity null. Focused schema tests 5/5; full suite 59 run, 56 pass, 3 Git-only skips. No old holdout replay.

Next: implement and test ambiguity precision/recall/F1 on synthetic positive/negative cases, then prepare a fresh business-held-out gold set with positive ambiguity cases after parser freeze. P3 is NOT PASSED; don't tune on prior inspected holdout or read answer/public labels.

## Latest checkpoint — ambiguity evaluator (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_AMBIGUITY_METRICS.md`. Evaluator reports ambiguity TP/FP/FN and precision/recall/F1, with null for unmeasurable denominators. Synthetic tests 2/2; full suite 61 run, 58 pass, 3 Git-only skips. No old holdout replay.

Next: prepare a fresh business-held-out question-only candidate split with positive/negative ambiguity cases, annotate and freeze it after parser freeze, then run evaluator once. The old `biz_107`–`biz_112` holdout remains prohibited for tuning/rerun. P3 remains NOT PASSED.

## Latest handoff — P3-HOLDOUT-2 diagnostic (2026-11-15)

Continue from tools/checkpoints/2026-11-15_P3_HOLDOUT2_DIAGNOSTIC.md and verify its archive manifest before edits. Current isolated copy is C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3, a no-Git snapshot of feature/offline-core at base 24cfa0908bd20f6e5b210366e956cae0d665b56e.

Latest parser hash: AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C. Do not tune against P3-HOLDOUT-2. Its diagnostic score was intent 44/50 (88%), core slot exact 40/50 (80%, below gate), slot micro-F1 91.84%, schema validity 48/48 interpreted (100%), and ambiguity precision/recall/F1 33.33%/50%/40% from two subjective positives. Per-business misses include biz_115, biz_117, and biz_118. Gold was single-agent annotated, not independent; prior query-only train diagnostics may have included these questions. Entity/unit/filter and answer correctness are not measured.

The candidate and gold JSONL, annotation script, full error details, and metrics JSON are in ignored local logs/ only; do not copy them into a source archive because they contain training-question identifiers/content. No answer labels or public-test files were opened. The complete suite passed 61 tests: 58 passed, 3 Git-dependent skips because there is no .git; exit 0.

Next exact unit: develop general P3 parser improvements using new synthetic or separate development cases outside biz_107–biz_118 and biz_125–biz_130, with one focused failing test first. Do not inspect/use the frozen holdout examples to select a rule. Re-run focused and full tests, then checkpoint. Any future accuracy claim requires a newly frozen, independently reviewed holdout with adequate positive ambiguity cases and a full slot metric.
## Archive verification — P3-HOLDOUT-2 diagnostic

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_holdout2-diagnostic.zip
- Archive SHA-256: e30fac0110e145d6e561974433c1a72527c0a1a969357365615024ff3b623b13 (external sidecar: work\checkpoints\2026-11-15_P3_HOLDOUT2_DIAGNOSTIC\archive.sha256; kept outside the ZIP to avoid self-reference).
- Archive entries: 76; internal manifest entries: 75; every SHA-256 verified; ZIP integrity PASS.
- Excluded: local logs, question candidates, gold annotations, train/public data, and generated smoke copies.
- Extracted smoke: work\rehydrated-smoke-P3-holdout2; 61 tests run, 58 passed, 3 Git-dependent skips; exit 0.
- Full post-build evidence: work\checkpoints\2026-11-15_P3_HOLDOUT2_DIAGNOSTIC\POST_BUILD_VERIFICATION.md.

## Latest handoff — P3 evaluator coverage expanded (2026-11-15)

Read tools/checkpoints/2026-11-15_P3_EVALUATOR_FULL_SLOTS.md. The evaluator now scores nine semantic slots including entity, unit, and filters, and reports time/dimensions exact separately. Synthetic evaluator tests pass 4/4; full suite is 63 run, 60 passed, 3 Git-only skips, exit 0. Parser hash is unchanged at AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C.

Do not rerun or tune P3-HOLDOUT-2. Its 80% slot exact result uses the earlier six-slot evaluator and is diagnostic only; the new nine-slot measure needs a new, independently reviewed holdout with all gold fields, sufficient positive ambiguity cases, and per-business floors. No train answer or public-test labels were accessed.

Next exact unit: continue P3 with isolated synthetic tests or a genuinely separate development set; record one failing case before a narrow parser change. Keep all previously inspected holdouts frozen. Current work remains a no-Git snapshot of feature/offline-core base 24cfa0908bd20f6e5b210366e956cae0d665b56e.
## P3 full-slot evaluator checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_full-slot-evaluator.zip
- SHA-256: 9b68864ee4eb3ccf25482ff0ba681daff711186c3143d0c51888196890325416; sidecar: work\checkpoints\2026-11-15_P3_EVALUATOR_FULL_SLOTS\archive.sha256.
- Archive contains 77 entries; 76 manifest entries verified, ZIP integrity PASS. No train/public data or generated logs are included.
- Extracted smoke: work\rehydrated-smoke-P3-full-slot-evaluator; 63 tests run, 60 passed, 3 Git-dependent skips; exit 0.
- Post-build verification and external manifest: work\checkpoints\2026-11-15_P3_EVALUATOR_FULL_SLOTS\POST_BUILD_VERIFICATION.md and post_build_manifest.sha256.

## Latest handoff — P3 evaluator input validation (2026-11-15)

Read tools/checkpoints/2026-11-15_P3_EVALUATOR_INPUT_VALIDATION.md. The full-slot evaluator now validates required candidate/gold fields and fails early with the missing slot names. Focused tests pass 5/5; full suite 64 run, 61 passed, 3 Git-only skips; exit 0. Evaluator SHA: D5B3BD4F25483523230FEE3AFFFCFB2C813EF264EF39200A3F6969A5A481F193. Parser is unchanged.

Do not rerun or tune P3-HOLDOUT-2; it was evaluated with the earlier six-slot tool and single-agent annotations. New full-slot metrics require a fresh independently reviewed gold set. No train answer/public labels were accessed. Working copy remains a no-Git snapshot of feature/offline-core base 24cfa0908bd20f6e5b210366e956cae0d665b56e.

Next exact unit: continue with one parser or evaluation behavior backed by synthetic/separate development examples, then run focused/full tests and create a new checkpoint archive.
## P3 evaluator input-validation checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_evaluator-input-validation.zip
- SHA-256: d7ed0bce2dfce1ff86fadcb3d4ea3767d7d6765409a8fabe0170c5d78e022586; sidecar: work\checkpoints\2026-11-15_P3_EVALUATOR_INPUT_VALIDATION\archive.sha256.
- 77 archive entries; all 76 internal manifest hashes verified; ZIP integrity PASS. No data or generated logs included.
- Extracted smoke: work\rehydrated-smoke-P3-evaluator-input-validation; 64 tests run, 61 passed, 3 Git-dependent skips; exit 0.
- Full verification: work\checkpoints\2026-11-15_P3_EVALUATOR_INPUT_VALIDATION\POST_BUILD_VERIFICATION.md; external manifest PASS.

## Latest handoff — P3 year-to-date comparison scope (2026-11-15)

Read tools/checkpoints/2026-11-15_P3_YTD_COMPARISON.md. The parser now represents an explicit year-to-date comparison against the same elapsed period last year, anchored to record as_of_date and clamped for leap dates. Two synthetic regressions failed before the fix and pass afterward. Timeparse 8/8, understanding 7/7, full suite 66 run / 63 passed / 3 Git-only skips, exit 0.

Current timeparse SHA-256 is E5C7732AA5CABDB525603D00AD6509DDBD5075B21A1847D2C2B6D2DF379252A7. P3-HOLDOUT-2 was not rerun and must not be used for tuning; its earlier metrics refer to the previous parser/evaluator. No answer/public labels were used.

Next exact unit: continue P3 on a separate synthetic or development case; freeze the parser before collecting any new independently reviewed full-slot holdout. Keep the no-Git snapshot and original sources safe.
## P3 year-to-date comparison checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_ytd-comparison.zip
- SHA-256: 42db858192e687608e2a61fae53a63ef7eab0149d388618d6c207bcaf9cbcad4; sidecar: work\checkpoints\2026-11-15_P3_YTD_COMPARISON\archive.sha256.
- Archive entries: 78; internal manifest entries: 77; all hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extracted smoke: work\rehydrated-smoke-P3-ytd-comparison; 66 tests run, 63 passed, 3 Git-dependent skips; exit 0.
- Post-build verification: work\checkpoints\2026-11-15_P3_YTD_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

## Latest handoff — P3 entity-catalog evaluation support (2026-11-15)

Read tools/checkpoints/2026-11-15_P3_ENTITY_CATALOG_EVALUATOR.md. The evaluator now accepts optional entity catalogs per candidate and passes them to RulePlanner, allowing full-slot scoring of unique aliases and ambiguous matches. Synthetic tests 7/7; full suite 68 run, 65 passed, 3 Git-only skips, exit 0. No parser change and no holdout replay.

Do not use P3-HOLDOUT-2 for tuning or run it with changed evaluator/parser. It lacks catalogs and its gold is single-agent. A future full-slot benchmark needs fresh, independently reviewed labels and business catalogs. No answer/public labels were accessed.
Next: continue P3 with separate synthetic/development coverage, then freeze parser and collect the independent benchmark. Working copy remains NO_GIT at base 24cfa0908bd20f6e5b210366e956cae0d665b56e.
## P3 entity-catalog evaluator checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_entity-catalog-evaluator.zip
- SHA-256: e71fa47f6a6888feec7be797360473c56d516522905c760b9d50f984afa32a5b; sidecar: work\checkpoints\2026-11-15_P3_ENTITY_CATALOG_EVALUATOR\archive.sha256.
- Archive entries: 79; 78 internal manifest hashes verified; ZIP integrity PASS; no train/public data or generated logs.
- Extracted smoke: work\rehydrated-smoke-P3-entity-catalog-evaluator; 68 tests run, 65 passed, 3 Git-dependent skips; exit 0.
- Post-build evidence: work\checkpoints\2026-11-15_P3_ENTITY_CATALOG_EVALUATOR\POST_BUILD_VERIFICATION.md; external manifest PASS.

## Latest handoff — P3 completed-month comparison (2026-11-15)

Read tools/checkpoints/2026-11-15_P3_MONTH_COMPARISON.md. Time parsing now compares the previous complete month with the month before it, including year rollover; it rejects incomplete comparisons. Synthetic tests failed before the fix, including a transient over-escaped-regex implementation error that was corrected. Focused timeparse 11/11; full suite 71 run, 68 passed, 3 Git-only skips; exit 0.

Current timeparse hash: EC2343B7CA8520AE5DE50FD2EC2A0856E3850FFE7E940F04CEAE7DA234A77925. No holdout replay or train/public labels. Next: continue P3 using synthetic/separate dev cases, then freeze parser and obtain independent full-slot review. Do not use P3-HOLDOUT-2 for tuning. Working copy remains no-Git at base 24cfa0908bd20f6e5b210366e956cae0d665b56e.
## P3 completed-month checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_month-comparison.zip
- SHA-256: c2bef2c81bbc1155d73de1e498dcc44eda872a24d23429fa0b0d556f7eab2805; sidecar: work\checkpoints\2026-11-15_P3_MONTH_COMPARISON\archive.sha256.
- Archive entries: 80; 79 internal manifest hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extract smoke: work\rehydrated-smoke-P3-month-comparison; 71 tests run, 68 passed, 3 Git-dependent skips; exit 0.
- Full verification: work\checkpoints\2026-11-15_P3_MONTH_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

## Latest handoff — P3 completed-quarter comparison (2026-11-15)

Read tools/checkpoints/2026-11-15_P3_QUARTER_COMPARISON.md. Time parsing now compares the last full quarter with the quarter before it, including Q1-to-prior-year rollover. Incomplete comparisons abstain. Synthetic tests failed before implementation; focused timeparse 14/14; full suite 74 run, 71 passed, 3 Git-only skips; exit 0.

Current timeparse SHA-256: E5588BAD3222C85C8BFB57A8459B04A260488708239E96BE93E1F5CAF9F9CB26. No holdout replay or answer/public labels. Continue P3 only with synthetic/separate development cases, then freeze parser for a new independently reviewed full-slot holdout. P3 remains NOT PASSED.
## P3 completed-quarter checkpoint archive

- Archive: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\archives\DataMate_checkpoint_2026-11-15_P3_quarter-comparison.zip
- SHA-256: 8ff6ff3e64d2a3b49050fd882f4f65e94bf8020dd2b1791f090a85db4479c056; sidecar: work\checkpoints\2026-11-15_P3_QUARTER_COMPARISON\archive.sha256.
- Archive entries: 81; all 80 internal manifest hashes verified; ZIP integrity PASS; no train/public data or logs.
- Extract smoke: work\rehydrated-smoke-P3-quarter-comparison; 74 tests run, 71 passed, 3 Git-dependent skips; exit 0.
- Post-build verification: work\checkpoints\2026-11-15_P3_QUARTER_COMPARISON\POST_BUILD_VERIFICATION.md; external manifest PASS.

## Latest handoff — P3 year-to-date scope precedence (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_YTD_SCOPE_PRECEDENCE.md`. A question-only development case exposed that “năm nay, từ đầu năm đến hết hôm nay” was parsed as just the endpoint date. Added a synthetic regression (red before fix), then moved YTD resolution before relative-day endpoint handling. Focused timeparse tests 15/15; complete suite 75 run, 72 passed, 3 Git-dependent skips; exit 0.

Latest hashes: `src/datamate/timeparse.py` EA890116E57AFB5885DCB7831ACABB2B96B4A943D03BF0E7AF5BC465AD8FD2C0; `tests/test_timeparse.py` AD49A26D70497F58DDCE3BE4B30FCE0FFF594FD53A2B053694EC37944F9B3BFB. The question-only development set, candidates, and annotations are excluded from source archives. No holdout was rerun, no answer labels/public-test content was read, and no Git operation occurred. P3 remains NOT PASSED; no 81% claim. Continue with isolated synthetic/question-only development work, then freeze code and arrange an independent full-slot holdout before reporting acceptance.

## Latest handoff — P3 requested-unit precedence (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_REQUESTED_UNIT_PRECEDENCE.md`. A synthetic product-price question exposed that the unit extractor selected `viên` from packaging text instead of the requested `tuýp`. The focused regression failed before the fix. Added the `tuýp` alias and priority for explicit “một/mỗi/từng <unit>” expressions. Query schema tests 6/6; full suite 76 run, 73 passed, 3 Git-only skips; exit 0. P3 remains NOT PASSED and no 81% claim is made.

## Latest handoff — P3 percent revenue-share cue (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_REVENUE_SHARE_CUE.md`. A synthetic question containing `%`, a category subject, revenue, and “chiếm” was wrongly classified as total revenue. Added the narrow contribution-cue condition; the regression failed before the fix. Focused understanding tests 8/8; full suite 77 run, 74 passed, 3 Git-only skips; exit 0. P3 remains NOT PASSED; no 81% claim. Continue using synthetic or separate question-only development and keep all reviewed holdouts frozen.

## Latest handoff — P3 supplier-ranking QuerySpec (2026-11-15)

Read `tools/checkpoints/2026-11-15_P3_SUPPLIER_RANKING_SPEC.md`. Supplier purchase ranking was classified as sales ranking. It now yields a structured `supplier_ranking` QuerySpec with supplier dimension and purchase amount metric, while remaining non-executable because purchase sources are not yet verified in the engine. Understanding tests 9/9; full suite 78 run, 75 passed, 3 Git-only skips; exit 0. Do not enable supplier ranking execution without validating its source schema. P3 remains NOT PASSED.


## Current handoff — P1/P2 confirmed complete; resume P3 (2026-11-15)

User confirmed P1 and P2 are complete. P1 is complete at L1 structural profile scope; the P7 business-support coverage metric remains separate. P2 was re-audited against the current ingestion evaluator: 30/30 businesses, 128 files, 339/339 tables/sheets reconciled; 3,997,277 source rows = 3,997,042 accepted + 0 rejected + 235 skipped; zero failures. The audit read README/business data only, not train answers or public test. Detailed checkpoint: `tools/checkpoints/2026-11-15_P2_INGESTION_REAUDIT.md`; ignored report SHA-256 `6AE9AC53F6BF2CF932DEC9BE71976A54B34CCA7B45E6DFB451E8DB097DCD6D09`.

Continue P3 in `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`, a no-Git snapshot of `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`. Current code has four regression-backed QuerySpec/time-parsing improvements; full suite 78 run / 75 pass / 3 Git-only skips. P3 is not passed: a current independently reviewed full-slot holdout (including ambiguity positives) is required before any ≥81% claim. Keep all inspected holdouts frozen and do not read answer labels or public-test content. Update `STATE.md`, progress, handoff, and checkpoint after each bounded work unit. P4–P8 remain in order after P3 acceptance; do not claim them complete.


## Latest handoff — current writable project and P3 review gate (2026-11-15)

Current writable project root: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af990f97d408191a5847ca24785860f`. Continue from `work\rehydrated-2026-11-15-P3\source`; its snapshot corresponds to `feature/offline-core` base `24cfa0908bd20f6e5b210366e956cae0d665b56e` and contains no `.git`. Do not use the stale sibling-workspace path above as the active location.

User confirmed P1/P2 complete. P1 is verified at L1 structural profile scope. P2 structural reconciliation evidence: 30/30 businesses; 128 files; 339/339 tables/sheets; 3,997,277 source rows = 3,997,042 accepted + 0 rejected + 235 intentionally skipped; zero failures.

P3 remains IN_PROGRESS / NOT PASSED. Blind packet is ready at `work\reviews\P3_HOLDOUT3`: 72 primary items, 12 each from `biz_101`–`biz_106`, and 4 disjoint no-explicit-time challenge items. Only question metadata/text from `sources\train.zip::train/questions.jsonl` was read; no train answers or public-test data were opened. The parser has not been run on these candidates. Challenge sample size is too small for a stable ambiguity-recall claim. Freeze manifest SHA-256: `c8fb19220e50fe7348b8de3308a5c90e3f9a06da24dff51038b5637dc17f9621`.

**Required next action:** have an independent reviewer complete `annotation_template.csv` and `entity_catalog_template.csv`, then adjudicate disagreements. Validate the frozen gold against all required fields and run the evaluator once. Do not tune against this packet. P4–P8 must follow only after P3 meets the rubric. Detailed checkpoint: `tools/checkpoints/2026-11-15_P3_BLIND_REVIEW_PACKET.md`.

Latest test evidence before this handoff update: 78 total, 75 passed, 3 Git-dependent hygiene skips, exit 0. Rerun the full suite after documentation changes. No code changes or Git actions were made in this work item; the official checkout and `main` remain untouched.

Final verification for this checkpoint: full unittest suite exited 0 (78 run, 75 passed, 3 Git-dependent skips). Review packet integrity passed (72 primary + 4 challenge, no overlap, all candidate hashes match). The only blocker is independent annotation/adjudication; after it arrives, validate the gold and run P3 evaluation once.
# Urgent submission preflight handoff — 2026-11-15

Resume from this section. The user's priority is a valid DataMate submission; do not spend the single daily Test Solution slot on an unverified build. Full audit, evidence, and commands are in `tools/checkpoints/2026-11-15_SUBMISSION_PREFLIGHT.md`.

- Writable source snapshot: `work/rehydrated-2026-11-15-P3/source`; no `.git`. Official checkout remains untouched at branch `feature/offline-core`, commit `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P1/P2 were user-confirmed complete. Dataset reconciliation is 30 businesses / 128 files / 339 tables and sheets / 3,997,277 total rows, with 0 failed files.
- Three runtime blockers were fixed: incremental output flush, organizer-compliant per-question logs, and streaming question input. Full tests: 80 run, 77 passed, 3 Git-only skips. Train-only 12-question smoke passed twice and was deterministic. This is not an accuracy metric.
- **NO-GO** because this machine has no Docker-family CLI and `wsl.exe --status` exits 1. Docker build, GPU compatibility, and offline container inference are not verified. No image/tar.gz/MD5/Drive upload/portal submission exists; no daily slot was consumed.
- Final build context candidate is `work/submission-build/context-final-verified-2026-11-15`. All included-file checksums are listed in its manifest; exact aggregate size and manifest SHA-256 are in `work/submission-build/FINAL_ARTIFACT_RECORD.md`. It is a build context, not a submission artifact.
- Use official Docker guide `sources/zac2026_DataMate_docker_guideline_final.pdf`; build and run on a machine with Docker and supported GPUs. Recheck official portal rules and deadline before action. Official Test Solution is a technical smoke check, not an official score; scored final submission is separate.
- The source is isolated from the target Git checkout. Do not claim synchronization. Do not open answer labels or public/private test data. P3 independent review remains **NOT COMPLETED / NOT PASSED**, and no reviewer annotations exist.

# Current handoff — public submission JSONL generation (2026-11-15)

Resume from `tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_START.md`. The user supplied portal screenshots showing Public Submissions JSONL and separate Docker Test Solution tabs. A one-pass Public Test inference output is being prepared, not uploaded. Do not inspect public answers (none are present), tune or rerun against public questions, or claim an accuracy score. Keep all source input, logs, and outputs separate from `sources/` and the Docker build context. Official repository remains clean at `feature/offline-core` / `24cfa0908bd20f6e5b210366e956cae0d665b56e`; do not synchronize or commit without authorization. Docker/Test Solution remains unverified because no Docker runtime is available.
# Current handoff — continue Playbook after Public JSONL preparation

The Public Submissions JSONL candidate is prepared and structurally verified, but not uploaded. Read tools/checkpoints/2026-11-15_PUBLIC_SUBMISSION_GENERATION_COMPLETE.md.

- Upload candidate, only after user confirms portal action: work/submission-build/public-test-submission-2026-11-15/submission.jsonl. 1,000 records; 44,806 bytes; SHA-256 0de940823521e386477efeb76c26d6533e61cabf1977b5c0d9cbb6fd0d61e112; MD5 85b4acc0abf681c8b5a6a6a6812910ab.
- The candidate passes format/runtime validation but has 71.8% abstentions. No accuracy/PA is known. Do not tune on public questions or this output.
- Test Solution is a separate Docker image upload. No Docker runtime is available; image, offline run, GPU test, tarball, MD5, and Test Solution are not ready. Portal's model dropdown lacks an obvious no-model/rule-engine selection.
- Official checkout is still clean at feature/offline-core / 24cfa0908bd20f6e5b210366e956cae0d665b56e; do not sync or mutate it.
- Continue the active Playbook from P3. P3 remains NOT PASSED pending honest reviewed full-slot/ambiguity evidence; P4–P8 must not be marked complete. Work only in work/rehydrated-2026-11-15-P3/source, preserve sources/, and checkpoint every bounded unit.


## Resume — 2026-11-17 — v26

- Read `docs/PROGRESS_REPORT_2026-11-17.md` and `tools/checkpoints/2026-11-17T0821+07-00_P6_V26_REPORT_SYNC.md` first.
- Current suite: 189 run, 186 passed, 3 Git-only skips; focused pipeline 69/69 passed.
- Latest frozen train v26: 237 correct / 6 wrong / 2,757 abstain out of 3,000; answered accuracy 97.53%, coverage 8.10%, PA 7.70%, runtime errors 0. This is in-sample only.
- Six remaining train errors: 3 sales-ranking false answers and 3 cancellation-rate label/rulebook conflicts. Keep rulebook semantics; investigate rankings with generic unit/schema evidence and regressions.
- Do not tune on public questions or open public/private labels. Current source-root `public_submission.jsonl` is stale and not v26. No v26 public artifact is confirmed.
- Replay only to a new directory and validate freeze before evaluator label access. No source changes were made by this report sync.


## Handoff — 2026-11-19 multi-bundle vertical slice

- Active repository: `pl2n/DataMate`; branch: `feature/multi-bundle-query`. Upstream remains untouched.
- Read `docs/MULTI_BUNDLE_QUERY.md`, `docs/DATA_INGESTION.md`, and `tools/checkpoints/2026-11-19_MULTI_BUNDLE_VERTICAL_SLICE.md`.
- First supported composite: same-period side-by-side revenue + collected amount. It reuses `Executor.execute_with_reason` and `verify_with_reason` for each component.
- Any required component failure abstains the entire composite. Arithmetic differences, cross-period comparisons, arbitrary conjunction splitting, and dynamic bundle discovery remain unsupported.
- Inspect GitHub Actions before treating the work as verified. Do not claim tests passed until the run is green.


### CI follow-up — 2026-11-19

- Workflow run for implementation commit `77dbd90e204356211c70a2cf56f7f52249cde01a`: 197 tests executed; functional/composite tests passed, but the job failed in two pre-existing hygiene assertions against tracked `CODEX PROGRESS` (oversized file and secret-like regex hit).
- This file was not changed. Do not suppress the secret scan or remove the artifact without maintainer review. Resolve the archive policy and rerun all tests.
- Run URL: https://github.com/pl2n/DataMate/actions/runs/44541834717


## Resume — 2026-11-19 — XLSX grouped-header support

- Read `tools/checkpoints/2026-11-19_EXCEL_GROUPED_HEADERS.md`.
- Branch: `feature/multi-bundle-query`; implementation commits: `add80f2` and `477a544`.
- Excel ingestion now recognizes only a narrow, explicit two-row merged-group header pattern; raw header rows and source row numbers are preserved and included in `profile()`.
- CI run `44545450222`: 199 tests; new tests pass; 197 pass overall and 2 pre-existing hygiene failures remain for `CODEX PROGRESS`. Do not claim the full workflow is green.
- Next: consider adding an explicit structural-analysis result object for ambiguous header candidates before broadening beyond this conservative pattern. Do not infer arbitrary multi-row headers.


## Resume — 2026-11-19 — semantic column mapping

- Read `tools/checkpoints/2026-11-19_SEMANTIC_COLUMN_MAPPING.md`.
- New `semantic.py` maps only explicit exact aliases and a small group-plus-leaf allowlist. It is metadata-only; no joins or metric execution are enabled.
- Generic labels and collisions fail closed. Extend aliases only with source-backed evidence and synthetic regressions.


### CI result — semantic mapping

- Run `44546168818` executed 203 tests. The new semantic tests passed; 201 passed overall.
- Two existing hygiene checks still fail on `CODEX PROGRESS` (size and secret-like regex). No code/test failure was reported outside those checks.
- Run: https://github.com/pl2n/DataMate/actions/runs/44546168818


## Resume — 2026-11-19 — relationship validation

- Read `tools/checkpoints/2026-11-19_RELATIONSHIP_VALIDATION.md`.
- `relationships.py` compares only exact values under shared, unambiguous canonical key fields. It reports cardinality and evidence but never performs joins.
- Preserve leading zeroes. Do not relax full child-key coverage or unique-parent requirements without explicit source evidence and regressions.


### CI result — relationship validation

- Run `44546976679` executed 210 tests; all new relationship tests passed and 208 tests passed overall.
- Two existing repository-hygiene checks still fail on `CODEX PROGRESS`. Do not bypass them.
- Run: https://github.com/pl2n/DataMate/actions/runs/44546976679


## Resume — 2026-11-19 — bundle registry

- Read `tools/checkpoints/2026-11-19_BUNDLE_REGISTRY.md`.
- `BundleRegistry` is an explicit allowlist. It currently contains only revenue and collected-amount definitions.
- `CompositePlanner` resolves its current two metrics through the registry. Do not claim arbitrary multi-bundle question parsing is implemented.


### CI result — bundle registry

- Run `44547696247` executed 216 tests; all new bundle-registry and composite tests passed, 214 passed overall.
- Two pre-existing hygiene checks still fail on `CODEX PROGRESS`. Preserve the checks and resolve the file policy separately.
- Run: https://github.com/pl2n/DataMate/actions/runs/44547696247


### CI result — bundle registry

- Latest registry/composite test run `44547696247`: 216 tests; 214 passed, including all new tests.
- Only the two pre-existing `CODEX PROGRESS` hygiene checks fail.


## Resume — 2026-11-19 — business schema catalog

- Read `tools/checkpoints/2026-11-19_SCHEMA_CATALOG.md`.
- `build_schema_catalog()` composes semantic column mappings and relationship evidence. It is metadata-only and does not join data.
- Use both table name and source file to resolve duplicate table names.


### CI result — schema catalog

- Run `44548265235` executed 219 tests; all schema catalog tests passed and 217 tests passed overall.
- Two pre-existing `CODEX PROGRESS` hygiene failures remain.
- Run: https://github.com/pl2n/DataMate/actions/runs/44548265235


## Resume — 2026-11-19 — requirement extraction

- Read `tools/checkpoints/2026-11-19_REQUIREMENT_EXTRACTION.md`.
- `RequirementExtractor` translates the existing `financial_metric_comparison` QuerySpec into two independent metric requirements.
- It does not split arbitrary conjunctions or enable other metric combinations yet.


### CI result — requirement extraction

- A stale annotation found by the first run was corrected in `45330bc`.
- Follow-up run `44548881088`: 222 tests, no code/test errors; 220 passed. Only two existing `CODEX PROGRESS` hygiene checks fail.
- Run: https://github.com/pl2n/DataMate/actions/runs/44548881088


## Resume — 2026-11-19 — versioned requirement schema

- Read `tools/checkpoints/2026-11-19_REQUIREMENT_SCHEMA.md`.
- Requirement extraction payloads are versioned at `1.0.0` and validated before composite plan compilation.
- Preserve unique requirement IDs/metrics and status/reason invariants.


### CI result — requirement schema

- Run `44549585604`: 226 tests, no code/test errors; 224 passed. Only the two pre-existing `CODEX PROGRESS` hygiene checks fail.
- Run: https://github.com/pl2n/DataMate/actions/runs/44549585604

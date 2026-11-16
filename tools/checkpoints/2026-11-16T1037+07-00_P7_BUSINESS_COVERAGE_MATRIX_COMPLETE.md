# P7 business coverage matrix — complete evidence slice

- Completed: 2026-11-16 10:37 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 independent reviewer was skipped at the user's direction. P3 remains **NOT VERIFIED / NOT PASSED**; no reviewer annotations or acceptance score are claimed.
- P7: structural profile and evidence matrix are complete; P7 itself remains **IN PROGRESS / NOT ACCEPTED** because L5 support is 0/30, below the 81% target.

## Inputs and provenance

- Train data directory: `work/evaluation/train-inputs-2026-11-16/data`.
- Structural profiler command: `PYTHONPATH=src python tools/profile_businesses.py ..\..\evaluation\train-inputs-2026-11-16\data --output ..\..\evaluation\business-profiles-train-v1-2026-11-16.json` — exit 0; 30 businesses, 30 READMEs, 128 files, 339 tables/sheets, no profile errors, zero questions passed to the profiler, and no ingestion census supplied.
- Profile: `work/evaluation/business-profiles-train-v1-2026-11-16.json`, SHA-256 `7565bdfecdb8614a0da156c9d5df4fb1ed42148027d7880d8dabcee4ad6dd910`.
- Frozen replay report: `work/evaluation/p6-train-replay-v7-current-code-2026-11-16/evaluation_report.json`, SHA-256 `1c127129b9469ec056dd3684bce67cec945650973774466a4b9f78f9626c43e0`.
- The profile generator was run with data directories only and no question/answer path. It stores README prose and structural metadata, not row/cell values. The derived matrix omits README prose and question diagnostics. No Public Test data or labels were read.
- The v7 report is a frozen train-only replay whose evaluator scored labels after prediction freeze. It is in-sample diagnostic evidence, not independent acceptance or generalization performance.

## Changes and results

- Added `tools/build_business_coverage_matrix.py` to validate matching business sets, calculate per-business replay metrics/macros, and emit JSON plus Markdown. Header/date/amount/unit/ID groups are name-based hints; candidate join header names are not approved joins.
- Added `tests/test_business_coverage.py` (3 tests): conservative level claims; omission of README prose/question text from derived output; and strict equality of profile/replay business sets.
- Generated `work/evaluation/business-coverage-matrix-train-v1-2026-11-16.json` and `docs/BUSINESS_COVERAGE.md`.
- L0 data present: 30/30; L1 structurally profiled: 30/30 (100%); L2 appeared in replay with no runtime errors: 30/30, but this is **not** a row-census reconciliation; L3 with mapped business-intent tests: 0/30; L4 with frozen train replay metrics: 30/30; L5 release-supported: 0/30 (0%).
- v7 overall replay: 3,000 questions; 47 correct, 37 wrong, 2,916 abstained; PA 0.003333 (0.33%); question-weighted answer coverage 0.028 (2.80%); answered accuracy 0.559524 (55.95%); p95 18 ms; runtime error map empty. 70/70 unanswerable cases were correctly abstained (recorded in the original report).
- Macro across 30 businesses: PA 0.010537 (1.05%); answer coverage 0.035847 (3.58%); macro answered accuracy 0.553045 (55.30%) across 8 businesses with at least one answer. These are train-only diagnostics.
- User clarified the business metric: default “revenue” means order value after discounts; collected/paid cash is a separate metric and must only be answered when explicitly requested; abstain if the source cannot establish the requested metric.

## Commands and verification

- `PYTHONPATH=src python -m unittest tests.test_business_coverage -v` — exit 0, 3/3 passed after correcting a test assertion found on the first run.
- `PYTHONPATH=src python tools/build_business_coverage_matrix.py --profile ..\..\evaluation\business-profiles-train-v1-2026-11-16.json --replay ..\..\evaluation\p6-train-replay-v7-current-code-2026-11-16\evaluation_report.json --json-output ..\..\evaluation\business-coverage-matrix-train-v1-2026-11-16.json --markdown-output docs\BUSINESS_COVERAGE.md` — exit 0; exactly 30 businesses; levels as above; both source hashes embedded in JSON.
- `PYTHONPATH=src python -m unittest discover -s tests -v` — exit 0; 119 run, 116 passed, 3 skipped because this isolated work copy has no `.git` directory and repository-hygiene checks require one.
- Output audit: profile 30/30; README 30/30; files 128; tables/sheets 339; profile errors 0; profile questions 0; replay businesses 30; runtime errors `{}`. Matrix includes schema names/hints and metrics only, not README prose, cell values, question text, or answer labels.
- No source application behavior was changed in this slice. No Docker, Git, official checkout, branch, source archive, public data, commit, push, or permission operation was performed.

## Next actions

- Continue the remaining Playbook workstreams without repeating verified P0–P2 or spending time on Docker, which the user removed from scope.
- Keep every phase status tied to its acceptance metric. P7 profile completion is not P7 acceptance; no supported business is claimed.
- Use the user's clarified revenue contract in the next implementation slice: order value after discounts is default revenue; explicit collected/paid questions use a distinct metric; abstain when the data cannot establish the requested measure.
- Continue to preserve `sources/` read-only, use only frozen train evaluation after predictions are frozen, and do not tune against Public Test.

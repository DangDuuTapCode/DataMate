# DataMate implementation progress — 2026-11-19

## Repository and workflow

- Repository: `pl2n/DataMate` (user fork only).
- Branch: `feature/multi-bundle-query`.
- Upstream `DangDuuTapCode/DataMate` has not been modified. An existing PR #1 from this fork branch to upstream `main` is open; this work did not create or modify it.
- Changes are made through GitHub APIs. There is no local checkout, so no local `git status` or local test execution is claimed.
- Current branch head at this checkpoint: `6fde7f8211ec488f860255da7bb7e5f6e7809cab`.

## Implemented architecture

### Ingestion and schema understanding
- Excel grouped/multi-row headers are retained and combined with leaf headers when the workbook has clear merged group headings.
- Semantic mapping uses conservative exact aliases and grouped-header context. Ambiguous/colliding fields are not silently selected.
- Relationship discovery uses exact key overlap, uniqueness, cardinality, blanks, and unmatched values. It validates candidates but does not execute joins.
- Exact relationship-key aliases now cover order, customer, product, payment receipt, employee, supplier, purchase receipt, batch/lot, branch, and device IMEI identifiers. Generic row numbers/reference labels remain unmapped; identifiers are compared as exact strings.
- Relationship records now retain both table name and source filename. Bundle validation compares full table identities, so identically named worksheets from different workbooks cannot be mistaken for the same table.
- A versioned `BusinessSchemaCatalog` stores table schemas and relationship evidence.

### Multi-bundle planning
- Declarative bundle registry and explicit composite-rule registry.
- Versioned requirement extraction contract and schema validation.
- Shared-context guards prevent composite components from silently dropping filters, dimensions, sorting, or unsupported top-k context.
- Composite planner supports only allowlisted intents/rules; arbitrary conjunction splitting and new metrics remain out of scope.

### Business-rule evidence and capability resolution
- `schemas/business_rule_evidence.v1.schema.json` and `src/datamate/rule_evidence.py` define strict business/profile-scoped evidence.
- Capability IDs and assertions use a closed vocabulary. Every claim has exact table scope and provenance metadata.
- Resolver checks exact canonical fields, same-table co-location, validated relationship cardinality, and active SplitRules compatibility.
- Payment status uses a dedicated classifier. Unknown statuses abstain; pending, failed, cancelled, refunded, and reversed states are not treated as settled.
- Collection requires amount/date/status in the exact table scoped by both payment-source-role and settlement-policy claims.
- Revenue supports reviewed `direct_line` or `detail_to_order` source shapes. Detail-to-order requires an ordered line/order scope and validated `order_id` relationship.
- Runtime creates component-specific Executors over only evidence-approved tables and enforces the reviewed revenue source shape.
- Missing, malformed, wrong-business, rejected, out-of-scope, unsupported, or digest-invalid evidence blocks composite execution. Ordinary single-metric execution remains separate.

### Provenance verification
- Runtime recomputes SHA-256 from exact bytes of allowlisted local sources:
  - input-root `rulebook.md`;
  - business-local `data_dictionary.csv`, `.xlsx`, or `.md`;
  - business-local `operator_attestation.json`.
- Arbitrary paths, traversal, URLs, unknown filenames, missing files, symlink source files, paths outside the input root, and digest mismatches fail closed.
- SHA-256 establishes byte correspondence, not reviewer identity or a cryptographic signature.
- `docs/BUSINESS_RULE_EVIDENCE.md` was corrected to match the runtime behavior and to state the digest limitation accurately.

## Current capability policy

- Do not enable either default financial bundle merely because synthetic tests pass or headers appear plausible.
- Collection stays unavailable unless the active mounted rulebook explicitly supports the successful-payment-only policy.
- Revenue/collection source roles and exact business semantics require reviewed evidence.
- No automatic joins, fuzzy semantic inference, arbitrary query conjunction splitting, or new metrics.

## Verification

GitHub Actions run `44565385010` on branch head `6fde7f8211ec488f860255da7bb7e5f6e7809cab` executed 272 tests:
- 270 passed, including all feature tests.
- The only two failures are inherited repository-hygiene checks against the existing `CODEX PROGRESS` artifact: large-file limit and secret-like-pattern false positive.
- These checks were not weakened and the inherited artifact was not modified.

Run: https://github.com/pl2n/DataMate/actions/runs/44565385010

## Contest archive inspection and follow-up

The supplied `Contest.zip` was inspected on 2026-11-19. It contains two valid DataMate input roots:
- `Contest/train/`: 30 businesses, 3,000 questions, answer labels, calendar, and train rulebook.
- `Contest/public_test/`: 14 businesses, 1,000 questions, calendar, and a separate public-test rulebook.

Each root has the expected `rulebook.md`, `questions.jsonl`, `calendar.csv`, and `data/<business_id>/` layout. Every inspected business directory has a `README.md` describing source files, column meanings, grain, and shop-specific conventions. The archive does not contain separate `data_dictionary.*` or `operator_attestation.json` files in those business directories.

A narrow follow-up was implemented:
- `src/datamate/rule_evidence.py` now accepts only the exact business-local filename `README.md` under the existing `data_dictionary` provenance source type.
- `tests/test_rule_evidence.py` adds a digest-verification regression test for that exact file and location.
- The reader still requires a manually supplied evidence record, exact table scope, reviewer metadata, and a matching SHA-256. It does not create claims from README content.

The train and public-test rulebooks differ. The public-test version adds cash-by-shift, weekday-average, extra ranking, and industry-specific conventions. The runtime must be run separately against each split root. Neither supplied rulebook contains the explicit successful-payment-only policy clause recognized by `SplitRules`; collection therefore remains unavailable for these inputs. Do not infer that policy from the existence of payment columns or a payment table.

## Next engineering step

The archive now supplies a concrete benchmark for the next feature milestone. Prioritize a coverage audit of the 14 public-test businesses and their 1,000 questions, especially cases requiring multiple tables, multiple file formats, and domain-specific relationships. Convert representative cases into small synthetic regression fixtures rather than committing the 192 MB archive or its full data. Expand capability contracts only where the rulebook and README provide explicit, testable evidence.

Verification baseline before these changes: GitHub Actions run `44565561293` executed 272 tests (270 passed; two inherited `CODEX PROGRESS` repository-hygiene failures). The new README allowlist/test changes have not yet been verified by a new CI run. No local checkout or local test execution is available in this workflow.

See `docs/NEXT_SESSION_HANDOFF.md` for the resume checklist and `tools/STATE.md` for the compact current state.

## Multi-source relationship expansion

The contest archive exposed identifier families absent from the original four-key relationship vocabulary. The semantic mapper and relationship discovery now include exact aliases for employee IDs, supplier IDs, purchase receipt IDs, lot/batch IDs, branch IDs, and IMEI, while extending order/customer/product/payment receipt aliases. Generic `STT` and `Mã tham chiếu` remain unmapped. Relationship discovery still compares exact string values, checks overlap/cardinality/blanks/unmatched keys, and never executes joins.

Regression coverage was added for exact alias mapping, generic-label rejection, and six many-to-one relationship families. These new code/test commits have not yet been verified by GitHub Actions; no local checkout or local test run is available.


## Composite order-line relationship evidence

The public-test POS SQLite business (`dev_006`) exposed a real composite relationship:
- `chi_tiet_don_lo` refers to a sale detail row through both `MaHoaDon` and `SoThuTu`.
- `MaHoaDon` alone is not sufficient because many detail rows belong to the same order.
- The rulebook explicitly says identical rows of the same order are export duplicates and count once.
- The inspected database has 72,411 sale-detail rows, of which 1,350 exact duplicate row groups are removed for relationship profiling; the remaining 71,061 rows have unique `(MaHoaDon, SoThuTu)` pairs.
- The lot-allocation table has 72,710 rows, including multiple rows for a line that draws from multiple lots; all its composite order-line keys match the deduplicated detail table.

Implemented:
- `order_line_number` exact aliases (`Số thứ tự`, `No.`); generic `STT` remains unmapped.
- Composite `order_id + order_line_number` relationship candidates with component key names and all participating column indices.
- `SplitRules` parses the explicit same-order exact-duplicate clause. The rule is passed from `main.py` into schema catalog construction.
- Composite relationship profiling removes exact duplicate rows only when that explicit rule is present. Without the clause, duplicate composite keys remain ambiguous.
- Schema catalog version is now `1.1.0`.

This is still relationship discovery only. No source table is mutated and no composite join is executed. Other composite/polymorphic relationships, such as stock-ledger references that require both document type and document number, remain unsupported.


## Exact approved revenue join contract

A reviewed `detail_to_order` source shape previously validated an `order_id` relationship in the schema catalog, but the Executor independently rediscovered key columns from headers. That left a gap between the columns validated as evidence and the columns actually used at execution.

Implemented:
- `RevenueJoinContract` captures exact line/order table identities, source filenames, canonical key set, and both physical key-column indices.
- `BundleCapabilityResolver` creates this contract only when exactly one source-matched, validated `order_id` relationship exists with the required cardinality.
- The resolver normalizes relationship direction, so catalog ordering does not change the logical line-to-order contract.
- `CompositePlanner` carries the contract on the component; `main.py` passes it to the component Executor.
- When a contract is present, the detail-to-order Executor selects only those exact source-qualified tables and uses the approved key-column indices rather than independently guessing the join key.
- Without a contract, legacy single-metric behavior is unchanged; the evidence-gated composite path uses the stricter contract.

Regression coverage:
- Resolver emits exact source/table/index contract.
- Reversing schema-catalog table order still yields the same line-to-order contract.
- Executor joins using the approved physical columns even when another order-like column is present.
- Duplicate detail rows are counted once only when the active rulebook explicitly authorizes it; otherwise joined revenue abstains.

CI on commit `21469c4be7a3d93e5bd2befb879315f3c9c36afd`: 286 tests, 284 passed. The only two failures remain inherited repository-hygiene checks for the existing `CODEX PROGRESS` artifact (`test_no_large_files` and `test_no_secret_like_strings`). All feature tests passed.


## Conservative multi-hop relationship path discovery

Added `src/datamate/relationship_paths.py` and `tests/test_relationship_paths.py`.

The resolver:
- traverses only validated relationship edges;
- uses exact source-qualified table identities;
- preserves single or composite canonical keys and physical column indices;
- evaluates direction-aware cardinality and explicitly rejects one-to-many fanout;
- accepts only a unique path within a bounded hop count;
- returns explicit `no_path`, `ambiguous`, `fanout_risk`, `invalid_request`, or `unique_safe` outcomes.

Seven synthetic tests cover a safe two-hop many-to-one chain, fanout rejection, competing paths, unvalidated edges, source-file identity, composite key preservation, and invalid arguments.

GitHub Actions run `44578825930` on commit `68564ac356af305e63aabe1703ce76d98aadb08f`: 293 tests executed, 291 passed. All feature tests passed. The only two failures remain the inherited `CODEX PROGRESS` artifact findings in `test_no_large_files` and `test_no_secret_like_strings`. No local checkout or local test execution was used.

Important limitation: this resolver is discovery-only and is not yet connected to the query planner or Executor. It must not be described as general multi-hop JOIN execution.


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


## Post-merge continuation — 2026-11-20

- PR #1 merged successfully into upstream `main` at `99478a179919a7b5121b00072f90522c50117aba`; upstream main compares identical to the merge commit.
- New fork branch: `feature/query-specific-join-execution`, based on merged PR head `15430b417d650e6145ed4e64cb637ebe2a00677c`.
- Hardened the structural FactJoinContract builder against forged unique-path metadata and malformed hop records. It now requires exactly one candidate, immutable typed hops, exact source-qualified endpoints, unique nonblank canonical keys, valid physical key-index tuples, literal false fanout, and safe join-type input validation.
- Added regression coverage for forged candidate count, malformed identities, duplicate key declarations, and invalid join-type values.
- Commits: `5c04d9b8498133e28170108ed3ba7fe8ec58301a`, `783631e99ed584fee284564c126b1275ca453edf`.
- CI for the new branch has not yet been verified. No local checkout or local test execution was used.
- Runtime wiring remains blocked pending a representative real query family with reviewed source evidence for fact grain, measure semantics, additive behavior, exact path/keys, and aggregation stage.


### Malformed-cardinality follow-up

- Added an explicit string-type check before cardinality membership validation and a regression for an unhashable list value.
- Latest code/test commits: `101a5089d1bd71c45b17516f5753a2e01f06f151`, `4e073e4f1a35a216179094ff0d63389f27829775`.
- Branch head verified at `4e073e4f1a35a216179094ff0d63389f27829775`; no Actions run is available yet.


### CI branch coverage

- Updated the Python test workflow to run for pushes to any `feature/**` branch and PRs targeting `main` or `feature/**`.
- Commit: `e74d43413c3966d7d80e6fbe8f985fb5b6ac4de9`.
- No Actions run/status was surfaced for this push; CI remains unverified.


## Contest-backed LEFT JOIN validation — 2026-11-20

- Inspected the re-uploaded Contest archive and selected the README/rulebook-backed `biz_129` customer-group revenue query family.
- Measured 145,479 sales lines, 38,499 orders, 220 customers, and 38,072 payment events. All detail order keys match; 23,309 nonblank order customer IDs match the catalog, while 15,190 orders have blank customer IDs.
- Identified required semantics: guest orders are excluded from customer groups but included in total-shop revenue. The full fact path therefore requires LEFT JOIN to preserve blank-customer orders. Payment events must remain a separate fact because up to four payment rows can exist per order.
- Added source-context semantic aliases, `validated_left_join` relationship evidence, `left_join_required` path status, and contract enforcement that rejects INNER JOIN for these paths.
- Added a synthetic README-shaped integration test and `docs/CONTEST_BIZ129_JOIN_CASE.md`.
- No contest source data was committed. Runtime wiring remains disabled. CI is not yet verified and no local tests were run.

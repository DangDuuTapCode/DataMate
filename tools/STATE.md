# DataMate current state — 2026-11-19

## Repository

- Work only in fork `pl2n/DataMate`, branch `feature/multi-bundle-query`.
- Current implementation/test head: `2522abbafdccb6bb930d3f79f9f0f13af8302d4f`; docs/checkpoint commits follow it.
- Latest implementation code head: `21469c4be7a3d93e5bd2befb879315f3c9c36afd`; branch ref was last checked at `179f5c3383aa456d88ee08f900daca868805c403` before final documentation-only synchronization. Fetch current branch head before the next code change.
- Branch head was verified at `04881307f968d69a6a6f64caa5c25b5211bb6ef9` before the composite-order-line milestone; fetch the current branch head before the next code change.
- Do not modify upstream `DangDuuTapCode/DataMate`. An existing PR #1 is open to upstream `main`; do not create a duplicate or merge it unless requested.
- GitHub API workflow only; no local checkout, local git status, or local test execution.
- Latest implementation baseline: `a6eade98f01e55326ae53bf6423800868b6f77b3`.
- Latest documentation commits: `bc01731c4e445841bbff72ab32b74bbcc18dfb6e` (provenance guide) and `382a75c33fb0bf51617dde33cee1ba172854ef65` (handoff).

## Implemented

- Grouped Excel headers and retained header metadata.
- Exact semantic mapping with ambiguity handling; relationship validation without automatic joins. Key families include order/customer/product/payment receipt plus employee, supplier, purchase receipt, batch/lot, branch, and IMEI; generic row numbers/reference labels remain unmapped.
- Relationship evidence carries both table names and source filenames; capability checks use exact `(table_name, source)` identity to distinguish repeated worksheet names.
- BusinessSchemaCatalog, bundle registry, requirement extraction/schema, composite rules, and shared-context guard.
- BundleCapabilityResolver checks exact canonical fields, co-location, validated relationships, and explicit business-rule evidence.
- Runtime constructs per-business catalogs/planners and records evidence/capability decisions.
- SplitRules/executor conformance for revenue amount/date/status semantics and collection successful-payment policy.
- Dedicated payment-status classifier; unknown values abstain.
- Evidence-approved exact table scope and revenue source shape are enforced by component-specific Executors.
- Business-rule evidence v1 contract and strict local SHA-256 provenance verification.

## Safety and capability boundaries

- Missing, malformed, wrong-business, rejected, incorrectly scoped, unsupported, or digest-invalid evidence blocks composite execution.
- Revenue source shape must be explicitly reviewed as `direct_line` or `detail_to_order`; detail-to-order requires a validated `order_id` relationship.
- Collection requires payment-event amount/date/status in the exact single table scoped by both source-role and settlement-policy claims.
- Collection remains unavailable unless the active rulebook explicitly states the supported successful-payment-only policy.
- Provenance allowlist remains narrow: input-root `rulebook.md`; business-local `data_dictionary.csv/.xlsx/.md` or `README.md`; business-local `operator_attestation.json`. README is treated as schema documentation only and never auto-generates evidence.
- SHA-256 proves byte correspondence only; it does not authenticate reviewer identity or provide a signature.
- No arbitrary path access, automatic joins, fuzzy inference, arbitrary conjunction splitting, or new metrics.

## CI

- Run `44564104588` on commit `a6eade98f01e55326ae53bf6423800868b6f77b3`: 272 tests; 270 passed. All feature tests passed. Two inherited `CODEX PROGRESS` hygiene checks failed (large-file limit and secret-like-pattern false positive).
- Run: https://github.com/pl2n/DataMate/actions/runs/44564104588
- Two docs-only commits followed that run; inspect their Actions results before further code edits.
- Never weaken or modify the inherited hygiene artifact to hide those failures.

## Contest archive and current blocker

The user supplied `Contest.zip`, inspected on 2026-11-19:
- Train root: 30 businesses, 3,000 questions, answers, calendar, and train rulebook.
- Public-test root: 14 businesses, 1,000 questions, calendar, and a separate public-test rulebook.
- Both roots match the runtime's expected directory layout. Every inspected business has a local `README.md` with source/column/table-grain documentation; separate data dictionaries and operator attestations are absent.
- Train and public-test rulebooks differ; each split must be run with its own root.
- Neither rulebook contains the explicit successful-payment-only policy clause. Collection remains unavailable.

Committed after archive inspection:
- `47649aa3ba70ddaaa363986d7beb2a81ba0a8a5f` README provenance allowlist.
- `fa402eae2862463f30a0d3403e7d0c7f82e5c819` README digest regression test.
- `a33ccdd32355f163069c47872e42acdb87b79489` evidence documentation.
- `7edf33b418cce8ed782cc64282c8b7376f08ce40` implementation progress update.
- `f5c73cdef1de583c094507344e270966f3044129` handoff update.

Next: audit public-test questions against the 14 input shapes, then build minimal synthetic fixtures for representative multi-source queries. Do not add the full archive to Git. The new code/test commits still need a verified Actions result. No local checkout or local test run is available.

## Latest multi-source expansion

- Exact aliases and relationship-key families expanded based on Contest.zip schemas.
- Added synthetic tests for exact aliases and six many-to-one relationship families.
- Commits: `8ff2c09`, `37f66c3`, `a784b4f`, `2d866ee`, `a64ba34`, `0465e9d`, `dccf1ba`, `45b3667`, `9d2ceab`.
- CI for these changes is not yet verified. The last known baseline remains run `44565561293` (272 tests; 270 passed, two inherited hygiene failures).

## Source-qualified relationship identity fix

- `RelationshipCandidate` now includes `from_source` and `to_source`.
- Revenue detail-to-order validation compares exact table identities, not worksheet names alone.
- Regression tests cover duplicate `Sheet1` names across workbooks and same-name scoped source pairs.
- Commits: `c4278e8`, `5d2b62e`, `5e67aff`, `abfc0df`, `dfe61ce`, `d16c67a`, `6e3af74`, `38a85ba`.
- CI remains unverified for this continuation.

## Composite order-line relationship milestone

- Active rulebook parser now detects the exact same-order duplicate-row clause; default false when absent.
- Exact `Số thứ tự`/`No.` aliases map to `order_line_number`; `STT` remains unmapped.
- Relationship discovery emits composite `order_id+order_line_number` evidence, with all key columns and source-qualified table identity.
- Exact duplicate rows are removed only for composite relationship profiling and only when the rulebook enables it. No source rows are mutated and no joins are executed.
- Main runtime passes the active rulebook flag into schema catalog construction; catalog schema version 1.1.0.
- Relevant commits: `107216e`, `64c426c`, `01e54b3`, `bd2b1f6`, `0f120e9`, `3191b7a`, `7016a60`, `ef200e2`, `06a579f`, `d0d75b9`, `4f6def6`, `6ae52b0`, `a6da9e4`, `4e17cd9`, `3741d34`, `aa6e746`, `ea5fb27`.
- This change set has no verified Actions result yet; no local checkout or local test run is available.


## Exact approved revenue join contract

- Detail-to-order revenue no longer relies only on a relationship check followed by independent executor header guessing in the composite path.
- `RevenueJoinContract` stores exact line/order table identities, source filenames, canonical key set, and physical key-column indices.
- Resolver emits it only for one exact validated source-qualified `order_id` relationship with safe cardinality; direction is normalized even if catalog order is reversed.
- Composite planner carries the contract and main passes it to the scoped Executor. Executor enforces exact table identity and key-column indices.
- Joined duplicate line rows are deduplicated only with explicit active rulebook authorization; otherwise execution abstains.
- Latest implementation commit before docs: `21469c4be7a3d93e5bd2befb879315f3c9c36afd`.
- CI run `44577298652`: 286 tests, 284 passed; all feature tests pass. Two inherited failures remain for the existing `CODEX PROGRESS` artifact in repository hygiene tests.
- Relevant commits: `c00cd0e`, `11cbcb0`, `ea7f156`, `9b20c0b`, `5e05f2b`, `d926cae`, `09cef43`, `004306d`, `72e94d6`, `3ae9966`, `f3a8bd4`, `059b931`, `21469c4`, plus documentation checkpoints `61e9430`, `705f016`, `7cd271a`.
- This is a narrow revenue detail-to-order contract, not a general join planner. Composite keys, polymorphic references, multi-hop paths, and arbitrary dimension joins remain unsupported.


## Multi-hop relationship path discovery (2026-11-20)

- Added `src/datamate/relationship_paths.py` and `tests/test_relationship_paths.py`.
- Discovery-only graph resolver; not wired into planner/Executor.
- Exact source-qualified table identity; validated edges only; carries composite canonical keys and endpoint column indices.
- Cardinality-aware traversal: many-to-one and one-to-one preserve source grain; one-to-many is `fanout_risk`.
- Unique path only; multiple paths ambiguous; no heuristic ranking.
- CI run `44578825930`: 293 tests, 291 passed; all feature tests pass. Two inherited hygiene failures remain for `CODEX PROGRESS`.
- Implementation commit: `68564ac356af305e63aabe1703ce76d98aadb08f`.
- Next: query-specific execution contract including fact grain, aggregation stage, exact path and fanout policy. Do not enable arbitrary multi-hop joins.
## Relationship path bound hardening (2026-11-20)

- Fixed candidate-cap off-by-one: exactly max_candidates paths may still be a valid unique result; overflow is reported only after observing one more path.
- Invalid/non-integer/boolean limits and malformed or blank table identities return invalid_request.
- Added six synthetic regressions for exact cap, overflow, reverse traversal fanout, hop limit, invalid limits, and cycles.
- Commits: 4212165cece5a9167095984865aca98ae6362890 and fe799c55ac9757a64007fbe03ef0a9028e6ff1f2.
- CI pending; no local test execution.


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

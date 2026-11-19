# Next-session handoff — 2026-11-19

## Repository and working rules

- Continue only on `pl2n/DataMate`, branch `feature/multi-bundle-query`.
- This is the user's fork. Do not modify upstream `DangDuuTapCode/DataMate` and do not create a PR unless explicitly requested.
- Work is performed through GitHub APIs; there is no local checkout. Do not claim a local `git status` or local test execution.
- Commit completed milestones frequently and update this handoff/checkpoint.
- Current branch head verified after documentation checkpoints: `e8ef27e7be1a4453f5b7b49bcb7c042d1b2e0183`. Latest implementation code head: `21469c4be7a3d93e5bd2befb879315f3c9c36afd`.
- Latest implementation baseline: `a6eade98f01e55326ae53bf6423800868b6f77b3`; continuation commits since then are documentation/checkpoint-only.

## Completed implementation

- Excel grouped/multi-row header ingestion with raw header metadata.
- Conservative semantic mappings, collision/ambiguity handling, and exact key relationship validation.
- Versioned business schema catalog.
- Declarative bundle registry, requirement extraction contract/schema, and composite rule registry.
- Shared-context safety checks for composite query components.
- Bundle capability resolution based on exact canonical fields, table co-location, validated relationship cardinality, and explicit business-rule evidence.
- Per-business runtime schema catalog and composite planner wiring.
- Versioned business-rule evidence contract with closed capability/assertion vocabulary, exact table scope, provenance metadata, and strict parsing.
- SplitRules/executor conformance checks for revenue amount basis, period basis, order-status exclusions, and collection successful-status policy.
- Payment status has its own conservative classifier; unknown statuses abstain.
- Evidence-approved table scope is passed into component-specific Executors. Revenue source shape is enforced as either `direct_line` or `detail_to_order`.
- Runtime recomputes SHA-256 from exact bytes of allowlisted local provenance files. Arbitrary paths, traversal, URLs, unknown filenames, missing files, symlinks, paths outside the input root, and digest mismatches fail closed.
- Documentation has been synchronized; see `docs/BUSINESS_RULE_EVIDENCE.md`, `docs/IMPLEMENTATION_PROGRESS.md`, `tools/STATE.md`, and `tools/checkpoints/2026-11-19_CONTINUATION_REVIEW.md`.

## Current capability boundaries

- Default financial bundles must remain unavailable unless their structural and business-rule evidence is verified.
- Revenue supports reviewed `direct_line` or `detail_to_order` source shapes. The latter requires a validated `order_id` relationship and ordered line-table then order-table scope.
- Collection requires payment amount, payment date, and explicit payment status in one exact reviewed table. Source-role and successful-status-policy claims must refer to that same table.
- Collection remains unavailable if the active rulebook does not explicitly support the successful-payment-only policy.
- No automatic joins, fuzzy semantic inference, arbitrary natural-language conjunction splitting, or new metrics.
- SHA-256 verification proves byte correspondence with an allowlisted local source; it does not authenticate the reviewer's identity or provide a cryptographic signature.

## Verification

- GitHub Actions run `44565561293` on `5a6085264796a9a2c413a1323cba5e96b5f9e0a7`: 272 tests; 270 passed.
- All feature tests passed. The only two failures are inherited `CODEX PROGRESS` repository-hygiene checks (large-file limit and a secret-like-pattern false positive). Do not weaken the checks or modify that inherited artifact.
- Run: https://github.com/pl2n/DataMate/actions/runs/44565561293
- The subsequent checkpoint commit `c1b3b4cea609d52d29620ee41a798d260e99dfe6` only adds documentation; no CI run for that commit was visible at the time of this handoff.
- No local checkout or local test execution is available in this workflow.

## Contest archive received — 2026-11-19

The user supplied `Contest.zip` (approximately 192 MB). It was inspected without adding the archive to the repository.

- `Contest/train/`: 30 business directories (`biz_101`–`biz_130`), 3,000 questions, answer labels, `calendar.csv`, and its own `rulebook.md`.
- `Contest/public_test/`: 14 business directories (`dev_001`–`dev_014`), 1,000 questions, `calendar.csv`, and a distinct `rulebook.md`.
- Both split roots match the runtime layout: root rulebook/questions/calendar plus `data/<business_id>/`.
- Each inspected business directory has a `README.md` documenting file roles, columns, table grain, relationships, and shop conventions. No separate `data_dictionary.*` or `operator_attestation.json` was found in those business directories.
- Train and public-test rulebooks differ. Public test adds cash-by-shift semantics, weekday averages, additional rankings, and rules for mother-and-baby, vehicle-repair, and phone-shop domains. Run each split with its own root; do not merge them under one rulebook.
- Neither rulebook has the explicit successful-payment-only clause parsed by `SplitRules`. `collection_status_policy` therefore remains unsupported for this archive. Payment tables/columns do not prove the settlement policy.

## Changes made after receiving the archive

- `src/datamate/rule_evidence.py`: exact business-local `README.md` is now accepted as a schema/documentation provenance source under the existing `data_dictionary` type. All existing digest, path, symlink, and scope checks remain in force.
- `tests/test_rule_evidence.py`: added a regression test for `README.md` digest verification.
- `docs/BUSINESS_RULE_EVIDENCE.md` and `docs/IMPLEMENTATION_PROGRESS.md`: documented actual split layout, README provenance boundary, rulebook differences, and the collection-policy limitation.
- These changes were committed sequentially:
  - `47649aa3ba70ddaaa363986d7beb2a81ba0a8a5f` — README provenance allowlist.
  - `fa402eae2862463f30a0d3403e7d0c7f82e5c819` — README provenance regression test.
  - `a33ccdd32355f163069c47872e42acdb87b79489` — evidence contract documentation.
  - `7edf33b418cce8ed782cc64282c8b7376f08ce40` — implementation progress and benchmark findings.

## Multi-source identifier expansion

The public-test archive showed that the original relationship vocabulary (order, customer, product, payment transaction) was too narrow for the supplied business schemas. Added exact aliases and relationship-key support for:
- employee/staff IDs;
- supplier/vendor IDs;
- purchase receipt IDs;
- lot/batch IDs;
- branch IDs;
- device IMEI;
- additional explicit order, customer, product/barcode, and payment-receipt aliases.

The change intentionally does not map generic `STT`, `Mã tham chiếu`, or generic `Mã`. Relationship validation still requires exact string overlap and safe cardinality; it does not perform joins.

Commits:
- `8ff2c0935536c4c31b21e845bb7fc02464b3bbda` — exact business identifier aliases.
- `37f66c385021eb49a22d6adbce6dfcd7951f6a5b` — expanded relationship-key vocabulary.
- `a784b4fb9524b54493474cd36a418bf25deace9b` — semantic alias regression test.
- `2d866ee9585211b69a39dcb226c911eb03041f2b` — relationship regression test.
- `a64ba3439d2a82dcc73d324b9ba6cdefeab1bd67` — payment receipt aliases.
- `0465e9d9d06b4c3c65d4cba48c1520458daa9619` — payment alias test update.
- `dccf1bab63c1ac511294d0f7f10b896ee53cc1a4` — relationship capability documentation.
- `45b3667a5f8db22ea9f9ca1cb66ea6294db70a7a` — implementation progress update.

## Source-qualified relationship identity fix

The archive includes multiple workbooks whose worksheet names repeat (often `Sheet1`). The prior `RelationshipCandidate` stored table names but not source filenames, and detail-to-order capability checks matched only names. This could conflate two distinct tables with the same sheet name.

Fixed:
- `RelationshipCandidate` now stores `from_source` and `to_source`, and serializes both.
- Revenue detail-to-order capability validation matches exact `(table_name, source)` pairs.
- Source-scope uniqueness is checked by full table identity, not table name alone.
- Regression tests cover same-named sheets in different workbooks and exact source-scoped detail-to-order validation.

Commits:
- `c4278e84faace7a690fd5de92e0c62ff5df85823` — source identity in relationship evidence.
- `5d2b62e6bc9ead2af82323989070dc3f23428efc` — exact source matching in capability resolver.
- `5e67affa186a4b428c3dac2ed43c68d24bd84a9b` — scope uniqueness by full identity.
- `abfc0dfc5b6adda4c2cfeaafd4ae75a4fe3194de` — repeated worksheet name regression.
- `dfe61ceb3bb12b6ef3d4b2b80e36ae19a018ceba` — same-name detail-to-order scope regression.
- `d16c67a7a26e7e4431a66524f4c105ccc8e2727f` — relationship identity documentation.
- `6e3af74a27e0a477f4597b6e800c93f8d8ac20a5` — progress update.

## Rulebook-aware composite order-line relationships

The POS SQLite input exposed a relationship that cannot be safely represented by one key:
- `chi_tiet_don_lo` references `chi_tiet_don` by `(MaHoaDon, SoThuTu)`.
- Single `MaHoaDon` overlaps at order grain and is many-to-many between the two detail tables.
- The rulebook explicitly states that exact duplicate rows within the same order are export errors and count once.
- The inspected POS database has 72,411 `chi_tiet_don` rows; 1,350 exact duplicate rows are removed only for relationship profiling, leaving 71,061 unique order-line keys. The lot allocation table has 72,710 rows; all composite order-line keys are covered by the deduplicated detail table. Multiple lot rows per line are expected.

Implemented:
- `SplitRules.deduplicate_identical_order_lines` parses the exact rulebook clause; absent clause defaults to false.
- Exact aliases for `Số thứ tự` and `No.` map to `order_line_number`; generic `STT` stays unmapped.
- Relationship discovery now emits a composite `order_id+order_line_number` candidate, with key component names and all column indices.
- Exact duplicate rows are removed from composite-key profiling only when the active rulebook explicitly authorizes it.
- `main.py` passes the active rulebook flag into `build_schema_catalog`.
- Schema catalog version is `1.1.0`.
- This is still discovery only: no source table mutation and no join execution.

Commits:
- `107216e39994fe7aa846dd47e55350f086e0ba73` — parse exact duplicate-line rule.
- `64c426cef3e51a20fd80202d4f0b385279cee352` — order-line sequence alias.
- `01e54b3dbc05629c2e48a4ca6edd6484086a465e` — composite relationship discovery.
- `bd2b1f6f9eb80d208cedc16d1975a328439306cf` — catalog policy parameter.
- `0f120e9c49a6f4c9f36c19712d8b7073f5c066f1` — runtime policy wiring.
- `3191b7a6559178daf303246251606810113e19d0` — normalized clause matching correction.
- `7016a6007ba15f18eb3a519be5dfaa7746ad6ab6` — semantic test update.
- `ef200e29f93393afbb5969a1f6648ef22fc34963` — composite relationship tests.
- `06a579f1fa474ac1664bbb1e1cf398614e1382f6` — catalog test.
- `d0d75b9941f440fd4cb4f13027ccb60845e2fb75` — split-rule tests.
- `4f6def6851ddff74ffeeba4079a6ca31d2c27369` — catalog schema version 1.1.0.
- `6ae52b0479b14da76d4b3d873925589339042c7f` — schema version test.
- `a6da9e40fb57a95d4c0924005aad81d142460b97` — partial-overlap test expectation.
- `4e17cd94e1f01ecb3e75ae1911916d0c8b8887cc` — relationship documentation.
- `3741d341d3709df8f9193e8e9c8599952e03b4f9` — duplicate-line rule documentation.
- `aa6e746425f1e77b05c7e1837e18202cb67b7477` — progress update.

## Exact approved revenue join contract

The prior detail-to-order resolver validated a source-qualified `order_id` relationship, but the Executor independently rediscovered key columns from headers. This meant the physical key used during execution was not explicitly carried from the evidence that had been validated.

Fixed:
- Added `RevenueJoinContract` with exact detail/order table identities, source filenames, canonical key set, and physical key-column indices.
- `BundleCapabilityResolver` emits it only when exactly one source-matched validated `order_id` relationship with safe line-to-order cardinality exists.
- The resolver normalizes edge direction; reversing the schema catalog table order still produces the same logical contract.
- `CompositePlanner` carries the contract into `QueryComponent`; `main.py` passes it to the scoped component Executor.
- Executor uses only the exact source-qualified tables and approved key-column indices when the contract is present.
- Existing non-composite single-metric execution remains unchanged when no contract is supplied.
- Exact duplicate joined line rows count once only if the active rulebook explicitly authorizes the policy. Without the clause, joined revenue abstains.

Regression tests cover contract creation, reversed catalog order, exact physical key-index use, and rulebook-gated duplicate handling.

Commits:
- `c00cd0ecabbeff8b9064fb704b61f6af39dabcdd` — require explicit rulebook policy before deduplication.
- `11cbcb02afdc496d74c03a96ba22f26a3248c7ac` — duplicate-policy regression tests.
- `ea7f156db237a258dff4c12abd43665bac87b6ed` — declare the duplicate rule in the joined-revenue test fixture.
- `9b20c0bc2871d1fa9b2deef91d643481936d707e` — exact approved join contract in capability resolution.
- `5e05f2b2ef948a8518a2915fc2974200e03b56c9` — carry contract through composite planning.
- `d926caebc0dbb6ab3cc8ece2717ec8843bd36277` — Executor accepts the contract.
- `09cef4347e767acb6122c9d10c7005e262ebe179` — enforce exact table identities and key indices.
- `004306dc46041dced471cbc970250ad90baca779` — runtime passes the contract.
- `72e94d6f1614a9bf0aca7d5183d83f7e6191d0d5` — resolver contract test.
- `3ae99663419ee0a3d7a6f51cad85edadfb28c490` — executor key-index test.
- `f3a8bd4340c58d2e4776442d75091880ac3214ab` — indentation correction caught by CI.
- `059b931f1b4d531814469def5e28f5f517c397ec` — reversed catalog-order test.
- `21469c4be7a3d93e5bd2befb879315f3c9c36afd` — joined evidence-label expectation.

Verification on `21469c4`: GitHub Actions run `44577298652`, 286 tests, 284 passed. All feature tests passed; the only failures are the two inherited `CODEX PROGRESS` repository-hygiene checks. No local checkout or local test run was used. Run: https://github.com/pl2n/DataMate/actions/runs/44577298652

## Next engineering step

Use the 14 public-test businesses and 1,000 public-test questions as a coverage map. Prioritize representative multi-source cases and add small synthetic fixtures for them; do not commit the 192 MB archive or its full business data. Focus on source-role and relationship contracts, not a universal join. Extend only with explicit README/rulebook evidence. Keep collection unavailable until a supported settlement policy is present.

Verification baseline before these changes: Actions run `44565561293` on `5a6085264796a9a2c413a1323cba5e96b5f9e0a7`, 272 tests, 270 passed, two inherited `CODEX PROGRESS` hygiene failures. The new code/test changes do not yet have a verified CI result. There is no local checkout or local test execution in this workflow.

## Useful files

- `src/datamate/rule_evidence.py`
- `src/datamate/bundle_capabilities.py`
- `src/datamate/split_rules.py`
- `src/datamate/metrics.py`
- `src/datamate/main.py`
- `tests/test_rule_evidence.py`
- `tests/test_bundle_capabilities.py`
- `tests/test_api.py`
- `docs/BUSINESS_RULE_EVIDENCE.md`
- `docs/BUNDLE_CAPABILITY_RESOLUTION.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `tools/STATE.md`

# Next-session handoff — 2026-11-19

## Repository and working rules

- Continue only on `pl2n/DataMate`, branch `feature/multi-bundle-query`.
- This is the user's fork. Do not modify upstream `DangDuuTapCode/DataMate` and do not create a PR unless explicitly requested.
- Work is performed through GitHub APIs; there is no local checkout. Do not claim a local `git status` or local test execution.
- Commit completed milestones frequently and update this handoff/checkpoint.
- Last previously verified documentation head: `48e5c60f3a3802984fb4cdc6c87e358f14ee96e9`. New continuation commits are listed below; fetch the branch head before the next code change.
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

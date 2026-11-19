# Next-session handoff — 2026-11-19

## Repository

Continue on pl2n/DataMate, branch feature/multi-bundle-query. Do not modify upstream DangDuuTapCode/DataMate; do not create a PR unless requested.

Implementation commit: c06e7c42befd1500d743219ab1a3ec3883213ef8. Work was performed through GitHub APIs; no local checkout or literal local git status is available.

## Completed architecture

See docs/IMPLEMENTATION_PROGRESS.md, docs/MULTI_BUNDLE_QUERY.md, and dated checkpoints under tools/checkpoints/. Completed pieces include grouped-header ingestion, semantic mappings, relationship validation, business schema catalog, bundle registry, requirement extraction/schema, composite rule registry, shared-context guard, and bundle capability resolution.

## Capability-resolution contract

Implementation:
- src/datamate/bundle_capabilities.py
- src/datamate/bundles.py
- tests/test_bundle_capabilities.py
- docs/BUNDLE_CAPABILITY_RESOLUTION.md

The resolver checks exact canonical fields, same-table co-location, and explicitly declared validated relationship cardinality. It reports missing/ambiguous fields and unverified business-rule capabilities. It never executes joins or infers business semantics.

Source-shape constraints:
- Revenue supports either direct line facts or a detail-to-order path. Do not model this as one flat same-table field list until the schema contract can express alternatives and the required relationship path.
- Collection currently requires payment-event amount and payment date. Its payment source role and settled-payment policy remain unverified.
- Both default bundles stay unavailable under catalog-gated planning until source-role and business-rule evidence is modeled and validated.

## Production runtime

src/datamate/main.py builds a BusinessSchemaCatalog once per business from the same ingested tables used by Executor, then passes it to a per-business CompositePlanner. A runner regression proves that mapped headers alone do not enable the financial composite while business-rule capabilities remain unverified.

## Verification

GitHub Actions run 44555242526 executed 242 tests: 240 passed. The only two failures are the inherited CODEX PROGRESS size and secret-like-regex hygiene checks. Feature tests passed.

Run: https://github.com/pl2n/DataMate/actions/runs/44555242526

## Active next step

Inspect src/datamate/split_rules.py, the actual mounted rulebook contract, and Executor source discovery. Design a versioned business-rule evidence contract for:
- alternative revenue source shapes and the relationship path for detail-to-order;
- payment table role and the policy when payment status is absent or present;
- rule-profile version, source provenance, and validation status.

Do not infer business semantics from column names or sample values. Keep automatic joins, arbitrary natural-language splitting, and new metrics out of scope.


## Business-rule evidence contract — latest milestone

Implemented:
- `schemas/business_rule_evidence.v1.schema.json`
- `src/datamate/rule_evidence.py`
- `tests/test_rule_evidence.py`
- `docs/BUSINESS_RULE_EVIDENCE.md`

The v1 payload is scoped to one business and contains versioned `revenue_rules` / `collection_rules` profiles. Each capability assertion has a closed allowlisted value, explicit exact table scope, and provenance (source type/reference, SHA-256, reviewer, timezone-aware review timestamp). Unknown or duplicate claims, unsupported assertions, malformed provenance, and business-ID mismatches are rejected.

Important boundaries:
- This is a strict contract/reader only. It does not synthesize evidence from headers/sample values, change executor calculations, or enable default bundles.
- Verified claims count only if all exact scoped table identities exist in the matching BusinessSchemaCatalog.
- Collection's current executor only applies successful-status filtering when a payment status column exists. The next integration must require an unambiguous `payment_status` field for the collection bundle and keep it unavailable when status is absent.
- Revenue source shape assertions need to match actual direct-line or detail-to-order executor paths; do not let an attestation silently authorize an unimplemented path.

## Next step

Wire the optional per-business evidence file (suggested path: `data/<business_id>/business_rule_evidence.json`) into `main.run`, `CompositePlanner`, and `BundleCapabilityResolver`. Missing/invalid/mismatched evidence must leave the bundle unavailable. Add tests for both valid and invalid runtime evidence. No automatic joins, fuzzy inference, or parser expansion.


## Business-rule evidence contract verification

Commit `f6d5115ea4099311ed3d01eeb0257abfa37818c4` adds the strict reader/schema/tests and docs. GitHub Actions run `44556933123` executed 250 tests; all new evidence-contract tests passed, with 248 total passing. Only the two inherited `CODEX PROGRESS` hygiene checks failed. Run: https://github.com/pl2n/DataMate/actions/runs/44556933123


## Latest milestone — business-rule evidence runtime integration

Current branch head before this documentation update: `02dc61c983de696ded042f021e2f64f2b886c8e6`.

The v1 evidence contract is now wired into production:
- Runtime reads optional `data/<business_id>/business_rule_evidence.json`.
- Valid evidence is passed to `CompositePlanner` and `BundleCapabilityResolver`.
- Missing/invalid evidence blocks composite planning. Trace records evidence status and per-bundle resolution reasons.
- Collection requires canonical payment-event amount, payment date, and payment status in one table. Source-role and successful-status policy claims must share the same exact table scope.
- Grouped payment headers are recognized by the executor. Explicit payment status is preferred; legacy generic-status fallback remains for single-metric execution.
- Revenue detail-to-order evidence requires ordered line/order table scope and validated many-to-one `order_id` relationship.
- SHA-256 provenance is recorded and format-checked, but this version does not recompute it from arbitrary external references. Treat the reviewer as responsible for digest/source correspondence.

CI run `44558398515`: 256 tests, 254 passed; all feature tests passed. The only failures are the two inherited `CODEX PROGRESS` hygiene checks. Run: https://github.com/pl2n/DataMate/actions/runs/44558398515

## Next step

Validate evidence assertions against the actual split rulebook and supported executor profile. Then design safe source-digest verification using controlled, known source locations. Keep absent/invalid evidence fail-closed; do not infer semantics from headers or sample values.


## Resume details

- Latest runtime code commit: `02dc61c983de696ded042f021e2f64f2b886c8e6`.
- Latest docs/schema commit: `96d63298a940a0e449c7303bbe668508d74c0637`.
- Latest CI: run `44559194129`, 256 tests / 254 passed. Only the two inherited repository-hygiene checks failed; feature tests passed. Run: https://github.com/pl2n/DataMate/actions/runs/44559194129
- Resume by cross-checking the six capability assertions with `SplitRules` and the exact `Executor` behavior, then implement controlled source-digest verification. Do not auto-generate evidence or weaken fail-closed behavior.

## Latest scope-validation milestone

Implementation commit: c7d251de506acd54093578639a7b1aac2711aed4.

- Collection required fields are restricted to the exact single table shared by both reviewed collection claims.
- Revenue detail-to-order accepts equivalent validated edge orientation from catalog table order: many-to-one line→order or one-to-many order→line. Evidence scope itself remains ordered line then order.
- Direct-line revenue evidence must scope exactly one table.
- Added a valid evidence-backed end-to-end runner test. It confirms the runtime loads the file, authorizes both bundles, executes both components, and returns the side-by-side table.
- CI run 44560238399: 259 tests; 257 passed; only the two inherited CODEX PROGRESS hygiene checks failed. Feature tests passed.

Next: validate evidence provenance/digests against controlled known sources. Do not retrieve arbitrary references or treat a syntactically valid hash as proof of source correspondence.


## Latest continuation — rulebook/executor conformance

Starting branch head: `ab834e246fdfe36d4b2025b32bbfeace0c36f5aa`.

Implemented:
- Payment status now has a dedicated classifier; collection no longer reuses order-status classification.
- Explicit successful/paid states are included; pending, failed, cancelled, refunded/reversed are excluded; unknown statuses abstain.
- SplitRules parses revenue amount basis, period basis, and an optional collection successful-status-only clause.
- BundleCapabilityResolver cross-checks revenue evidence against active SplitRules. Collection policy evidence is accepted only when the active rulebook explicitly supports it.
- CompositePlanner passes its RulePlanner's active SplitRules to capability resolution.
- Synthetic tests cover payment states, unknown states, and evidence/rulebook mismatches.

The runtime-mounted `data/rulebook.md` is not versioned in this repository. Do not assume it contains the collection clause; without it, collection stays unavailable.

Next: review CI, then design controlled SHA-256 verification against allowlisted input-root files. No local checkout or local test execution is available in this workflow.

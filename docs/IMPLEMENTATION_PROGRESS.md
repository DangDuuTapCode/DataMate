# Implementation progress — 2026-11-19

## Repository and branch

- Repository: pl2n/DataMate (user fork only).
- Branch: feature/multi-bundle-query.
- Upstream DangDuuTapCode/DataMate is not modified; no PR is open.
- Implementation commit: c06e7c42befd1500d743219ab1a3ec3883213ef8.
- Work is performed through GitHub APIs without a local checkout; remote refs, commits, trees, and Actions runs are inspected.

## Completed multi-bundle work

- Excel grouped/multi-row headers with retained raw header metadata.
- Conservative exact semantic mappings with collision and ambiguity handling.
- Relationship discovery/validation based on exact key overlap and cardinality; no automatic joins.
- Versioned BusinessSchemaCatalog.
- Declarative BundleRegistry and explicit composite rule registry.
- Requirement extraction and versioned requirement payload validation.
- Composite shared-context guard.
- BundleCapabilityResolver with missing/ambiguous field checks, same-table co-location checks, required relationship/cardinality validation, and unverified business capability reporting.
- Production runtime builds one schema catalog per business from the same ingested tables used by Executor and supplies it to that business's CompositePlanner.

## Capability-resolution contract

- Collection declares payment-event amount and payment date as required canonical fields.
- Revenue has no flat required-field tuple: Executor supports alternative direct-line and detail-to-order source shapes. Do not model those as one same-table field list.
- Payment source role, settled-payment policy, revenue source shape, eligible-sales semantics, sale-period meaning, and order-status semantics remain unverified.
- Both default financial bundles remain unavailable under catalog-gated planning until the missing evidence is modeled and validated.
- The resolver never executes joins or infers business semantics from header names/sample values.

## Verification

GitHub Actions run 44555242526 executed 242 tests. 240 passed; the only two failures were the inherited repository-hygiene checks against CODEX PROGRESS (size limit and secret-like regex). The bundle resolver, runtime gate, and runner regression tests passed. No hygiene checks were weakened and the inherited file was not modified.

Run: https://github.com/pl2n/DataMate/actions/runs/44555242526

## Next step

Inspect the current rulebook contract and executor source discovery in detail. Design a versioned business-rule evidence model for revenue source alternatives, payment source role/status handling, and rule-profile provenance. Do not mark default bundles available based on headers or sample values alone. Keep automatic joins, arbitrary conjunction splitting, and new metrics out of scope.


## Business-rule evidence contract — 2026-11-19

- Added `schemas/business_rule_evidence.v1.schema.json` and strict stdlib reader `src/datamate/rule_evidence.py`.
- Added profile-scoped, allowlisted assertions for revenue source shape, eligible sales amount, sale-period meaning, order-status semantics, payment source role, and settled-payment policy.
- Each claim requires exact table scope and provenance (source type/reference, SHA-256, reviewer, timezone-aware timestamp).
- Unknown claims/assertions, duplicate profiles/claims, malformed provenance, and business-ID mismatches fail closed.
- Verified claims count only when every scoped table matches the business catalog's exact table name and source.
- No evidence is synthesized from column names or sample values. This milestone does not enable either default bundle or change Executor behavior.

Tests added: `tests/test_rule_evidence.py`. Design note: `docs/BUSINESS_RULE_EVIDENCE.md`.

## Next step

Integrate validated evidence with `BundleCapabilityResolver` and per-business runtime loading. Require `payment_status` for a collection bundle because the current executor only filters to successful payment statuses when that column exists. Keep absent/invalid evidence fail-closed.


### Business-rule evidence CI

- Commit: `f6d5115ea4099311ed3d01eeb0257abfa37818c4`.
- GitHub Actions run `44556933123`: 250 tests executed; all 8 new business-rule evidence tests passed. 248 tests passed overall; the only two failures are the inherited `CODEX PROGRESS` repository-hygiene checks.
- Run: https://github.com/pl2n/DataMate/actions/runs/44556933123
- Follow-up docs guide: `docs/BUSINESS_RULE_EVIDENCE.md`.


## Business-rule evidence runtime integration — 2026-11-19

- Added per-business loading from `data/<business_id>/business_rule_evidence.json`.
- Passed validated evidence through `main.run` → `CompositePlanner` → `BundleCapabilityResolver`.
- Trace records evidence status (`loaded`, `missing`, `invalid`) and capability-resolution reasons.
- Collection composite requires canonical `payment_event_amount`, `payment_date`, and `payment_status` in one table. Role and settled-status claims must scope the same table.
- Payment executor recognizes grouped payment amount/date/status headers and prefers the explicit payment-status column. Legacy generic-status fallback remains for ordinary single-metric queries.
- Revenue detail-to-order evidence requires exact ordered line/order scope and a validated many-to-one `order_id` relationship.
- CI run `44558398515`: 256 tests, 254 passed; only the two inherited `CODEX PROGRESS` hygiene checks failed. All feature tests passed.

Run: https://github.com/pl2n/DataMate/actions/runs/44558398515

## Next step

Validate evidence assertions against the active split rulebook and executor profile, and design safe source-digest verification using controlled, known source locations. Do not enable capabilities on a claim whose policy contradicts runtime behavior.


## Final checkpoint for this work session

- Runtime code commit: `02dc61c983de696ded042f021e2f64f2b886c8e6`.
- Documentation/schema clarification commit: `96d63298a940a0e449c7303bbe668508d74c0637`.
- CI run `44559194129` on the documentation/schema commit: 256 tests, 254 passed; only the two inherited `CODEX PROGRESS` hygiene checks failed. Feature tests passed.
- Next work: validate business-rule assertions against actual split-rulebook semantics and design controlled digest verification.

## Evidence-scope hardening — 2026-11-19

- Collection's three required canonical fields are now checked only inside the exact one-table scope shared by payment-source-role and settlement-policy claims.
- Revenue detail-to-order checks accept the validated relationship in either catalog edge orientation (many-to-one line→order or one-to-many order→line), while the evidence scope remains ordered line table then order table.
- Unsupported flexible source-shape assertions are not accepted; only direct_line and detail_to_order are supported.
- Added regression tests for out-of-scope payment fields, reversed catalog order, and a valid evidence-backed end-to-end runner execution.
- Latest CI run 44560238399: 259 tests executed; 257 passed. Only the two inherited CODEX PROGRESS hygiene checks failed.
- Run: https://github.com/pl2n/DataMate/actions/runs/44560238399

## Next step

Review the evidence file's provenance against controlled, known source locations and define a safe digest-verification path. Do not fetch arbitrary external references or infer reviewer attestations.


## Rulebook/executor conformance — 2026-11-19

- Added parsed `revenue_amount_basis`, `revenue_period_basis`, and optional `collection_status_policy` to SplitRules.
- The evidence resolver now checks revenue claims against the active rulebook: line amount after line discount, matching period basis, and exclusion of cancelled/returned/failed-delivery outcomes.
- Collection's `successful_status_only` claim is accepted only if the active rulebook contains an explicit supported collection-status clause.
- Added `classify_payment_status` and changed collected-amount execution to use it instead of the order-status classifier. Unknown payment statuses abstain; recognized pending/failed/cancelled/refunded states are excluded.
- Regression coverage includes `Đã thanh toán`, `Chờ thanh toán`, failed, cancelled, refunded, unknown status, and evidence/rulebook mismatch.
- The actual mounted rulebook is supplied at runtime and is not committed here. Its collection clause has not been inspected in this repository; absence means the collection bundle remains unavailable.


## CI verification — 2026-11-19

GitHub Actions run `44561508605` on commit `211941c8b8bdaafabd5f0c85477f1ce99bdf041b` executed 264 tests. 262 passed, including all feature tests. The only two failures remain the inherited `CODEX PROGRESS` large-file and secret-like-pattern hygiene checks.

Run: https://github.com/pl2n/DataMate/actions/runs/44561508605

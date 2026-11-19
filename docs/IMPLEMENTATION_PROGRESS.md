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

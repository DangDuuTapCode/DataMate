# Checkpoint — business-rule evidence runtime integration (2026-11-19)

## Runtime flow

`main.run` reads optional `data/<business_id>/business_rule_evidence.json` and validates it with the v1 contract. Valid evidence is passed to the per-business CompositePlanner and BundleCapabilityResolver. Missing, malformed, or wrong-business evidence blocks composite planning and is recorded in the trace. The ordinary single-metric path remains available.

## Capability safeguards

- Collection requires `payment_event_amount`, `payment_date`, and `payment_status` to map unambiguously and co-occur in one table.
- `payment_source_role` and `settled_payment_status_policy` evidence must be verified and scoped to the same exact table.
- Executor resolves grouped payment headers for amount/date/status and prefers an explicit payment-status field. A generic-status fallback remains for ordinary single-metric queries, but cannot satisfy the composite schema gate.
- Revenue `direct_line` evidence scopes one table.
- Revenue `detail_to_order` evidence scopes line table first and order table second, and requires a validated many-to-one `order_id` relationship.
- Revenue amount/date/status evidence scopes must be contained within the declared source-shape scope.

## Traceability

Trace records `business_rule_evidence.status` as `loaded`, `missing`, or `invalid`, and records bundle capability resolutions/reasons.

## CI

Run `44558398515` on commit `02dc61c983de696ded042f021e2f64f2b886c8e6`: 256 tests; 254 passed. All feature tests passed. Only the two inherited `CODEX PROGRESS` hygiene checks failed.

Run: https://github.com/pl2n/DataMate/actions/runs/44558398515

## Remaining work

Cross-check claims against the actual split rulebook and executor profile. SHA-256 is currently recorded and format-checked but not recomputed from external references; design digest verification using controlled, known source locations rather than arbitrary file paths.


## Session verification and handoff

Latest runtime code commit: `02dc61c983de696ded042f021e2f64f2b886c8e6`. Latest documentation/schema commit: `96d63298a940a0e449c7303bbe668508d74c0637`.

CI run `44559194129` executed 256 tests; 254 passed, including all feature tests. The only two failures were inherited repository-hygiene checks.

Next milestone: validate evidence assertions against actual split-rulebook/executor semantics and design controlled source digest verification.

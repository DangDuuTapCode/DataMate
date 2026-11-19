# Bundle capability resolution

## Purpose

The BundleRegistry describes allowlisted metric bundles. BundleCapabilityResolver checks structural requirements against BusinessSchemaCatalog and reviewed business-rule claims against BusinessRuleEvidence. It never performs joins or infers business meaning from column names or sample values.

## Structural requirements

A resolution is available only when:
- every required canonical field has an unambiguous exact semantic mapping;
- all required fields are co-located in at least one source table;
- every declared relationship has validated status and the required cardinality;
- no required relationship is rejected or ambiguous.

The result distinguishes missing/ambiguous fields, field-group conflicts, missing/rejected relationships, unverified/rejected business capabilities, and the rule-profile version.

## Business-rule evidence

The v1 contract is defined in `schemas/business_rule_evidence.v1.schema.json` and read by `src/datamate/rule_evidence.py`. A business supplies an optional file at:

`data/<business_id>/business_rule_evidence.json`

Every verified claim is scoped to exact `table_name` and `source` identities and carries source type/reference, SHA-256, reviewer, and timezone-aware review timestamp. The runtime rejects unknown/malformed claims, wrong business IDs, and scope mismatches. SHA-256 is recorded and format-checked, but this version does not reopen arbitrary references to recompute the digest.

## Revenue source alternatives

Revenue supports:
- `direct_line`: evidence scope must identify exactly one table.
- `detail_to_order`: evidence scope must list the line table first and order table second. The schema catalog must contain a validated many-to-one `order_id` relationship from the first table to the second.

Revenue amount, period, and status claims must be scoped within the declared source-shape tables. The executor remains the final guard for actual source columns and data quality.

## Collection requirements

The composite collection bundle requires three exact canonical fields co-located in one payment table:
- `payment_event_amount`
- `payment_date`
- `payment_status`

The `payment_source_role` and `settled_payment_status_policy` claims must both be verified and scoped to the same single table. The accepted policy is `successful_status_only`.

The executor recognizes grouped payment amount/date/status headers and prefers the explicit payment-status column. A legacy generic-status fallback is retained for ordinary single-metric queries, but it cannot satisfy the composite capability gate.

## Runtime behavior

`main.run` loads evidence per business and passes it to CompositePlanner and BundleCapabilityResolver. Missing or invalid evidence blocks composite planning and is recorded in the trace as `missing` or `invalid`; capability-resolution details explain the block. The ordinary single-metric path remains available.

No default evidence file is generated. A bundle becomes available only when structural requirements and all required reviewed claims pass. No automatic join is authorized by a validated relationship.

## Verification

GitHub Actions run `44558398515` executed 256 tests; 254 passed. All feature tests passed. The only two failures are inherited repository-hygiene checks against the upstream `CODEX PROGRESS` artifact.

Run: https://github.com/pl2n/DataMate/actions/runs/44558398515


## Active rulebook compatibility

A verified evidence payload is necessary but not sufficient. The resolver cross-checks revenue amount, period, and order-status assertions against the active `SplitRules`. It also requires the collection successful-status-only assertion to match an explicit supported clause in the active rulebook. Missing collection policy leaves that bundle unavailable.

The collection executor uses a dedicated payment-status classifier, separate from `classify_order_status`. Unknown payment labels cause abstention; recognized pending, failed, cancelled, refunded, or reversed states are excluded.


## Execution scope binding

The resolver returns the exact approved table identities and, for revenue, the reviewed source shape. CompositePlanner carries these into each QueryComponent. At runtime, main creates a component-specific Executor over only those exact tables. Revenue's direct-line and detail-to-order assertions are also enforced by the Executor; a detail-to-order claim disables the direct-candidate shortcut and uses the existing validated detail/order path.

This prevents a second, unreviewed candidate table from being selected after the capability gate has approved a different table. Missing scope identities fail closed.


## Provenance verification

Runtime recomputes SHA-256 from exact bytes of allowlisted files only. Rulebooks resolve to the input-root `rulebook.md`; data dictionaries and operator attestations resolve to fixed filenames inside the business directory. Path traversal, external URLs, unknown names, missing files, any symlink source, paths resolving outside the input root, and digest mismatches fail closed.

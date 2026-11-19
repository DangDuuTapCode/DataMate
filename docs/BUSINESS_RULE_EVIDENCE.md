# Business-rule evidence contract

## Purpose

A semantic column mapping or matching table name is structural evidence only. It does not prove that a value represents eligible revenue, a payment event, or a settled collection. This contract records reviewed business-rule assertions with provenance and exact table scope.

## Version 1 payload

The JSON Schema is `schemas/business_rule_evidence.v1.schema.json`; the strict Python reader is `src/datamate/rule_evidence.py`.

A payload is scoped to one `business_id` and contains versioned profiles:
- `revenue_rules`
- `collection_rules`

Every capability record contains:
- a known capability ID;
- status: `verified`, `unverified`, or `rejected`;
- a capability-specific allowlisted assertion (required for verified records);
- exact `table_name` + `source` scope;
- provenance: source type, reference, SHA-256, reviewer, and timezone-aware review timestamp.

Unknown capability IDs, assertions, profiles, duplicate records, malformed provenance, and business-ID mismatches fail closed. The reader does not generate evidence from headers, sample values, filenames, or the current executor's output.

## Supported assertions in v1

| Profile | Capability | Accepted assertion |
|---|---|---|
| revenue_rules | revenue_executor_source_shape | direct_line / detail_to_order |
| revenue_rules | eligible_sales_amount | line_amount_after_line_discount |
| revenue_rules | sale_period | order_date / delivery_date / sales_date |
| revenue_rules | order_status_semantics | exclude_cancelled_returned_failed |
| collection_rules | payment_source_role | payment_event_or_receipt |
| collection_rules | settled_payment_status_policy | successful_status_only |

These are a closed vocabulary, not automatic proof. A reviewer must confirm the assertion against an authoritative rulebook or data dictionary and record the source digest. A verified claim counts only when every scoped table exists in the matching business schema catalog with the exact table name and source.

## Runtime integration

The runtime reads an optional per-business file at `data/<business_id>/business_rule_evidence.json`. It passes a valid contract into `CompositePlanner` and then to `BundleCapabilityResolver`. Missing, malformed, wrong-business, rejected, or incorrectly scoped evidence leaves the corresponding bundle unavailable. The trace records evidence status and capability-resolution reasons.

Additional safeguards:
- Collection requires `payment_event_amount`, `payment_date`, and `payment_status` as unambiguous canonical fields co-located in one table.
- The payment-source and settled-status claims must refer to the same exact table identity.
- The executor recognizes grouped payment headers and selects the explicit payment-status column. Its legacy fallback remains for ordinary single-metric queries; the composite gate will not authorize that fallback without a canonical status mapping.
- Revenue `detail_to_order` evidence requires an ordered scope of line table then order table and a validated many-to-one `order_id` relationship. A direct-line claim must scope exactly one table.
- Revenue amount/date/status claims must be scoped within the declared source-shape tables.

The SHA-256 value is recorded and format-checked; this version does not reopen arbitrary external references to recompute the digest. The reviewer is responsible for ensuring it matches the cited source. No default evidence file is generated and no business rule is inferred.

The ordinary single-metric execution path is unchanged. Composite planning remains fail-closed when evidence is missing or invalid.

## Scope enforcement regression coverage

The capability resolver now enforces that collection amount/date/status mappings
exist in the exact single table named by both the payment-source-role and
settlement-policy claims. Identical columns in an unreviewed table do not
satisfy the bundle.

For revenue detail-to-order assertions, evidence scope is ordered as line table
then order table. The resolver accepts the relationship validator's equivalent
orientation forms: line-to-order many-to-one, or order-to-line one-to-many,
because the catalog's edge direction follows input table order. A one-to-one
validated edge is also non-multiplying and accepted. Missing, rejected,
ambiguous, or conflicting relationship evidence blocks the bundle.

A direct-line assertion must scope exactly one table. The currently supported
source-shape assertions remain the closed values direct_line and
detail_to_order.

An end-to-end runner test now proves that a valid, correctly scoped evidence
file can enable both default components and produce a verified side-by-side
result. Missing and malformed evidence continue to abstain.

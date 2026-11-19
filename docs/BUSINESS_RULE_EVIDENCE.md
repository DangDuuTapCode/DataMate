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

## Runtime boundary

This milestone introduces the versioned contract and strict reader. It does not automatically mark either default bundle available, alter executor calculations, infer missing policies, or enable new query intents. The subsequent integration step must pass validated evidence into `BundleCapabilityResolver` and preserve the fail-closed default when evidence is absent or scoped to a different table/business.

Collection status deserves particular care: the existing executor filters rows to statuses classified as successful only when a payment-status column exists. A safe bundle gate must therefore require an unambiguous `payment_status` field as well as reviewed policy evidence; it must not accept a status-less payment table as proof of settled collections.

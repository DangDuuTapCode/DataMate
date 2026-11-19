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

The ordinary single-metric execution path is unchanged. Composite planning remains fail-closed when evidence is missing or invalid.

## Scope enforcement regression coverage

The capability resolver now enforces that collection amount/date/status mappings exist in the exact single table named by both the payment-source-role and settlement-policy claims. Identical columns in an unreviewed table do not satisfy the bundle.

For revenue detail-to-order assertions, evidence scope is ordered as line table then order table. The resolver accepts the relationship validator's equivalent orientation forms: line-to-order many-to-one, or order-to-line one-to-many, because the catalog's edge direction follows input table order. A one-to-one validated edge is also non-multiplying and accepted. Missing, rejected, ambiguous, or conflicting relationship evidence blocks the bundle.

A direct-line assertion must scope exactly one table. The currently supported source-shape assertions remain the closed values `direct_line` and `detail_to_order`.

An end-to-end runner test now proves that a valid, correctly scoped evidence file can enable both default components and produce a verified side-by-side result. Missing and malformed evidence continue to abstain.

## Active-rulebook conformance

Reviewed claims are checked against the active `SplitRules` object before they can satisfy a bundle:
- `eligible_sales_amount` must match the parsed line-amount-after-line-discount rule.
- `sale_period` must match the active order/delivery/sales date basis.
- `order_status_semantics` is accepted only when the executor rule profile excludes cancelled, returned, and failed-delivery orders.
- `settled_payment_status_policy` is accepted only when the active rulebook explicitly states that only successful payment transactions count as collected money. If this clause is absent, collection remains unavailable.

The executor classifies payment statuses independently from order statuses. Explicit paid/successful states are included; pending, failed, cancelled, refunded, and reversed states are excluded. Unknown statuses cause abstention. This prevents order-status semantics from being reused as proof of payment settlement.

## Execution uses the approved source scope

The resolver returns exact approved table identities. `CompositePlanner` stores that scope on each component, and `main` creates a component-specific `Executor` over only those tables. The reviewed revenue source shape is also passed to `Executor`, so `detail_to_order` cannot silently fall back to a direct-line candidate. This closes the gap between capability validation and actual table selection.

## Provenance digest verification

At runtime, every evidence claim's SHA-256 is recomputed from the exact bytes of a strictly allowlisted local file:
- `rulebook.md` at the input root;
- `data_dictionary.csv`, `data_dictionary.xlsx`, or `data_dictionary.md` inside the business data directory;
- `README.md` inside the business data directory (the contest input uses this file to document file roles, columns, and data conventions);
- `operator_attestation.json` inside the business data directory.

A business-local `README.md` is accepted only as a named schema/documentation source under the existing `data_dictionary` provenance type. This does not turn README content into verified evidence automatically: a reviewer must still create the evidence record, identify the exact table scope, and verify the claim against the relevant rulebook or documented source. The runtime only verifies that the referenced bytes match the recorded digest.

An optional fragment after `#` is treated only as a citation anchor; it is never interpreted as a path. Absolute paths, separators, traversal, URLs, unknown filenames, missing files, any symlink source, files resolving outside the input root, and digest mismatches invalidate the evidence. No external URL is fetched. The digest proves that the referenced local file matches the recorded bytes; it does not independently authenticate the reviewer's identity or create a cryptographic signature.


## Confirmed contest input layout (2026-11-19)

The supplied `Contest.zip` has two separate input roots:
- `Contest/train/`: 30 business directories (`biz_101`–`biz_130`), 3,000 questions, answers, a calendar, and its own `rulebook.md`.
- `Contest/public_test/`: 14 business directories (`dev_001`–`dev_014`), 1,000 questions, a calendar, and a separate `rulebook.md`.

Each root follows the runtime layout expected by DataMate: `rulebook.md`, `questions.jsonl`, `calendar.csv`, and `data/<business_id>/`. Run the two splits with their respective root directories; do not combine their business folders under one root because their rulebooks are distinct.

The business-local `README.md` files are present in this input and document source files, table grain, column meanings, key relationships, units, and shop-specific conventions. They are now an explicitly named, digest-verifiable schema/documentation source. The input does not include a separate `data_dictionary.*` or `operator_attestation.json` file in the inspected business directories.

The train and public-test rulebooks are not byte-identical. The public-test rulebook adds further conventions, including cash-by-shift semantics, weekday averages, extra customer/employee rankings, and industry-specific rules for mother-and-baby shops, vehicle repair, and phone shops. Always load the rulebook from the selected split root.

Neither supplied rulebook contains the explicit successful-payment-only policy clause recognized by `SplitRules`. Therefore `collection_status_policy` remains unsupported for these contest inputs, and the collection bundle must stay unavailable. Payment columns or a payment table alone are not sufficient to prove which statuses count as collected money.

The archive is an evaluation corpus, not a source of automatic business-rule attestations. Do not synthesize `business_rule_evidence.json` from filenames, headers, sample values, or README text alone.

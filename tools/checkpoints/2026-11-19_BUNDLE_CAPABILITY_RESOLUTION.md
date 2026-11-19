# Bundle capability resolution checkpoint — 2026-11-19

## Scope

Connected declarative bundle requirements to the business schema catalog without changing existing metric calculations or executing joins.

## Changes

- BundleDefinition now declares required canonical fields and optional RequiredRelationship specifications.
- Default revenue bundle declares order_total_after_discount, order_date, and order_status.
- Default collection bundle declares payment_event_amount, payment_date, and payment_status.
- BundleCapabilityResolver checks exact mapped fields and validated relationship status/cardinality.
- Required fields must co-occur in at least one source table. A bundle cannot be satisfied by combining unrelated fields across tables.
- Resolution reports missing_fields, ambiguous_fields, field_group_conflicts, missing_relationships, rejected_relationships, unverified_capabilities, and reason codes.
- CompositePlanner accepts an optional schema_catalog. When present, every component bundle must pass the resolver before a plan is created.

## Safety boundary

A BusinessSchemaCatalog is structural evidence, not a business rulebook. A payment_status header does not establish which values are settled, and a mapped sales amount does not prove all revenue eligibility/exclusion rules. The default financial bundles therefore remain unavailable under catalog-gated planning until those business capabilities are separately evidenced. This is intentional fail-closed behavior.

No joins are performed. Existing executor logic is unchanged. No parser cues or arbitrary natural-language splitting were added.

## Tests

Added synthetic tests for:
- exact required field mappings;
- missing and ambiguous fields;
- required-field co-location;
- validated relationship/cardinality;
- missing and rejected relationships;
- CompositePlanner catalog gating;
- default financial bundles blocked by unverified business-rule capabilities.

GitHub Actions verification is pending at checkpoint creation. The known two upstream repository-hygiene failures remain separate and unchanged.

## Next step

Review how the existing executor discovers source columns and how rule profiles are represented. Define a versioned business-rule evidence contract before allowing default revenue/collection bundles to become available. Do not infer settled-payment or eligible-sales semantics from headers or sample values alone.

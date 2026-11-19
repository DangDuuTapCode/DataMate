# Bundle capability resolution checkpoint — 2026-11-19

## Scope

Connected declarative bundle requirements to the business schema catalog without changing existing metric calculations or executing joins.

## Changes

- BundleDefinition now declares required canonical fields and optional RequiredRelationship specifications.
- Collection declares payment_event_amount and payment_date as its required fields.
- Revenue has no flat required-field list yet: the executor accepts alternative direct-line and detail-to-order source shapes, which cannot be represented accurately by one same-table field tuple.
- Both default bundles retain unverified source-role/business-rule capabilities and remain unavailable under catalog-gated planning.
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


## CI result

GitHub Actions run 44554164419 executed 241 tests. 239 passed; the only two failures were the known inherited CODEX PROGRESS repository-hygiene checks (size limit and secret-like regex). All feature tests for field mapping/co-location, relationship validation, and planner gating passed. No hygiene checks were weakened and no upstream file was modified.

Run: https://github.com/pl2n/DataMate/actions/runs/44554164419
## Executor contract correction and production wiring

Executor inspection showed that revenue has two supported source shapes: a
direct line-grain table with date, line amount, and product identity, or a
detail table linked to a unique dated/statused order table. The current flat
required-field model cannot safely express that alternative, so the default
revenue bundle intentionally declares no flat required-field list and remains
unavailable due to unverified source-shape/business-rule capabilities.

Collection requires payment-event amount and payment date in a payment-role
table. Status is optional in current source discovery, so its absent/present
policy remains an unverified capability. The main pipeline now builds a
BusinessSchemaCatalog once per business and supplies it to that business's
CompositePlanner, activating the gate in production.

CI for this correction is pending.


## Source-shape refinement

Executor inspection confirmed that revenue supports two alternative source shapes (direct line-grain facts or detail-to-order), so no flat required-field tuple is declared for revenue yet. Collection requires payment-event amount and payment date; payment source role and settled-payment policy remain unverified. The resolver therefore keeps both default bundles unavailable under catalog-gated planning.

Latest runtime CI run `44555242526`: 242 tests, 240 passed; the only failures are the two inherited repository-hygiene checks. The runtime-gating regression passed.

## Runtime wiring verification

Production main.run now constructs a BusinessSchemaCatalog per business and passes it to the corresponding CompositePlanner. The runner regression confirms that header mappings alone do not enable the default financial composite.

Latest CI: run 44555242526, 242 tests executed, 240 passed. The only two failures were inherited CODEX PROGRESS hygiene checks. Feature tests passed.

Run: https://github.com/pl2n/DataMate/actions/runs/44555242526

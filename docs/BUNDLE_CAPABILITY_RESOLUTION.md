# Bundle capability resolution

## Purpose

The BundleRegistry describes which metric bundles are allowlisted. A bundle can
declare exact canonical fields and validated relationship shapes required by
its implementation. BundleCapabilityResolver checks those declarations
against a BusinessSchemaCatalog; it does not execute queries or joins.

## Resolution contract

A resolution is available only when all declared structural requirements pass:

- every required canonical field has an unambiguous exact semantic mapping;
- all required fields are co-located in at least one source table;
- every required relationship has a validated status and the declared cardinality;
- no required relationship is rejected or ambiguous.

The result reports missing fields, ambiguous fields, field-group co-location
conflicts, missing relationships, rejected relationships, unverified business
capabilities, and reason codes. Fields found in unrelated tables cannot be
combined to satisfy a single bundle's same-table field requirement.

## Important boundary

A schema catalog proves structural observations, not business meaning. A
mapped payment_status column does not prove which values count as settled.
The collection executor currently requires a payment-role table, payment-event
amount, and payment date; status is optional in its current source discovery,
so the business policy for absent/present status remains unverified.

Revenue has deliberately not been assigned a flat required-field list. Its
executor supports either a direct line-grain source (date, line amount, and
product identity) or a detail-to-order path (line amount and line identity
linked to a dated/statused order table). A flat same-table tuple would misstate
that contract. A future schema contract must represent these alternatives and
their validated relationship path before revenue can be marked available.

Existing default financial bundles therefore retain unverified source-role
and business-rule capability labels. Until a separately reviewed evidence
source validates them, the resolver reports the bundle as unavailable.

The current revenue and collection calculations remain unchanged. No automatic
joins are introduced. A bundle with no unverified rule capabilities can be
resolved as available from exact field/relationship evidence alone.
## Production integration

The pipeline entry point builds a BusinessSchemaCatalog once per business and
passes it to that business's CompositePlanner. Thus catalog-gated capability
resolution is active in production planning, not merely exposed as an optional
test-only API.

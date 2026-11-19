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

A schema catalog proves structural observations, not business meaning. For
example, a mapped payment_status column does not prove which values count as
settled, and order_total_after_discount does not by itself establish all
revenue eligibility/exclusion rules. Existing default financial bundles
therefore retain their business-rule capability labels. Until a separately
reviewed rulebook/evidence source can validate those labels, the resolver
reports the bundle as unavailable even when all structural fields are present.

The current revenue and collection calculations remain unchanged. No automatic
joins are introduced. A bundle with no unverified rule capabilities can be
resolved as available from exact field/relationship evidence alone.

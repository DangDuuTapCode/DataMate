# Checkpoint — declarative metric bundle registry (2026-11-19)

## Scope

Replace the hard-coded metric-to-bundle tuple in the composite planner with an explicit registry, without broadening query understanding or changing calculations.

## Implementation

- Added `src/datamate/bundles.py`.
- Added immutable `BundleDefinition` and validated `BundleRegistry`.
- Default registry contains `revenue` and `collected_amount` only.
- Each definition records bundle ID, metric ID, existing executor intent, output type, required capability labels, rule-profile label, and period/entity support.
- Updated `CompositePlanner` to resolve its existing fixed financial pair through the registry.
- Unknown and duplicate metric requirements fail closed.

## Boundaries

- No arbitrary conjunction parsing.
- No dynamic source-table discovery.
- No new metric execution.
- No changes to revenue or collection calculation rules.
- Capability labels are declarative requirements, not yet validated against every source schema.

## Tests

Synthetic tests cover default definitions, unknown/duplicate requirement resolution, duplicate metric/bundle rejection, and output-type allowlisting.

## Next

1. Run GitHub Actions and inspect the results.
2. Add a versioned bundle metadata schema if definitions stabilize.
3. Generalize requirement extraction only after bundle resolution has a clear, testable contract.

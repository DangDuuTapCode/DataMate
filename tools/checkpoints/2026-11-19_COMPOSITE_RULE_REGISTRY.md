# Checkpoint — explicit composite rule registry (2026-11-19)

## Scope

Decouple recognized composite-intent combinations from the requirement extractor and composite planner.

## Implementation

- Added `CompositeRule` and `CompositeRuleRegistry` in `requirements.py`.
- Each rule declares a QuerySpec intent, an ordered metric list, and comparison type.
- Default registry contains only `financial_metric_comparison` → `revenue` + `collected_amount`.
- Requirement extraction resolves each metric through `BundleRegistry`.
- `CompositePlanner` now accepts any explicitly registered composite intent and compiles its requirements; unregistered intents remain unsupported.

## Boundaries

- No arbitrary conjunction splitting.
- No new natural-language parser cues.
- No new production metric combinations in the default registry.
- Only side-by-side comparison is supported.
- Component type, period/entity support, requirement schema, execution, and verification gates remain in force.

## Tests

Synthetic tests cover duplicate/invalid rule definitions, custom allowlisted metric composition, and unregistered-intent abstention.

## Next

1. Run CI and inspect all failures.
2. Keep the default registry limited until new metric combinations have source and business-rule evidence.
3. Add explicit parser rules separately for any new combination.

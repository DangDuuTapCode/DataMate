# Checkpoint — versioned requirement extraction contract (2026-11-19)

## Scope

Give extracted multi-metric requirements a versioned, validated JSON contract before composite plan compilation.

## Implementation

- Added `schemas/requirement_extraction.v1.schema.json`.
- Added JSON-native payload serialization and validation in `requirements.py`.
- Exposed the existing schema-subset validator as `query_schema.validate_payload`.
- Composite planning validates the requirement payload before creating component plans.
- Cross-field invariants enforce:
  - resolved composite has at least two requirements;
  - requirement IDs and metric IDs are unique;
  - resolved payload has no failure reason;
  - unresolved/unsupported payload has no executable requirements and includes a reason.

## Tests

Synthetic tests cover valid resolved payloads, duplicate metric rejection, unresolved payload validity, and failure-reason/status mismatch.

## Boundaries

- Does not broaden the supported composite intent.
- Does not split arbitrary conjunctions.
- Does not enable new metrics or joins.

## Next

1. Run CI and inspect all failures.
2. Add a plan-level schema only if it contributes additional validation beyond the requirement contract.
3. Generalize supported requirement combinations with explicit cue and compatibility tests.

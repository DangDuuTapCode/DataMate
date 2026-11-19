# Checkpoint — requirement extraction layer (2026-11-19)

## Scope

Separate recognized multi-metric requirement extraction from composite query plan compilation.

## Implementation

- Added `src/datamate/requirements.py`.
- Added `MetricRequirement`, `RequirementExtraction`, and `RequirementExtractor`.
- First allowlisted extraction rule: `financial_metric_comparison` → `revenue` + `collected_amount`.
- Requirement records include ID, metric, bundle, executor intent, expected output type, required capability labels, and rule-profile label.
- Updated `CompositePlanner` to consume extracted requirements and resolve each through `BundleRegistry`.

## Boundaries

- No arbitrary `and` / `và` splitting.
- No new metric combinations.
- No dynamic bundle discovery.
- No changes to metric calculation or component verification.
- Unknown, single, unresolved, unsupported-output, or unsupported-context requests fail closed.

## Tests

Synthetic tests cover resolved two-requirement extraction, single/unknown intent rejection, missing bundle resolution, and existing composite planning/execution behavior.

## Next

1. Run CI and inspect all failures.
2. Add an explicit serialized composite-query schema for the requirement contract.
3. Expand requirement extraction only with separate cue-level regressions and an explicit supported-combination policy.


## Requirement extraction CI result

The first workflow run found a stale type annotation after moving the requirement model; it was fixed in commit `45330bc6accdc30e38eff31217422c3f01121253`. Follow-up run `44548881088` executed 222 tests with no code/test errors; 220 passed. The only failures are the two pre-existing repository-hygiene checks against `CODEX PROGRESS`.

Run: https://github.com/pl2n/DataMate/actions/runs/44548881088

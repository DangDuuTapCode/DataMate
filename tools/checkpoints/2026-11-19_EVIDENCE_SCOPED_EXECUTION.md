# Checkpoint — evidence-scoped execution (2026-11-19)

## Problem

Capability resolution checked exact reviewed table identities, but the runtime still passed the full business table set to every component Executor. This left a gap between the table approved during planning and the table selected during execution.

## Changes

- `BundleCapabilityResolution` now returns `approved_table_scope` and `executor_source_shape`.
- Revenue scope comes from the exact verified source-shape claim.
- Collection scope comes from the exact single table shared by the verified payment-role and settlement-policy claims.
- `QueryComponent` carries the approved scope and source shape.
- `main.run` creates a component-specific Executor using only tables whose exact `(name, source)` identities are approved.
- A missing scoped table causes `source_scope_mismatch` abstention.
- Executor receives the reviewed revenue shape:
  - `direct_line` selects exactly one direct fact candidate.
  - `detail_to_order` skips direct-candidate selection and uses the existing detail/order path.

## Regression coverage

- End-to-end composite test now includes a second, unreviewed sales table and a second, unreviewed payment table with otherwise valid-looking fields. The result must still use only the two reviewed tables.
- Pipeline test places an order-summary table with a tempting direct amount alongside line details; when the reviewed shape is `detail_to_order`, the Executor must use the line-detail join rather than the direct summary amount.
- Resolver tests assert the exact scope returned for collection and revenue.

## Verification

CI pending for this checkpoint commit. The previous CI run `44561793925` executed 264 tests; 262 passed, with only the two inherited `CODEX PROGRESS` hygiene failures. No local checkout or local test execution is available.

## Next

Implement source digest verification without allowing arbitrary path traversal or external fetching. Evidence references should resolve only to a controlled allowlist of files under the runtime input root; compute SHA-256 over the exact bytes and compare it to the reviewed digest. Preserve abstention when source bytes cannot be safely resolved.

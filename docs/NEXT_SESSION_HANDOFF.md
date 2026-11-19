# Next-session handoff — 2026-11-19

## Repository

Continue on `pl2n/DataMate`, branch `feature/multi-bundle-query`. Do not modify upstream `DangDuuTapCode/DataMate`; do not create a PR unless requested.

Latest branch head before runtime wiring:
`17ac08fbee0b3cd634cfe1501d9ea213ed8cd46c`.

There is no local checkout in this session, so a literal `git status` has not been run. Inspect GitHub refs, commits and trees for remote branch state.

## Completed architecture

See `docs/IMPLEMENTATION_PROGRESS.md`, `docs/MULTI_BUNDLE_QUERY.md`, and dated checkpoints under `tools/checkpoints/`. Completed pieces include grouped-header ingestion, semantic mappings, relationship validation, business schema catalog, bundle registry, requirement extraction/schema, composite rule registry, shared-context guard, and bundle capability resolution.

## Capability-resolution contract

Implementation:
- `src/datamate/bundle_capabilities.py`
- `src/datamate/bundles.py`
- `tests/test_bundle_capabilities.py`
- `docs/BUNDLE_CAPABILITY_RESOLUTION.md`

The resolver checks exact canonical fields, same-table co-location, and explicitly declared validated relationship cardinality. It reports missing/ambiguous fields and unverified business-rule capabilities. It never executes joins or infers business semantics.

Important source-shape correction:
- Revenue supports either direct line facts or a detail-to-order path. Do not model this as one flat same-table field list until the schema contract can express alternatives and the required relationship path.
- Collection currently requires payment-event amount and payment date. Its payment source role and settled-payment policy remain unverified.
- Both default bundles stay unavailable under catalog-gated planning until source-role and business-rule evidence is modeled and validated.

## Active next step — wire the gate into runtime

Inspect `src/datamate/main.py`. Before this slice, runtime instantiated `CompositePlanner(planner)` without a catalog, so the optional gate could be bypassed.

Build one `BusinessSchemaCatalog` per business from the same ingested tables used by its `Executor`, and pass that catalog into a per-business `CompositePlanner`. Add a runner test proving that mapped headers alone do not enable the financial composite while business-rule capabilities remain unverified.

After CI, record the resulting commit and run URL here, in `docs/IMPLEMENTATION_PROGRESS.md`, `tools/STATE.md`, and a dated checkpoint. Keep arbitrary conjunction parsing, automatic joins, and new metrics out of scope.

# Next-session handoff — 2026-11-19

## Repository

Continue on pl2n/DataMate, branch feature/multi-bundle-query. Do not modify upstream DangDuuTapCode/DataMate; do not create a PR unless requested.

Implementation commit: c06e7c42befd1500d743219ab1a3ec3883213ef8. Work was performed through GitHub APIs; no local checkout or literal local git status is available.

## Completed architecture

See docs/IMPLEMENTATION_PROGRESS.md, docs/MULTI_BUNDLE_QUERY.md, and dated checkpoints under tools/checkpoints/. Completed pieces include grouped-header ingestion, semantic mappings, relationship validation, business schema catalog, bundle registry, requirement extraction/schema, composite rule registry, shared-context guard, and bundle capability resolution.

## Capability-resolution contract

Implementation:
- src/datamate/bundle_capabilities.py
- src/datamate/bundles.py
- tests/test_bundle_capabilities.py
- docs/BUNDLE_CAPABILITY_RESOLUTION.md

The resolver checks exact canonical fields, same-table co-location, and explicitly declared validated relationship cardinality. It reports missing/ambiguous fields and unverified business-rule capabilities. It never executes joins or infers business semantics.

Source-shape constraints:
- Revenue supports either direct line facts or a detail-to-order path. Do not model this as one flat same-table field list until the schema contract can express alternatives and the required relationship path.
- Collection currently requires payment-event amount and payment date. Its payment source role and settled-payment policy remain unverified.
- Both default bundles stay unavailable under catalog-gated planning until source-role and business-rule evidence is modeled and validated.

## Production runtime

src/datamate/main.py builds a BusinessSchemaCatalog once per business from the same ingested tables used by Executor, then passes it to a per-business CompositePlanner. A runner regression proves that mapped headers alone do not enable the financial composite while business-rule capabilities remain unverified.

## Verification

GitHub Actions run 44555242526 executed 242 tests: 240 passed. The only two failures are the inherited CODEX PROGRESS size and secret-like-regex hygiene checks. Feature tests passed.

Run: https://github.com/pl2n/DataMate/actions/runs/44555242526

## Active next step

Inspect src/datamate/split_rules.py, the actual mounted rulebook contract, and Executor source discovery. Design a versioned business-rule evidence contract for:
- alternative revenue source shapes and the relationship path for detail-to-order;
- payment table role and the policy when payment status is absent or present;
- rule-profile version, source provenance, and validation status.

Do not infer business semantics from column names or sample values. Keep automatic joins, arbitrary natural-language splitting, and new metrics out of scope.

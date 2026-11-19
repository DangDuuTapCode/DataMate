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


## Business-rule evidence contract — latest milestone

Implemented:
- `schemas/business_rule_evidence.v1.schema.json`
- `src/datamate/rule_evidence.py`
- `tests/test_rule_evidence.py`
- `docs/BUSINESS_RULE_EVIDENCE.md`

The v1 payload is scoped to one business and contains versioned `revenue_rules` / `collection_rules` profiles. Each capability assertion has a closed allowlisted value, explicit exact table scope, and provenance (source type/reference, SHA-256, reviewer, timezone-aware review timestamp). Unknown or duplicate claims, unsupported assertions, malformed provenance, and business-ID mismatches are rejected.

Important boundaries:
- This is a strict contract/reader only. It does not synthesize evidence from headers/sample values, change executor calculations, or enable default bundles.
- Verified claims count only if all exact scoped table identities exist in the matching BusinessSchemaCatalog.
- Collection's current executor only applies successful-status filtering when a payment status column exists. The next integration must require an unambiguous `payment_status` field for the collection bundle and keep it unavailable when status is absent.
- Revenue source shape assertions need to match actual direct-line or detail-to-order executor paths; do not let an attestation silently authorize an unimplemented path.

## Next step

Wire the optional per-business evidence file (suggested path: `data/<business_id>/business_rule_evidence.json`) into `main.run`, `CompositePlanner`, and `BundleCapabilityResolver`. Missing/invalid/mismatched evidence must leave the bundle unavailable. Add tests for both valid and invalid runtime evidence. No automatic joins, fuzzy inference, or parser expansion.

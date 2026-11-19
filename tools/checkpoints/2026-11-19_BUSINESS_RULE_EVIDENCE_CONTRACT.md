# Checkpoint — versioned business-rule evidence contract (2026-11-19)

## Purpose

Create a strict, provenance-backed contract for the business semantics that a structural schema catalog cannot prove.

## Files

- `schemas/business_rule_evidence.v1.schema.json`
- `src/datamate/rule_evidence.py`
- `tests/test_rule_evidence.py`
- `docs/BUSINESS_RULE_EVIDENCE.md`

## Contract

A payload belongs to one business and contains versioned revenue/collection profiles. Each capability claim has:
- a closed capability ID and allowlisted assertion;
- status `verified`, `unverified`, or `rejected`;
- exact table name/source scope;
- source type/reference/SHA-256, reviewer, and timezone-aware review timestamp.

The strict Python reader rejects unknown profiles/capabilities/assertions, duplicates, malformed provenance, and business ID mismatch. Verified claims are returned only when all scoped tables exist in the exact business schema catalog.

## Semantics and boundaries

The contract covers:
- revenue executor source shape;
- eligible sales amount;
- sale-period meaning;
- order-status semantics;
- payment source role;
- settled-payment status policy.

It does not generate evidence from column names or samples, enable default bundles, perform joins, or change executor behavior. The next integration must require `payment_status` for collection because successful-status filtering is conditional on that column in the current executor. Revenue evidence must match the actual direct-line/detail-to-order implementation path.

## Next milestone

Load `data/<business_id>/business_rule_evidence.json` per business, pass validated evidence through CompositePlanner to BundleCapabilityResolver, require exact business/table scope, and keep missing/invalid evidence fail-closed. Add runtime and resolver tests before considering any capability executable.

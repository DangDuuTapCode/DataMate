# Checkpoint — runtime wiring for bundle capability gate (2026-11-19)

## Context

The schema-based `BundleCapabilityResolver` was CI-verified, but inspection of `src/datamate/main.py` found that runtime still instantiated `CompositePlanner(planner)` without a catalog. Since the planner's catalog gate is optional for compatibility, production orchestration could bypass the check.

## Bounded change

- Build a `BusinessSchemaCatalog` from the exact tables read for each business.
- Reuse those same tables for the business `Executor` and the catalog.
- Keep a per-business `CompositePlanner` that receives the catalog.
- Add a runner regression: even when sales and payment headers map structurally, a composite query abstains while source-role/business-rule capabilities remain unverified.

## Source-shape constraints

Revenue supports alternative direct-line and detail-to-order source shapes; do not force these into a flat required-field tuple. Collection requires payment-event amount and payment date, while payment source-role and settled-payment policy remain unverified.

## Safety

No joins, new metrics, rule inference, or parser expansion. The ordinary single-metric path is unchanged. Default composite financial bundles remain fail-closed pending validated business-rule evidence.

## Verification

GitHub Actions run 44555242526 executed 242 tests: 240 passed. The only two failures were the inherited CODEX PROGRESS size and secret-like-regex hygiene checks. The runtime-gating runner regression passed.

Run: https://github.com/pl2n/DataMate/actions/runs/44555242526


## CI result — runtime wiring

GitHub Actions run `44555207826` on commit `c2f965d9ff0f06c14a68ed212660a92b50d1754a` executed 242 tests. The runtime-gating regression passed; 240 tests passed overall. The only two failures were the inherited `CODEX PROGRESS` size-limit and secret-like-pattern checks. Follow-up documentation commit: `c06e7c42befd1500d743219ab1a3ec3883213ef8`.

Run: https://github.com/pl2n/DataMate/actions/runs/44555207826

# Current state — 2026-11-19

- Repository: pl2n/DataMate (user fork).
- Branch: feature/multi-bundle-query.
- Upstream DangDuuTapCode/DataMate: do not modify.
- Implementation commit: c06e7c42befd1500d743219ab1a3ec3883213ef8.
- Work uses GitHub APIs; no local checkout or local git status was available.
- Completed: grouped-header ingestion, semantic mappings, relationship validation, schema catalog, bundle registry, requirement extraction/schema, composite rule registry, shared-context guard, bundle capability resolver, and production runtime catalog gating.
- Revenue source alternatives and collection source-role/status semantics remain unverified. Default financial composites must fail closed until evidence contracts are implemented.
- Latest CI: run 44555242526; 242 tests, 240 passed; two inherited CODEX PROGRESS hygiene failures. Do not weaken checks or alter that inherited artifact.
- Next: inspect split_rules.py and Executor source discovery; design a versioned business-rule evidence contract for source shapes, status semantics, rule-profile version, and provenance.
- Source of truth: docs/NEXT_SESSION_HANDOFF.md, docs/IMPLEMENTATION_PROGRESS.md, docs/MULTI_BUNDLE_QUERY.md, and dated checkpoints.


## Business-rule evidence contract

- Added versioned contract `schemas/business_rule_evidence.v1.schema.json` and strict reader `src/datamate/rule_evidence.py`.
- Evidence is business/profile scoped, uses closed capability/assertion vocabularies, exact table identities, SHA-256 provenance, reviewer, and timezone-aware review timestamp.
- No default bundle is enabled; no executor calculation is changed.
- Next: integrate per-business evidence into capability resolution and runtime. Collection bundle must require unambiguous payment_status because executor filtering is conditional on its presence.


## Latest verified commit

- Branch head: `f6d5115ea4099311ed3d01eeb0257abfa37818c4` (business-rule evidence contract and test expectation correction).
- CI run `44556933123`: 250 tests; 248 passed, including all new evidence-contract tests. Only the two inherited `CODEX PROGRESS` hygiene checks failed.
- Run: https://github.com/pl2n/DataMate/actions/runs/44556933123


## Latest business-rule evidence runtime state

- Runtime loads `data/<business_id>/business_rule_evidence.json` and passes valid evidence into composite capability resolution.
- Missing/invalid evidence is recorded in trace and blocks composite planning.
- Collection composite requires payment-event amount, payment date, and payment status; status and source-role claims must be scoped to the same exact table.
- Revenue detail-to-order evidence requires a validated many-to-one `order_id` relationship.
- CI run `44558398515`: 256 tests, 254 passed; two inherited hygiene failures only. Feature tests passed.
- Next: cross-check claims against the actual split rulebook/executor profile and design safe digest verification.


## Session close state

- Runtime integration commit: `02dc61c983de696ded042f021e2f64f2b886c8e6`.
- Latest docs/schema commit: `96d63298a940a0e449c7303bbe668508d74c0637`.
- CI run `44559194129`: 256 tests, 254 passed; only two inherited `CODEX PROGRESS` hygiene failures.
- Next: validate evidence assertions against actual rulebook/executor behavior and add safe digest verification.

## Evidence-scope hardening

- Collection's payment amount/date/status fields must be co-located in the exact table scoped by both reviewed collection claims.
- Revenue detail-to-order validates the line/order relationship independent of catalog edge orientation; direct_line evidence must scope one table.
- End-to-end valid-evidence runner test passes; missing/invalid evidence still blocks.
- Latest CI run 44560238399: 259 tests, 257 passed; only two inherited CODEX PROGRESS hygiene failures.
- Next: design controlled source-digest verification; never fetch arbitrary external references.


## Rulebook/executor conformance

- Payment statuses are classified independently from order statuses; unknown payment states abstain.
- SplitRules exposes revenue amount/date semantics and an optional collection status policy.
- Resolver cross-checks evidence against the active SplitRules. Collection's successful-only policy requires an explicit active rulebook clause.
- CompositePlanner passes the active SplitRules into bundle capability resolution.
- The mounted runtime rulebook is not committed. Do not assume it contains the collection clause.


## Latest verified conformance milestone

- Payment status has its own classifier; unknown labels abstain.
- Evidence assertions are checked against active SplitRules; collection requires an explicit successful-only rulebook clause.
- CompositePlanner passes active SplitRules into capability resolution.
- CI run `44561508605`: 264 tests; 262 passed. All feature tests passed; only two inherited CODEX PROGRESS hygiene failures.
- Next: bind evidence-approved table scope to Executor candidate selection; then implement controlled digest verification.

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

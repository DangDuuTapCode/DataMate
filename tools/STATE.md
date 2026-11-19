# DataMate current state — 2026-11-19

## Repository

- Work only in fork `pl2n/DataMate`, branch `feature/multi-bundle-query`.
- Do not modify upstream `DangDuuTapCode/DataMate`; do not create a PR unless requested.
- GitHub API workflow only; no local checkout, local git status, or local test execution.
- Latest implementation baseline: `a6eade98f01e55326ae53bf6423800868b6f77b3`.
- Latest documentation commits: `bc01731c4e445841bbff72ab32b74bbcc18dfb6e` (provenance guide) and `382a75c33fb0bf51617dde33cee1ba172854ef65` (handoff).

## Implemented

- Grouped Excel headers and retained header metadata.
- Exact semantic mapping with ambiguity handling; relationship validation without automatic joins. Key families include order/customer/product/payment receipt plus employee, supplier, purchase receipt, batch/lot, branch, and IMEI; generic row numbers/reference labels remain unmapped.
- BusinessSchemaCatalog, bundle registry, requirement extraction/schema, composite rules, and shared-context guard.
- BundleCapabilityResolver checks exact canonical fields, co-location, validated relationships, and explicit business-rule evidence.
- Runtime constructs per-business catalogs/planners and records evidence/capability decisions.
- SplitRules/executor conformance for revenue amount/date/status semantics and collection successful-payment policy.
- Dedicated payment-status classifier; unknown values abstain.
- Evidence-approved exact table scope and revenue source shape are enforced by component-specific Executors.
- Business-rule evidence v1 contract and strict local SHA-256 provenance verification.

## Safety and capability boundaries

- Missing, malformed, wrong-business, rejected, incorrectly scoped, unsupported, or digest-invalid evidence blocks composite execution.
- Revenue source shape must be explicitly reviewed as `direct_line` or `detail_to_order`; detail-to-order requires a validated `order_id` relationship.
- Collection requires payment-event amount/date/status in the exact single table scoped by both source-role and settlement-policy claims.
- Collection remains unavailable unless the active rulebook explicitly states the supported successful-payment-only policy.
- Provenance allowlist remains narrow: input-root `rulebook.md`; business-local `data_dictionary.csv/.xlsx/.md` or `README.md`; business-local `operator_attestation.json`. README is treated as schema documentation only and never auto-generates evidence.
- SHA-256 proves byte correspondence only; it does not authenticate reviewer identity or provide a signature.
- No arbitrary path access, automatic joins, fuzzy inference, arbitrary conjunction splitting, or new metrics.

## CI

- Run `44564104588` on commit `a6eade98f01e55326ae53bf6423800868b6f77b3`: 272 tests; 270 passed. All feature tests passed. Two inherited `CODEX PROGRESS` hygiene checks failed (large-file limit and secret-like-pattern false positive).
- Run: https://github.com/pl2n/DataMate/actions/runs/44564104588
- Two docs-only commits followed that run; inspect their Actions results before further code edits.
- Never weaken or modify the inherited hygiene artifact to hide those failures.

## Contest archive and current blocker

The user supplied `Contest.zip`, inspected on 2026-11-19:
- Train root: 30 businesses, 3,000 questions, answers, calendar, and train rulebook.
- Public-test root: 14 businesses, 1,000 questions, calendar, and a separate public-test rulebook.
- Both roots match the runtime's expected directory layout. Every inspected business has a local `README.md` with source/column/table-grain documentation; separate data dictionaries and operator attestations are absent.
- Train and public-test rulebooks differ; each split must be run with its own root.
- Neither rulebook contains the explicit successful-payment-only policy clause. Collection remains unavailable.

Committed after archive inspection:
- `47649aa3ba70ddaaa363986d7beb2a81ba0a8a5f` README provenance allowlist.
- `fa402eae2862463f30a0d3403e7d0c7f82e5c819` README digest regression test.
- `a33ccdd32355f163069c47872e42acdb87b79489` evidence documentation.
- `7edf33b418cce8ed782cc64282c8b7376f08ce40` implementation progress update.
- `f5c73cdef1de583c094507344e270966f3044129` handoff update.

Next: audit public-test questions against the 14 input shapes, then build minimal synthetic fixtures for representative multi-source queries. Do not add the full archive to Git. The new code/test commits still need a verified Actions result. No local checkout or local test run is available.

## Latest multi-source expansion

- Exact aliases and relationship-key families expanded based on Contest.zip schemas.
- Added synthetic tests for exact aliases and six many-to-one relationship families.
- Commits: `8ff2c09`, `37f66c3`, `a784b4f`, `2d866ee`, `a64ba34`, `0465e9d`, `dccf1ba`, `45b3667`, `9d2ceab`.
- CI for these changes is not yet verified. The last known baseline remains run `44565561293` (272 tests; 270 passed, two inherited hygiene failures).

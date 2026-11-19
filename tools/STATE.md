# DataMate current state — 2026-11-19

## Repository

- Work only in fork `pl2n/DataMate`, branch `feature/multi-bundle-query`.
- Do not modify upstream `DangDuuTapCode/DataMate`; do not create a PR unless requested.
- GitHub API workflow only; no local checkout, local git status, or local test execution.
- Latest implementation baseline: `a6eade98f01e55326ae53bf6423800868b6f77b3`.
- Latest documentation commits: `bc01731c4e445841bbff72ab32b74bbcc18dfb6e` (provenance guide) and `382a75c33fb0bf51617dde33cee1ba172854ef65` (handoff).

## Implemented

- Grouped Excel headers and retained header metadata.
- Exact semantic mapping with ambiguity handling; relationship validation without automatic joins.
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
- Provenance allowlist remains narrow: input-root `rulebook.md`; business-local `data_dictionary.csv/.xlsx/.md`; business-local `operator_attestation.json`.
- SHA-256 proves byte correspondence only; it does not authenticate reviewer identity or provide a signature.
- No arbitrary path access, automatic joins, fuzzy inference, arbitrary conjunction splitting, or new metrics.

## CI

- Run `44564104588` on commit `a6eade98f01e55326ae53bf6423800868b6f77b3`: 272 tests; 270 passed. All feature tests passed. Two inherited `CODEX PROGRESS` hygiene checks failed (large-file limit and secret-like-pattern false positive).
- Run: https://github.com/pl2n/DataMate/actions/runs/44564104588
- Two docs-only commits followed that run; inspect their Actions results before further code edits.
- Never weaken or modify the inherited hygiene artifact to hide those failures.

## Active blocker / next step

The actual mounted business input files are not in the GitHub repository. `data/` is gitignored except for `data/README.md`. The repository does not establish the exact real filenames or placement for a data dictionary or operator attestation.

Obtain the actual input directory listing/input contract and mounted `rulebook.md`. Only then may exact additional filenames or parser support be added. Until then, keep the allowlist narrow and both default financial bundles evidence-gated.

See `docs/NEXT_SESSION_HANDOFF.md` for the continuation checklist and `docs/IMPLEMENTATION_PROGRESS.md` for milestone history.

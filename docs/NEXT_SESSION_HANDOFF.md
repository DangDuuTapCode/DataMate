# Next-session handoff — 2026-11-19

## Repository and working rules

- Continue only on `pl2n/DataMate`, branch `feature/multi-bundle-query`.
- This is the user's fork. Do not modify upstream `DangDuuTapCode/DataMate` and do not create a PR unless explicitly requested.
- Work is performed through GitHub APIs; there is no local checkout. Do not claim a local `git status` or local test execution.
- Commit completed milestones frequently and update this handoff/checkpoint.
- Current branch head: `c1b3b4cea609d52d29620ee41a798d260e99dfe6`.
- Latest implementation baseline: `a6eade98f01e55326ae53bf6423800868b6f77b3`; continuation commits since then are documentation/checkpoint-only.

## Completed implementation

- Excel grouped/multi-row header ingestion with raw header metadata.
- Conservative semantic mappings, collision/ambiguity handling, and exact key relationship validation.
- Versioned business schema catalog.
- Declarative bundle registry, requirement extraction contract/schema, and composite rule registry.
- Shared-context safety checks for composite query components.
- Bundle capability resolution based on exact canonical fields, table co-location, validated relationship cardinality, and explicit business-rule evidence.
- Per-business runtime schema catalog and composite planner wiring.
- Versioned business-rule evidence contract with closed capability/assertion vocabulary, exact table scope, provenance metadata, and strict parsing.
- SplitRules/executor conformance checks for revenue amount basis, period basis, order-status exclusions, and collection successful-status policy.
- Payment status has its own conservative classifier; unknown statuses abstain.
- Evidence-approved table scope is passed into component-specific Executors. Revenue source shape is enforced as either `direct_line` or `detail_to_order`.
- Runtime recomputes SHA-256 from exact bytes of allowlisted local provenance files. Arbitrary paths, traversal, URLs, unknown filenames, missing files, symlinks, paths outside the input root, and digest mismatches fail closed.
- Documentation has been synchronized; see `docs/BUSINESS_RULE_EVIDENCE.md`, `docs/IMPLEMENTATION_PROGRESS.md`, `tools/STATE.md`, and `tools/checkpoints/2026-11-19_CONTINUATION_REVIEW.md`.

## Current capability boundaries

- Default financial bundles must remain unavailable unless their structural and business-rule evidence is verified.
- Revenue supports reviewed `direct_line` or `detail_to_order` source shapes. The latter requires a validated `order_id` relationship and ordered line-table then order-table scope.
- Collection requires payment amount, payment date, and explicit payment status in one exact reviewed table. Source-role and successful-status-policy claims must refer to that same table.
- Collection remains unavailable if the active rulebook does not explicitly support the successful-payment-only policy.
- No automatic joins, fuzzy semantic inference, arbitrary natural-language conjunction splitting, or new metrics.
- SHA-256 verification proves byte correspondence with an allowlisted local source; it does not authenticate the reviewer's identity or provide a cryptographic signature.

## Verification

- GitHub Actions run `44565561293` on `5a6085264796a9a2c413a1323cba5e96b5f9e0a7`: 272 tests; 270 passed.
- All feature tests passed. The only two failures are inherited `CODEX PROGRESS` repository-hygiene checks (large-file limit and a secret-like-pattern false positive). Do not weaken the checks or modify that inherited artifact.
- Run: https://github.com/pl2n/DataMate/actions/runs/44565561293
- The subsequent checkpoint commit `c1b3b4cea609d52d29620ee41a798d260e99dfe6` only adds documentation; no CI run for that commit was visible at the time of this handoff.
- No local checkout or local test execution is available in this workflow.

## Active next step — confirm real input contract

The repository's `data/` directory is for mounted competition input and is gitignored (except `data/README.md`). The actual runtime bundle is not available through the GitHub repository. No exact data-dictionary or operator-attestation filename/placement is documented by the checked-in input contract.

Before expanding the provenance allowlist:
1. Obtain the actual business input directory listing or the relevant input-contract files.
2. Confirm exact filenames and placement for any data dictionary or operator attestation.
3. Add only explicitly confirmed names to the allowlist and tests.
4. Inspect the actual mounted `rulebook.md` to determine whether its collection policy clause matches the parser's supported rule.

Do not guess filenames, broaden to arbitrary paths, or enable bundles from synthetic tests alone. If the actual bundle cannot be provided, leave the allowlist unchanged and record the blocker.

## Useful files

- `src/datamate/rule_evidence.py`
- `src/datamate/bundle_capabilities.py`
- `src/datamate/split_rules.py`
- `src/datamate/metrics.py`
- `src/datamate/main.py`
- `tests/test_rule_evidence.py`
- `tests/test_bundle_capabilities.py`
- `tests/test_api.py`
- `docs/BUSINESS_RULE_EVIDENCE.md`
- `docs/BUNDLE_CAPABILITY_RESOLUTION.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `tools/STATE.md`

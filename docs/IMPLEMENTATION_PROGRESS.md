# DataMate implementation progress — 2026-11-19

## Repository and workflow

- Repository: `pl2n/DataMate` (user fork only).
- Branch: `feature/multi-bundle-query`.
- Upstream `DangDuuTapCode/DataMate` is untouched; no PR is open.
- Changes are made through GitHub APIs. There is no local checkout, so no local `git status` or local test execution is claimed.
- Current branch head at this checkpoint: `6fde7f8211ec488f860255da7bb7e5f6e7809cab`.

## Implemented architecture

### Ingestion and schema understanding
- Excel grouped/multi-row headers are retained and combined with leaf headers when the workbook has clear merged group headings.
- Semantic mapping uses conservative exact aliases and grouped-header context. Ambiguous/colliding fields are not silently selected.
- Relationship discovery uses exact key overlap, uniqueness, cardinality, blanks, and unmatched values. It validates candidates but does not execute joins.
- A versioned `BusinessSchemaCatalog` stores table schemas and relationship evidence.

### Multi-bundle planning
- Declarative bundle registry and explicit composite-rule registry.
- Versioned requirement extraction contract and schema validation.
- Shared-context guards prevent composite components from silently dropping filters, dimensions, sorting, or unsupported top-k context.
- Composite planner supports only allowlisted intents/rules; arbitrary conjunction splitting and new metrics remain out of scope.

### Business-rule evidence and capability resolution
- `schemas/business_rule_evidence.v1.schema.json` and `src/datamate/rule_evidence.py` define strict business/profile-scoped evidence.
- Capability IDs and assertions use a closed vocabulary. Every claim has exact table scope and provenance metadata.
- Resolver checks exact canonical fields, same-table co-location, validated relationship cardinality, and active SplitRules compatibility.
- Payment status uses a dedicated classifier. Unknown statuses abstain; pending, failed, cancelled, refunded, and reversed states are not treated as settled.
- Collection requires amount/date/status in the exact table scoped by both payment-source-role and settlement-policy claims.
- Revenue supports reviewed `direct_line` or `detail_to_order` source shapes. Detail-to-order requires an ordered line/order scope and validated `order_id` relationship.
- Runtime creates component-specific Executors over only evidence-approved tables and enforces the reviewed revenue source shape.
- Missing, malformed, wrong-business, rejected, out-of-scope, unsupported, or digest-invalid evidence blocks composite execution. Ordinary single-metric execution remains separate.

### Provenance verification
- Runtime recomputes SHA-256 from exact bytes of allowlisted local sources:
  - input-root `rulebook.md`;
  - business-local `data_dictionary.csv`, `.xlsx`, or `.md`;
  - business-local `operator_attestation.json`.
- Arbitrary paths, traversal, URLs, unknown filenames, missing files, symlink source files, paths outside the input root, and digest mismatches fail closed.
- SHA-256 establishes byte correspondence, not reviewer identity or a cryptographic signature.
- `docs/BUSINESS_RULE_EVIDENCE.md` was corrected to match the runtime behavior and to state the digest limitation accurately.

## Current capability policy

- Do not enable either default financial bundle merely because synthetic tests pass or headers appear plausible.
- Collection stays unavailable unless the active mounted rulebook explicitly supports the successful-payment-only policy.
- Revenue/collection source roles and exact business semantics require reviewed evidence.
- No automatic joins, fuzzy semantic inference, arbitrary query conjunction splitting, or new metrics.

## Verification

GitHub Actions run `44565385010` on branch head `6fde7f8211ec488f860255da7bb7e5f6e7809cab` executed 272 tests:
- 270 passed, including all feature tests.
- The only two failures are inherited repository-hygiene checks against the existing `CODEX PROGRESS` artifact: large-file limit and secret-like-pattern false positive.
- These checks were not weakened and the inherited artifact was not modified.

Run: https://github.com/pl2n/DataMate/actions/runs/44565385010

## Active blocker and next step

The actual mounted business input bundle is not available in the repository. The `data/` directory is gitignored except for `data/README.md`; the checked-in docs do not establish the exact real filenames or placement for a data dictionary or operator attestation.

Next:
1. Obtain the actual business input directory listing or authoritative input contract.
2. Confirm exact filenames and placement for data dictionary/operator attestation before expanding the provenance allowlist.
3. Inspect the actual mounted `rulebook.md` and verify its collection policy clause.
4. Add only evidence-backed filename/parser support and corresponding tests.
5. Keep bundles unavailable until source roles, business rules, and table scopes are verified.

See `docs/NEXT_SESSION_HANDOFF.md` for the resume checklist and `tools/STATE.md` for the compact current state.

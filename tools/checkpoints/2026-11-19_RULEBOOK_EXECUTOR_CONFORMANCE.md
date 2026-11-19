# Checkpoint — rulebook/executor conformance (2026-11-19)

## Starting point

Branch head at the beginning of this milestone:
`ab834e246fdfe36d4b2025b32bbfeace0c36f5aa`.

The mounted runtime rulebook is supplied under the input data root and is not committed in this repository. Synthetic fixtures are used for tests only.

## Findings

- Collection execution reused `classify_order_status` for payment rows.
- Order and payment status vocabularies are not interchangeable. A valid `Đã thanh toán` label was not explicitly recognized by the order classifier.
- The existing SplitRules reader exposed revenue date/status defaults but no collection settlement clause.
- A reviewed evidence assertion must not authorize a policy the active SplitRules object does not support.

## Changes

- Added `classify_payment_status` in `src/datamate/rules.py`, independent from order status classification.
- Collection execution now includes recognized successful/paid states; excludes known pending, failed, cancelled, refunded/reversed states; and abstains on unknown statuses.
- SplitRules now exposes:
  - `revenue_amount_basis`
  - `revenue_period_basis`
  - optional `collection_status_policy`
- SplitRules recognizes collection policy only through an explicit allowlisted rulebook row and a successful-only clause.
- BundleCapabilityResolver cross-checks revenue amount/date/status claims against active SplitRules and only accepts collection settlement policy evidence when the active rulebook supports the same assertion.
- CompositePlanner passes the active SplitRules into capability resolution.
- Evidence schema remains closed: only exact source-shape alternatives are accepted; the resolver's obsolete flexible source-shape branch was removed.
- Added synthetic regressions for payment status classes, unknown payment status, rulebook policy absence, revenue date mismatch, and incomplete unsuccessful-order exclusions.

## Safety boundary

If the actual mounted rulebook lacks the explicit collection status policy, the collection bundle remains unavailable. No status semantics are inferred from a header, filename, or sample value.

## Verification

CI is pending for the commit that records this checkpoint. No local checkout exists, so no local test command or local git status is claimed.

## Next work

1. Inspect the CI run and resolve any feature-test regressions.
2. Ensure the exact table scope approved by evidence is also the table scope used by Executor. In particular, verify revenue candidate selection cannot execute against a different, unreviewed candidate table.
3. Design safe SHA-256 verification against known files under the input root. Never follow arbitrary evidence-provided paths.

# Bundle evidence scope validation checkpoint — 2026-11-19

## Scope

Harden reviewed business-rule evidence against table-scope mismatch and relationship edge orientation.

## Changes

- Collection required fields (payment_event_amount, payment_date, payment_status) are checked only in the exact single table shared by both payment_source_role and settled_payment_status_policy claims.
- Revenue detail_to_order evidence keeps an ordered table scope (line table, then order table), but relationship validation accounts for catalog edge orientation: many_to_one line→order or one_to_many order→line. A validated one_to_one relation is also non-multiplying.
- direct_line evidence must scope exactly one table.
- Only the closed supported source-shape assertions direct_line and detail_to_order are accepted.
- Added tests for fields existing only outside the reviewed collection scope, reverse catalog table order, and valid evidence-backed runtime execution.

## Verification

GitHub Actions run 44560238399 executed 259 tests; 257 passed. The only two failures are the inherited CODEX PROGRESS size and secret-like-regex hygiene checks. All feature tests passed.

Run: https://github.com/pl2n/DataMate/actions/runs/44560238399

## Next

Design controlled source-digest verification using known local source locations. Do not retrieve arbitrary external references or treat a syntactically valid SHA-256 value as proof of correspondence.

# Checkpoint — Contest biz_129 LEFT JOIN contract

Date: 2026-11-20
Branch: `feature/query-specific-join-execution`

## User-provided source

- Archive: uploaded `Contest.zip` (308 entries).
- Inspected in place; not added to repository.
- Authoritative source materials used: `Contest/train/data/biz_129/README.md`, `Contest/train/rulebook.md`, and `Contest/train/questions.jsonl`.

## Case selected

Customer-group revenue queries:
- `q_264a7294b457`
- `q_6ee842fa8f92`
- `q_635440e343cc`
- `q_d361c00c6829`

Data profile measured from archive:
- Sales lines: 145,479.
- Orders: 38,499, unique order key.
- Customers: 220, unique customer key.
- Payment events: 38,072 rows, 37,748 distinct order IDs, maximum 4 payment events per order.
- Orders with known customer ID: 23,309, all match customer catalog.
- Orders with blank customer ID: 15,190.

## Key semantic finding

The rulebook says guest orders do not belong to any customer group, but they still contribute to whole-shop revenue. The correct full-grain path from sales lines through orders to customers must therefore preserve blank customer IDs via LEFT JOIN. Payment events are a separate fact and must not be joined directly to sales lines because multiple payment events can multiply sales-line revenue.

## Changes committed

- Semantic mapping: README-scoped aliases for `Số CT`, `Số phiếu`, and `Mã giao dịch` based on exact source role.
- Relationship discovery: `validated_left_join` state when target keys are unique, all nonblank source keys match, and source blank keys exist.
- Relationship paths: `left_join_required` status and per-hop flag.
- FactJoinContract: refuses INNER JOIN if any hop requires LEFT JOIN.
- Tests: source-context alias tests, blank-key relationship/path/contract tests, synthetic biz_129-shaped integration test.
- Docs: `docs/CONTEST_BIZ129_JOIN_CASE.md`, updates to implementation progress, changelog, state, and handoff.

## Guardrails

- No Contest archive or source records were committed.
- No runtime Executor/Planner wiring was enabled.
- The structural contract does not apply date/status filters or compute customer-group numerator/whole-shop denominator.
- Payment-event aggregation remains a separate future component.
- No local tests were run. GitHub Actions has not surfaced a workflow run/status for this branch; CI remains unverified.

## Next work

1. Open a draft PR from this branch to upstream `main` to obtain CI results, then inspect/fix failures.
2. Review the new relationship status against every consumer; existing bundle capability resolution should continue to ignore `validated_left_join` because it accepts only ordinary `validated`.
3. Design query execution for a three-table path with explicit LEFT JOIN, revenue eligibility/date filters, customer-group numerator, whole-shop denominator, and a separate payment-event grain.
4. Only then wire a narrowly allowlisted query family; do not enable arbitrary joins.

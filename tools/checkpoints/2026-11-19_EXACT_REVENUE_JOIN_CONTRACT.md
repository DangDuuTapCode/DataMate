# Exact approved revenue join contract — 2026-11-19

## Problem

The composite capability resolver verified a specific source-qualified `order_id` relationship, but the detail-to-order Executor independently searched headers to rediscover key columns. The validated physical key columns were not part of the execution contract.

A second issue was found in the same path: exact duplicate detail rows were silently dropped even when the active rulebook did not authorize that treatment.

## Changes

- `src/datamate/bundle_capabilities.py`
  - Added `RevenueJoinContract`.
  - Captures exact line and order table identities (table name + source filename), canonical key set, and physical key-column indices.
  - Resolver creates the contract only for exactly one source-matched validated `order_id` edge with safe line-to-order cardinality.
  - Normalizes edge orientation so schema catalog ordering does not change the contract.
- `src/datamate/composite.py`
  - Carries the approved contract on `QueryComponent`.
- `src/datamate/main.py`
  - Passes the contract to the component Executor after applying exact table scope.
- `src/datamate/metrics.py`
  - Executor accepts the contract.
  - When supplied, detail-to-order execution restricts itself to the exact source-qualified line/order tables and uses the validated physical key-column indices.
  - If an exact duplicate line is encountered, it is skipped only when `SplitRules.deduplicate_identical_order_lines` is true; otherwise the calculation abstains.
  - Legacy single-metric behavior without a supplied contract remains unchanged.
- Tests cover resolver contract serialization, reversed catalog ordering, exact executor key-index use, duplicate handling with/without rulebook authorization, and the existing joined-revenue fixture now states the policy explicitly.

## Verification

GitHub Actions run `44577298652` for commit `21469c4be7a3d93e5bd2befb879315f3c9c36afd`:
- 286 tests executed.
- 284 passed.
- All feature tests passed.
- Two inherited repository hygiene failures remain: `test_no_large_files` and `test_no_secret_like_strings`, both reporting the existing `CODEX PROGRESS` artifact.
- No local checkout or local test execution was used.

Run URL: https://github.com/pl2n/DataMate/actions/runs/44577298652

## Commits

- `c00cd0ecabbeff8b9064fb704b61f6af39dabcdd`
- `11cbcb02afdc496d74c03a96ba22f26a3248c7ac`
- `ea7f156db237a258dff4c12abd43665bac87b6ed`
- `9b20c0bc2871d1fa9b2deef91d643481936d707e`
- `5e05f2b2ef948a8518a2915fc2974200e03b56c9`
- `d926caebc0dbb6ab3cc8ece2717ec8843bd36277`
- `09cef4347e767acb6122c9d10c7005e262ebe179`
- `004306dc46041dced471cbc970250ad90baca779`
- `72e94d6f1614a9bf0aca7d5183d83f7e6191d0d5`
- `3ae99663419ee0a3d7a6f51cad85edadfb28c490`
- `f3a8bd4340c58d2e4776442d75091880ac3214ab`
- `059b931f1b4d531814469def5e28f5f517c397ec`
- `21469c4be7a3d93e5bd2befb879315f3c9c36afd`

## Remaining limitations / next work

This is a narrow detail-to-order revenue contract, not a general join planner. Composite-key lot allocation and polymorphic stock-ledger document references remain discovery-only. Next work should define a query-specific execution contract for one representative multi-source question, with explicit grain preservation and fan-out checks, rather than enabling arbitrary joins.

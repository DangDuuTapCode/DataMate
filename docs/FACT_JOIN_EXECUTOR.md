# Explicit fact join executor

## Purpose

`execute_fact_join_contract(tables, contract)` executes one already-approved `FactJoinContract`. It is a low-level primitive, not a natural-language planner and not an automatic join engine.

The function returns `FactJoinResult` or `None` when any contract, schema, key, or table check fails.

## Guarantees

- Uses exact source-qualified table identities from the contract.
- Revalidates that every canonical join key still maps to the declared physical column indices.
- Allows only declared `many_to_one` and `one_to_one` hops with `fanout=False`.
- Rebuilds a unique target-key index for every hop; duplicate nonblank target keys fail closed.
- Requires every nonblank source key reached from the fact rows to match. It never silently drops unmatched nonblank fact rows.
- Blank source keys are accepted only when the hop carries `requires_left_join=True` and the contract uses `join_type="left"`.
- Preserves one output row per original fact row, including duplicate fact lines. It never deduplicates facts.
- Preserves identifier text exactly after trimming; it does not case-fold or numerically coerce keys, so leading zeroes remain significant.
- Keeps table rows separate and source-qualified rather than flattening columns with colliding names.

`FactJoinResult.column(table_identity, column_index)` returns a row-aligned tuple for a source column. A missing LEFT JOIN match is represented by `None`.

## Explicit non-goals

The executor does not:
- infer relationships or choose a path;
- apply business filters, date windows, order-status rules, or customer-group filters;
- aggregate, sum, deduplicate, or calculate ratios;
- join payment-event facts into sales-line facts;
- decide whether a measure is additive or whether the declared fact grain is true.

Those responsibilities remain with reviewed query/rule evidence and a future query-specific metric executor.

## Current integration boundary

The module is covered by synthetic multi-hop tests, but it is not yet wired into `Executor.execute`, `RulePlanner`, or the public query pipeline. The Contest `biz_129` case study motivates the path and LEFT JOIN requirement; it does not authorize arbitrary joins.

# P6 revenue-column number parsing — start checkpoint — 2026-11-16 17:47 GMT+7

- Current v17 target still cannot be executed end-to-end after the validated join/date fixes because its `Thanh tien` values are textual and strict per-cell parsing marks values such as `75,000` ambiguous.
- Read-only column diagnosis on biz_124 found 97,033 nonempty values in `Thanh tien`; strict parsing marks 89,638 ambiguous. Existing `infer_decimal_separator` finds a consistent decimal policy (`.`), and parsing every cell with that explicit column policy succeeds. This is source-column evidence, not a label-derived assumption.
- Bounded fix only: use existing separator inference for a selected numeric source column in calculations that already consume it (threshold revenue, revenue/collected/quantity totals, ranking). If inference is unavailable, preserve strict per-cell parsing/abstention. No new locale default or dataset-specific special case.
- Add synthetic tests for a consistent grouped-number column and an ambiguous-only column; run focused and full tests, then data smoke and fresh train freeze/evaluation before public inference.

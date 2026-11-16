# P6 sales-source and normalized-quantity fix — start checkpoint — 2026-11-16 20:24 GMT+7

## v18 finding after verified train scoring

- v18 freeze passed, evaluator revalidated, then read train labels. Metrics: 28 correct, 10 wrong, 2,962 abstain / 3,000; coverage 1.2667%; answered accuracy 73.68%; penalized accuracy 0.600%; p95 14 ms; runtime errors 0. This is in-sample only and regresses penalized accuracy from v17's 0.7667%; do not call v18 an improvement.
- Wrong answers: 7 sales rankings and 3 cancellation rates. Relative to v17, several formerly abstaining sales questions were answered from `SoNhapHang` (incoming purchase table), and biz_126 ranking used the ordinary sold-unit column rather than README-documented base-unit `SL lẻ`. Existing biz_125 ranking discrepancy remains unresolved; cancellation-rate labels conflict with documented split rule and the selected raw statuses.
- Exact wrong IDs/details and v17 comparisons were read only after freeze validation; public labels remain unopened.

## Bounded changes only

- Add generic purchase-table identification and exclude incoming purchase rows from sales revenue/quantity/ranking/order count selection.
- Prefer documented normalized base-quantity headers (`SL lẻ`, `Số lượng lẻ`, `SL cơ bản`, `quy ra đơn vị lẻ`) over raw transaction quantity when selecting a sales-quantity metric.
- Add synthetic regressions proving the ranking cannot be sourced from purchase records and chooses base quantity when raw and normalized columns coexist.
- Do not tune the cancellation-rate metric to train labels; its documented/user-approved semantics need to stay distinct, and biz_116/biz_124 label mismatches remain recorded.
- After focused and full suite, generate a fresh v19 and compare train-only metrics after freeze validation. Do not run public inference until this false-answer regression is fixed or safely abstained.

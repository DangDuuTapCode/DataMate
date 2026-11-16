# P6 daily revenue safe-join extension — start checkpoint — 2026-11-16 17:36 GMT+7

## v17 diagnostic finding

- v17 was hash-validated before train-only scoring. Metrics: 26 correct, 3 wrong, 2,971 abstain / 3,000; 0.9667% coverage, 89.66% answered accuracy, 0.7667% penalized accuracy, p95 22 ms, 0 runtime errors. In-sample train only; no acceptance/generalization claim.
- The new daily-threshold intent correctly recognized the biz_124 question and parsed 15,000,000, but abstained with `missing_column`; it could not yet combine line amount with invoice date/status. This is not a solved end-to-end case.

## Structural evidence (train business schema only)

- biz_124 README says sales files connect by invoice ID.
- Line table `BanHang_ChiTietHoaDon.xlsx`: 97,033 rows; relevant headers include `Thanh tien`, `Mã giao dịch`, and `Ma hang`.
- Invoice table `BanHang_HoaDon.xlsx`: 51,044 rows; relevant headers include `Order ID`, `Ngày bán`, and `Trạng thái`.
- Read-only structural scan: invoice IDs were unique, no line-row invoice IDs were blank, and every line ID matched an invoice ID. No answer values or public/private labels were used for this schema scan. The official evaluator had already read train labels after v17 freeze validation.
- Split rulebook defines period by order date; its revenue lines are after line discount, unsuccessful order exclusions, and explicit in-transit inclusion. User-approved convention excludes canceled, returned, and failed-delivery revenue; keep classes distinct.

## Bounded change

- Add a generic line-to-invoice join for daily threshold questions only when there is exactly one viable line table and one invoice table, the invoice key is unique/nonblank, every nonblank line key matches, and date/status/line-amount columns are identified unambiguously.
- Use invoice `Ngày bán` as order date only for a uniquely identified invoice/order table with a validated order key; do not match by row position or partial keys.
- Deduplicate exact duplicate line rows as specified by rulebook §8, preserve distinct rows with different order IDs, apply rulebook time/status rules plus the user's unsuccessful-delivery exclusion, then sum by date.
- Add synthetic tests for a valid join, duplicate headers/IDs, unmatched lines, duplicate lines, status exclusions, and in-transit behavior under explicit rulebook inclusion.
- Regenerate a new immutable train replay only after tests pass; preserve v16/v17 and validate freeze before evaluator labels.

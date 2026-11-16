# Revenue versus collected money — implementation slice start

- Started: 2026-11-16 10:43 Asia/Bangkok.
- Work copy: `work/rehydrated-2026-11-15-P3/source` (isolated, no `.git`), based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User's authoritative business rule: default revenue is order value after discounts; collected/paid money is a separate metric; if source evidence cannot establish the requested metric, abstain.
- P3 reviewer remains skipped per user. P3 remains NOT VERIFIED / NOT PASSED.

## Evidence already read

- biz_127 README defines `don_hang.Tổng đơn` as total amount owed for the whole order, `Khách trả` as paid amount, `chi_tiet_don.Amount` as line value after discount, and `thanh_toan.Giá trị` as each payment event amount with `Ngày thu` as the collection date.
- biz_129 README defines `don_hang.Phải thu` as total order amount, `Thanh toán` as paid amount, `chi_tiet_don.Tiền bán` as line value after discount, and `thanh_toan.Tiền` as each payment event with `Thời điểm` as event time.
- Current executor sums the unique dated non-payment `AMOUNT` table for `revenue` and excludes payment tables. Current intent classifier does not give explicit collected/paid questions a distinct executable intent.

## Planned bounded scope

- Add a generic `collected_amount` intent for explicit received/paid-money wording; preserve the default `revenue` intent for after-discount order value.
- Execute collected amount only from one unambiguous payment-event table with an explicit event-date header and amount header. Use the receipt/payment event date for the requested period. Do not fall back to order totals, remaining debt, or order-date snapshots. Missing/ambiguous source, values, dates, or empty period must abstain.
- Add schema/API allowlist updates and synthetic regressions for separated metrics, split payments, collection-time filtering, and fail-closed cases. No business-ID-specific constants or answer values.
- Freeze predictions before any train-label scoring. Do not use Public Test questions/labels for tuning. No Git/official checkout/source archive/Docker changes.

## Acceptance evidence to record

- Focused intent and executor tests, then full unittest suite.
- If full train replay is run, record the frozen prediction hash before evaluator label access; report in-sample metrics and compare against v7 without claiming independent acceptance.
- Update STATE, implementation progress, handoff, changelog, and a completion checkpoint after this unit.

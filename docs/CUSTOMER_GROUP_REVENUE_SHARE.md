# Customer-group revenue share — biz_129

## Supported query family

The first runtime query family is intentionally scoped to Contest business `biz_129` and the three README-documented CSV roles:

- `chi_tiet_don.csv`: sales-line fact; `Số CT` and `Tiền bán`
- `don_hang.csv`: order metadata; `Số phiếu`, `Mã khách mua`, `Ngày bán`, `Tình trạng đơn`
- `khach_hang.csv`: customer dimension; `Mã khách lẻ/sỉ`, `Nhóm`

The currently recognized group labels observed in this source are `thân thiết`, `lẻ`, and `sỉ`. The query planner does not enable this intent for other business IDs.

Representative supported questions include:
- `q_264a7294b457`: October 2025 share of revenue from `thân thiết` customers.
- `q_6ee842fa8f92`: June 2025 share of revenue from `thân thiết` customers.

## Calculation contract

```text
numerator   = eligible sales-line amount for the requested customer group
denominator = eligible sales-line amount for the whole shop
share       = round(numerator / denominator * 100, 2)
```

Both numerator and denominator use net sales-line amounts after line-level discounts. The period comes from the order date (the README's `Ngày bán` field in this source). Cancelled and returned orders are excluded in full, including partial returns; in-transit orders remain included. Exact duplicate rows within the same order are counted once as required by rulebook §8.

Guest orders have blank customer IDs. The order → customer hop therefore requires LEFT JOIN. Guest lines retain their sales amount and remain in the whole-shop denominator, but they have no customer group and cannot enter the numerator—even when the customer dimension contains a group named `lẻ`.

Payment events remain a separate fact. Joining multiple payment rows to sales lines could multiply revenue and is not part of this query family.

## Fail-closed conditions

Execution abstains if the business ID is not `biz_129`, the three exact source roles are not unique, any required semantic field is missing or ambiguous, rulebook evidence does not establish the required amount/date/status/duplicate policies, the relationship path is not unique and non-fanout, a nonblank key is unmatched, a target key is duplicated, a date/status/amount is unparseable, or the denominator is zero.

## Verification

- Synthetic tests cover guest rows, exact duplicate-line handling, order-level returns, in-transit orders, missing fields, unknown statuses, unmatched keys, and business scoping.
- A full `main.run` test writes the percentage answer through the public question pipeline.
- The original Contest archive was independently audited; its aggregate checks are recorded in [CONTEST_BIZ129_JOIN_CASE.md](CONTEST_BIZ129_JOIN_CASE.md). No raw contest rows are committed or embedded as runtime constants.

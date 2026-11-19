# Contest case study: customer-group revenue joins

## Source basis

This analysis uses the uploaded `Contest.zip` training materials:
- `Contest/train/data/biz_129/README.md` for the five CSV file roles and their documented key columns.
- `Contest/train/rulebook.md` sections 1, 3, 7, and 8 for revenue eligibility, customer grouping, unanswerable behavior, and source-row interpretation.
- `Contest/train/questions.jsonl` for the representative questions listed below.

The archive is an analysis fixture only. Its source data is not copied into this repository.

## Representative query family

The training questions include:
- `q_264a7294b457`: share of October 2025 revenue from customers in group `thân thiết`.
- `q_6ee842fa8f92`: share of June 2025 revenue from customers in group `thân thiết`.
- `q_635440e343cc`: total March 2025 sales for customers in group `thân thiết`.
- `q_d361c00c6829`: revenue of orders belonging to customers in group `thân thiết` in June 2025.

The README documents the relevant links:
- `chi_tiet_don.csv`: sales lines, order key `Số CT`, product key `Mã hàng bán`, net line amount `Tiền bán`.
- `don_hang.csv`: order header, order key `Số phiếu`, customer key `Mã khách mua`, date `Ngày bán`, status `Tình trạng đơn`.
- `khach_hang.csv`: customer dimension, customer key `Mã khách lẻ/sỉ`, group `Nhóm`.
- `thanh_toan.csv`: payment events, order key `Mã giao dịch`, payment event identifier `Mã GD`.

The three-table revenue path is therefore:

`chi_tiet_don.csv` (sales-line fact)
→ `don_hang.csv` (order metadata)
→ `khach_hang.csv` (customer group).

## Observed structural profile

Counts below were measured from the uploaded archive, not copied into runtime configuration:

| Source | Rows | Key profile |
|---|---:|---|
| `chi_tiet_don.csv` | 145,479 | 38,499 distinct order IDs; every nonblank order ID matches the order file |
| `don_hang.csv` | 38,499 | 38,499 unique order IDs |
| `khach_hang.csv` | 220 | 220 unique customer IDs |
| `thanh_toan.csv` | 38,072 | 37,748 distinct order IDs; up to 4 payment events per order |

In `don_hang.csv`, 23,309 orders have a nonblank customer ID and all those IDs match the customer catalog. Another 15,190 orders have a blank customer ID. The order-to-customer relationship is therefore many-to-one for known customers, with a meaningful blank-key population on the order side.

## Business semantics and join consequences

The rulebook says:
- Revenue excludes cancelled and returned orders; a returned order is excluded in full, including partial returns. Orders still shipping remain included.
- Revenue is the sum of net line amounts after line-level discount, not the amount collected from customers.
- Revenue period is based on order date.
- Revenue by customer group uses the customer-group column. Orders with no recorded customer (walk-in/guest) belong to no group, including the `lẻ` group.
- The denominator for a customer-group share is the whole shop's revenue, including guest orders.

Consequences:
1. The fact grain is one sales-detail row. Both order and customer joins must be non-fanout many-to-one joins.
2. The order-to-customer hop has blank source keys. A normal inner join would remove guest sales and corrupt the whole-shop denominator. The contract must require LEFT JOIN for the full fact path; guest rows remain in the fact set with null customer attributes and are not assigned to a customer group.
3. The customer-group numerator filters the joined customer dimension to the requested group. The denominator aggregates all eligible fact rows before group filtering (or is computed as a separate all-customer aggregate).
4. The payment-event table must not be joined directly to the sales-line fact: multiple payment rows per order can multiply sales-line amounts. Collection/debt questions need a separate payment-grain component, aggregated by order or payment period under their own rulebook semantics.

The current relationship validator previously rejected the customer edge solely because of blank source keys. The new `validated_left_join` evidence state distinguishes this safe non-fanout relationship from a fully matched relationship. The path resolver propagates a `left_join_required` status, and `FactJoinContract` refuses to build the path as an inner join.

## Implementation boundary

This case is a structural and semantic test fixture, not permission to enable arbitrary runtime joins. The contract still does not execute the join, apply order-status/date predicates, or calculate the percentage. Runtime wiring remains blocked until the executor can apply the exact join sequence and preserve the separate numerator/denominator semantics. No payment event is joined into this sales-line fact path.

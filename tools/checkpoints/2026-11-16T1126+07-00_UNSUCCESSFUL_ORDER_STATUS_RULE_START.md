# Unsuccessful-order status semantics — implementation slice start

- Started: 2026-11-16 11:26 Asia/Bangkok.
- Work copy: `work/rehydrated-2026-11-15-P3/source`, isolated no-Git snapshot, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User-directed DataMate convention: keep three distinct status groups—canceled by customer/system, returned after delivery, and failed delivery. All three count in the unsuccessful-order group for the cancellation-rate metric. Preserve raw statuses and do not infer an outcome where corresponding status evidence is absent.
- P3 reviewer remains skipped; P3 remains NOT VERIFIED / NOT PASSED.

## Evidence prompting the slice

- Frozen v8 train evaluation had two `cancellation_rate` errors on biz_116; the engine returned 0.00% for April and June 2026.
- biz_116 README identifies the `Trạng thái` field as order status but does not define cancellation-rate grouping. Source values include `khách hủy`, `đã trả hàng`, `không giao được`, `đang vận chuyển`, and `thành công`.
- The user has explicitly chosen the business convention. Matching train labels are supporting diagnostic evidence only, not the authority for this rule.

## Planned bounded scope

- Add a non-mutating status classifier that distinguishes canceled, returned, delivery-failed, in-transit/pending, successful, and unknown states. Keep original raw values unchanged.
- Calculate cancellation rate from unique order IDs in the combined unsuccessful group (canceled + returned + delivery-failed); do not count in-transit/pending as unsuccessful and do not infer from missing status fields.
- Add generic status-header aliases that README/profile evidence documents (including `Kết quả` and `Ghi chú TT`) only after checking the full structural inventory.
- Add synthetic regressions for classification, deduplication, unknown/missing status, and in-transit exclusion. Run the full suite and freeze a new replay before evaluation labels are opened.
- Write the convention to project business-rule documentation and record exact provenance. No business-ID/question-ID constants or answer values.

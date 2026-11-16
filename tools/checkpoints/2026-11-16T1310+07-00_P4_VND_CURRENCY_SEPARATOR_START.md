# P4 VND amount parsing — start

- Started: 2026-11-16 13:10 Asia/Bangkok.
- Working copy: isolated/no-Git `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Read-only source inspection found documented after-discount detail amounts in biz_127/biz_129 formatted as `10.000đ`, `1tr040`, `1,04tr`, and `1,156tr`. Previously explicit VND groupings were ambiguous, and `tr` values were invalid. Existing README fields identify these as after-discount detail amounts.
- Bounded fix: explicit VND marker plus valid lone three-digit group resolves to grouping; Vietnamese `tr`/`triệu` multiplies a parsed coefficient by one million; compact `1tr040` means 1,040,000; a three-digit decimal tail like `1,156tr` remains ambiguous without column evidence. Bare `10.000` remains ambiguous and explicit caller separator policy takes precedence.
- Source parse audit after the fix (no labels): biz_127 `Amount` 131,192/131,192 values parsed; biz_129 `Tiền bán` 145,479/145,479 parsed, with comma inferred at column level. Detail-to-order reconciliation found many legitimate mismatches (biz_127 9,605/33,874 exact; biz_129 11,587/38,499 exact), so do not replace order-total revenue with detail sums or add a join without a documented reconciliation contract.
- New completion evidence: `tools/checkpoints/2026-11-16T1325+07-00_P4_VND_MILLION_NORMALIZATION_COMPLETE.md`.
- No source-input mutation, public-test tuning, Git, Docker, or official checkout action. Keep user-approved revenue rule: exclude canceled, returned, and failed-delivery orders.

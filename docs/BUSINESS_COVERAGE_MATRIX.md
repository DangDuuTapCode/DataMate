# Train Business Profile and Coverage Matrix

This is structural profile coverage (L1), not proof that any business/intent is release-supported.
Question intent figures are rule-parser coverage diagnostics, not reviewed accuracy. No answer labels or public-test content are used.

- Businesses profiled: 30/30
- Structured files: 128; tables/sheets: 339
- Rows from prior full ingestion census: 3,997,042
- Questions profiled: 3,000

| Business | Formats | Files | Tables/sheets | Ingested rows | Questions | Intent coverage | Profile level |
|---|---|---:|---:|---:|---:|---:|---|
| biz_101 | .csv | 1 | 1 | 56,501 | 40 | 97.5% | L1 structural |
| biz_102 | .xlsx | 2 | 19 | 86,106 | 119 | 95.0% | L1 structural |
| biz_103 | .xlsx | 2 | 17 | 45,611 | 119 | 97.5% | L1 structural |
| biz_104 | .xlsx | 2 | 2 | 62,896 | 119 | 97.5% | L1 structural |
| biz_105 | .xlsx | 6 | 21 | 141,748 | 119 | 95.8% | L1 structural |
| biz_106 | .xlsx | 10 | 10 | 289,353 | 119 | 88.2% | L1 structural |
| biz_107 | .xlsx | 1 | 1 | 43,605 | 40 | 100.0% | L1 structural |
| biz_108 | .xlsx | 7 | 7 | 113,696 | 119 | 97.5% | L1 structural |
| biz_109 | .xlsx | 2 | 9 | 156,626 | 118 | 90.7% | L1 structural |
| biz_110 | .csv | 1 | 1 | 29,317 | 40 | 92.5% | L1 structural |
| biz_111 | .csv | 5 | 5 | 239,499 | 118 | 99.2% | L1 structural |
| biz_112 | .xlsx | 3 | 17 | 113,375 | 118 | 90.7% | L1 structural |
| biz_113 | .xlsx | 1 | 1 | 32,994 | 40 | 100.0% | L1 structural |
| biz_114 | .csv | 1 | 1 | 26,119 | 40 | 92.5% | L1 structural |
| biz_115 | .xlsx | 4 | 19 | 55,962 | 118 | 98.3% | L1 structural |
| biz_116 | .xlsx | 1 | 4 | 79,117 | 118 | 97.5% | L1 structural |
| biz_117 | .xlsx | 7 | 23 | 66,286 | 118 | 91.5% | L1 structural |
| biz_118 | .xlsx | 4 | 23 | 92,169 | 118 | 89.8% | L1 structural |
| biz_119 | .xlsx | 10 | 28 | 172,569 | 118 | 94.9% | L1 structural |
| biz_120 | .xlsx | 10 | 27 | 240,702 | 118 | 90.7% | L1 structural |
| biz_121 | .xlsx | 2 | 7 | 172,139 | 118 | 94.9% | L1 structural |
| biz_122 | .xlsx | 9 | 26 | 214,306 | 118 | 92.4% | L1 structural |
| biz_123 | .sqlite | 1 | 17 | 268,911 | 118 | 91.5% | L1 structural |
| biz_124 | .csv, .xlsx | 13 | 13 | 305,973 | 118 | 96.6% | L1 structural |
| biz_125 | .csv | 1 | 1 | 79,052 | 40 | 95.0% | L1 structural |
| biz_126 | .xlsx | 1 | 1 | 66,429 | 40 | 100.0% | L1 structural |
| biz_127 | .csv | 5 | 5 | 198,800 | 118 | 98.3% | L1 structural |
| biz_128 | .xlsx | 8 | 25 | 152,259 | 118 | 96.6% | L1 structural |
| biz_129 | .csv | 5 | 5 | 222,331 | 118 | 98.3% | L1 structural |
| biz_130 | .xlsx | 3 | 3 | 172,591 | 118 | 91.5% | L1 structural |

## README caveats for later operator work

- `biz_107`, `biz_113`, and `biz_126` are handwritten sales books without invoice IDs or customer names; invoice/customer metrics cannot be inferred from rows.
- `biz_110` contains invoice-level rows only and has no product-line detail; product quantity/ranking must abstain.
- `biz_102`–`biz_104`, `biz_112`, `biz_115`–`biz_116`, `biz_118`, and `biz_130` include sales details without a stable product code; some joins rely on product name and require an explicit uniqueness check.
- `biz_105` and `biz_117` encode returns as negative quantities on the original invoice; revenue and quantity rules must preserve that sign and cancellation semantics.
- `biz_119`–`biz_122` and `biz_123`–`biz_124` contain lot/expiry or medication metadata. Lot-level sales may span multiple lots, and returned goods go back to the sold lot.
- `biz_115`, `biz_116`, and `biz_118` contain delivery ledgers with 1–3 delivery rounds; only qualifying non-cancelled building-material orders are delivered, and latest orders may not yet appear.
- `biz_123` is SQLite with stock-movement history; as-of inventory must use the last product movement at or before the requested date.
- `biz_124` combines POS exports, handwritten purchase/expense ledgers, and inventory CSV; the sources require separate declared joins.
- `biz_125`–`biz_130` have restaurant service-fee lines for eligible cold-room dining orders; do not count them as merchandise quantity.
- Many README conversion factors are product-specific; unit conversion must not be generalized from a shared unit name.

## Interpretation

The matrix establishes L1 structural profiling only. Higher business levels (ingestion tests, intent-specific golden tests, replay evaluation, release support) are not implied. Candidate joins in the JSON profile are header-name matches only and are not approved execution keys.

# Multi-source identifier expansion — 2026-11-19

## Why this change

The supplied Contest archive includes relationships not represented by the original four-key vocabulary. Examples documented by the public-test README files and SQLite schema include employee IDs, supplier IDs, purchase receipt IDs, batch/lot IDs, branch IDs, and device IMEI. Without exact canonical mappings, the schema catalog cannot discover these links.

## Implementation

- `src/datamate/semantic.py` adds exact aliases for:
  - order/invoice IDs, including explicit invoice/bill labels;
  - customer IDs and common customer-code variants;
  - product/item IDs and barcodes;
  - employee/staff IDs;
  - supplier/vendor IDs;
  - purchase receipt IDs;
  - batch/lot IDs;
  - branch IDs;
  - payment receipt/transaction IDs;
  - device IMEI.
- `src/datamate/relationships.py` now considers the added employee, supplier, purchase receipt, batch, branch, and IMEI keys alongside the original order/customer/product/payment keys.
- Generic `STT`, `Mã tham chiếu`, and generic `Mã` remain unmapped.
- Identifier matching remains exact-string-only; leading zeroes are preserved.
- Relationship discovery continues to evaluate overlap, uniqueness, cardinality, blanks, and unmatched keys. It does not execute a join or infer a business rule.

## Tests added

- `tests/test_semantic.py`: exact contest identifier aliases map; generic row/reference labels remain unmapped.
- `tests/test_relationships.py`: six added key families produce validated many-to-one candidates only when synthetic values have full child coverage and unique parent keys.

## Commits

- `8ff2c0935536c4c31b21e845bb7fc02464b3bbda` — semantic identifier aliases.
- `37f66c385021eb49a22d6adbce6dfcd7951f6a5b` — relationship-key families.
- `a784b4fb9524b54493474cd36a418bf25deace9b` — semantic tests.
- `2d866ee9585211b69a39dcb226c911eb03041f2b` — relationship tests.
- `a64ba3439d2a82dcc73d324b9ba6cdefeab1bd67` — payment receipt aliases.
- `0465e9d9d06b4c3c65d4cba48c1520458daa9619` — payment alias test.
- `dccf1bab63c1ac511294d0f7f10b896ee53cc1a4` — relationship docs.
- `45b3667a5f8db22ea9f9ca1cb66ea6294db70a7a` — progress docs.
- `9d2ceab8bea925be6be1c980c48e57ee4c3c31dd` — handoff.
- `03f125312db206a4a3ad7def42b22edf0a508a22` — state.

## Verification

No new GitHub Actions result has been verified for this change set. The prior known baseline is run `44565561293` (272 tests; 270 passed, two inherited `CODEX PROGRESS` repository-hygiene failures). No local checkout or local test execution is available.

## Next

Before enabling execution over these new relationships, add explicit, evidence-scoped join planning for selected query families and verify it against representative multi-source fixtures. Do not treat a validated relationship as permission to join every table that shares a key.

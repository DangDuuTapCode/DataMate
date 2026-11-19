# Rulebook-aware composite order-line relationships — 2026-11-19

## Contest evidence

The public-test POS SQLite business `dev_006` contains:
- `chi_tiet_don`: 72,411 rows with `MaHoaDon`, `SoThuTu`, `MaHangHoa`, line amount/quantity fields.
- `chi_tiet_don_lo`: 72,710 rows with `MaHoaDon`, `SoThuTu`, `MaLo`, and lot allocation quantities.

The relationship is composite: `chi_tiet_don_lo.(MaHoaDon, SoThuTu)` -> `chi_tiet_don.(MaHoaDon, SoThuTu)`. Joining by `MaHoaDon` alone is not safe because it collapses all lines of an order.

Observed data checks:
- `chi_tiet_don` has 1,350 exact duplicate row groups. Deduplicating exact rows leaves 71,061 rows and 71,061 unique order-line pairs.
- `chi_tiet_don_lo` has 72,710 rows and 70,315 distinct order-line pairs; repeated pairs represent multiple lot allocations for one line.
- Every distinct lot-allocation order-line pair is present in the detail table.
- The active rulebook explicitly says identical rows of the same order are export errors and count once. This policy is not assumed if the clause is absent.

## Implementation

- `src/datamate/split_rules.py`
  - Adds `deduplicate_identical_order_lines`, parsed only from the explicit same-order exact-duplicate clause.
  - Defaults false when the clause is absent; synthetic test defaults explicitly enable it.
- `src/datamate/semantic.py`
  - Maps exact `Số thứ tự` and `No.` aliases to `order_line_number`.
  - Leaves generic `STT` unmapped.
- `src/datamate/relationships.py`
  - Adds composite `order_id + order_line_number` candidates.
  - Serializes `canonical_keys`, `from_column_indices`, and `to_column_indices`.
  - Uses exact full-row deduplication for composite relationship profiling only when the active rulebook explicitly enables it.
  - Preserves source-qualified table identities.
- `src/datamate/schema_catalog.py`
  - Accepts the explicit deduplication policy and increments schema catalog version to `1.1.0`.
- `src/datamate/main.py`
  - Passes the active split rulebook policy into schema catalog construction.
- No source rows are mutated and no joins are executed.

## Regression tests

- `tests/test_split_rules.py`: exact clause enables policy; absent clause does not.
- `tests/test_semantic.py`: order-line sequence maps while `STT` remains unmapped.
- `tests/test_relationships.py`: composite key remains ambiguous without the rule; validates as many-to-one with the rule; partial key coverage remains only a candidate.
- `tests/test_schema_catalog.py`: explicit policy is passed through catalog construction and changes only composite relationship status.

## Commits

- `107216e39994fe7aa846dd47e55350f086e0ba73` — split-rule parser.
- `64c426cef3e51a20fd80202d4f0b385279cee352` — order-line sequence aliases.
- `01e54b3dbc05629c2e48a4ca6edd6484086a465e` — composite relationship discovery.
- `bd2b1f6f9eb80d208cedc16d1975a328439306cf` — catalog policy parameter.
- `0f120e9c49a6f4c9f36c19712d8b7073f5c066f1` — runtime wiring.
- `3191b7a6559178daf303246251606810113e19d0` — normalized clause match fix.
- `7016a6007ba15f18eb3a519be5dfaa7746ad6ab6` — semantic tests.
- `ef200e29f93393afbb5969a1f6648ef22fc34963` — relationship tests.
- `06a579f1fa474ac1664bbb1e1cf398614e1382f6` — catalog test.
- `d0d75b9941f440fd4cb4f13027ccb60845e2fb75` — split-rule tests.
- `4f6def6851ddff74ffeeba4079a6ca31d2c27369` — schema catalog version 1.1.0.
- `6ae52b0479b14da76d4b3d873925589339042c7f` — version test.
- `a6da9e40fb57a95d4c0924005aad81d142460b97` — partial-overlap expectation.
- `4e17cd94e1f01ecb3e75ae1911916d0c8b8887cc` — relationship docs.
- `3741d341d3709df8f9193e8e9c8599952e03b4f9` — rule evidence docs.
- `aa6e746425f1e77b05c7e1837e18202cb67b7477` — implementation progress.
- `ea5fb27e93f8ca3f43e1b31628233d9794eafbcf` — continuation handoff.
- `880b85d1a6ceb8ef322fb8747901e84906e312b0` — state checkpoint.

## Verification

No new GitHub Actions result has been verified. The last known pre-change baseline was run `44565561293`: 272 tests, 270 passed, two inherited `CODEX PROGRESS` hygiene failures. The newly added tests have not been executed in a local checkout or verified by Actions.

## Next

The next major milestone is query-specific execution over a validated relationship path. It must preserve row grain, apply only rulebook-authorized deduplication, reject ambiguous/many-to-many joins, and distinguish simple keys from composite or polymorphic keys. In particular, `the_kho` references different document types through `(KieuChungTu, MaChungTu)`; this is not a safe single-key join and remains unsupported.

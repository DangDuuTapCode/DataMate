import unittest

from datamate.join_contracts import build_fact_join_contract
from datamate.join_executor import execute_fact_join_contract
from datamate.relationship_paths import resolve_relationship_path
from datamate.relationships import RelationshipCandidate, discover_relationships
from datamate.types import Table


def relationship(left, right, key, cardinality, *, left_index=0, right_index=0):
    return RelationshipCandidate(
        from_table=left[0],
        from_source=left[1],
        to_table=right[0],
        to_source=right[1],
        canonical_key=key,
        from_column_index=left_index,
        to_column_index=right_index,
        cardinality=cardinality,
        status="validated",
        confidence=1.0,
        from_row_count=3,
        to_row_count=2,
        from_distinct_keys=2,
        to_distinct_keys=2,
        matched_distinct_keys=2,
        from_unmatched_keys=0,
        to_unmatched_keys=0,
        from_blank_keys=0,
        to_blank_keys=0,
        from_duplicate_excess=1,
        to_duplicate_excess=0,
        evidence=("synthetic_test",),
    )


class FactJoinExecutorTests(unittest.TestCase):
    def setUp(self):
        self.details = Table(
            "chi_tiet_don",
            ["Số CT", "Mã hàng bán", "Tiền bán"],
            [
                ["ORD1", "SP1", "50000"],
                ["ORD1", "SP2", "30000"],
                ["ORD2", "SP1", "100000"],
            ],
            "chi_tiet_don.csv",
        )
        self.orders = Table(
            "don_hang",
            ["Số phiếu", "Mã khách mua", "Ngày bán"],
            [
                ["ORD1", "KH1", "2025-10-01"],
                ["ORD2", "", "2025-10-02"],
                ["ORD3", "KH1", "2025-10-03"],
            ],
            "don_hang.csv",
        )
        self.customers = Table(
            "khach_hang",
            ["Mã khách lẻ/sỉ", "Nhóm"],
            [["KH1", "thân thiết"]],
            "khach_hang.csv",
        )
        self.contract = self._contract(
            [self.details, self.orders, self.customers],
            join_type="left",
        )

    def _contract(self, tables, *, join_type):
        relationships = discover_relationships(tables)
        path = resolve_relationship_path(
            relationships,
            ("chi_tiet_don", "chi_tiet_don.csv"),
            ("khach_hang", "khach_hang.csv"),
            max_hops=2,
        )
        return build_fact_join_contract(
            path,
            ("chi_tiet_don", "chi_tiet_don.csv"),
            ("khach_hang", "khach_hang.csv"),
            fact_grain="one row per sales order detail line",
            measure_field="Tiền bán",
            measure_column_index=2,
            join_type=join_type,
        )

    def test_executes_two_hop_left_join_without_losing_guest_fact_rows(self):
        result = execute_fact_join_contract(
            [self.details, self.orders, self.customers], self.contract
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.row_count, 3)
        self.assertEqual(result.column(
            ("chi_tiet_don", "chi_tiet_don.csv"), 2
        ), ("50000", "30000", "100000"))
        self.assertEqual(result.column(
            ("khach_hang", "khach_hang.csv"), 1
        ), ("thân thiết", "thân thiết", None))
        self.assertEqual(result.value(
            2, ("don_hang", "don_hang.csv"), 1
        ), "")

    def test_executes_complete_inner_join_when_no_source_keys_are_blank(self):
        known_customer_orders = Table(
            self.orders.name,
            self.orders.headers,
            [
                ["ORD1", "KH1", "2025-10-01"],
                ["ORD2", "KH1", "2025-10-02"],
                ["ORD3", "KH1", "2025-10-03"],
            ],
            self.orders.source,
        )
        contract = self._contract(
            [self.details, known_customer_orders, self.customers],
            join_type="inner",
        )
        result = execute_fact_join_contract(
            [self.details, known_customer_orders, self.customers], contract
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.join_type, "inner")
        self.assertEqual(result.row_count, 3)
        self.assertEqual(result.column(
            ("khach_hang", "khach_hang.csv"), 1
        ), ("thân thiết", "thân thiết", "thân thiết"))

    def test_identifier_matching_preserves_leading_zeroes(self):
        details = Table(
            self.details.name, self.details.headers,
            [["001", "SP1", "10000"]], self.details.source,
        )
        orders = Table(
            self.orders.name, self.orders.headers,
            [["001", "KH1", "2025-10-01"]], self.orders.source,
        )
        contract = self._contract([details, orders, self.customers], join_type="inner")
        self.assertIsNotNone(execute_fact_join_contract(
            [details, orders, self.customers], contract
        ))

        numeric_looking_mismatch = Table(
            orders.name, orders.headers,
            [["1", "KH1", "2025-10-01"]], orders.source,
        )
        self.assertIsNone(execute_fact_join_contract(
            [details, numeric_looking_mismatch, self.customers], contract
        ))

    def test_rejects_blank_fact_grain(self):
        from dataclasses import replace

        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers],
            replace(self.contract, fact_grain=" "),
        ))

    def test_preserves_duplicate_fact_lines(self):
        duplicate_details = Table(
            self.details.name,
            self.details.headers,
            self.details.rows + [self.details.rows[0]],
            self.details.source,
        )
        contract = self._contract(
            [duplicate_details, self.orders, self.customers],
            join_type="left",
        )
        result = execute_fact_join_contract(
            [duplicate_details, self.orders, self.customers], contract
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.row_count, 4)
        self.assertEqual(result.column(
            ("chi_tiet_don", "chi_tiet_don.csv"), 2
        )[-1], "50000")

    def test_rejects_nonblank_unmatched_source_key(self):
        bad_orders = Table(
            self.orders.name,
            self.orders.headers,
            [
                ["ORD1", "KH1", "2025-10-01"],
                ["ORD2", "", "2025-10-02"],
                ["ORD3", "KH404", "2025-10-03"],
            ],
            self.orders.source,
        )
        bad_details = Table(
            self.details.name,
            self.details.headers,
            self.details.rows + [["ORD3", "SP1", "20000"]],
            self.details.source,
        )
        self.assertIsNone(execute_fact_join_contract(
            [bad_details, bad_orders, self.customers], self.contract
        ))

    def test_rejects_duplicate_target_keys(self):
        duplicate_customers = Table(
            self.customers.name,
            self.customers.headers,
            self.customers.rows + [["KH1", "sỉ"]],
            self.customers.source,
        )
        self.assertIsNotNone(self.contract)
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, duplicate_customers], self.contract
        ))

    def test_rejects_blank_source_key_without_left_join_evidence(self):
        forged = self.contract
        first, second = forged.path_hops
        altered_second = type(second)(
            second.from_table, second.to_table, second.canonical_keys,
            second.from_column_indices, second.to_column_indices,
            second.cardinality, second.fanout, False,
        )
        from dataclasses import replace
        forged = replace(forged, path_hops=(first, altered_second))

        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers], forged
        ))

    def test_rejects_measure_header_mismatch_and_unhashable_contract_values(self):
        from dataclasses import replace

        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers],
            replace(self.contract, measure_field="not the source header"),
        ))
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers],
            replace(self.contract, join_type=[]),
        ))
        first, second = self.contract.path_hops
        malformed = type(second)(
            second.from_table, second.to_table, second.canonical_keys,
            second.from_column_indices, second.to_column_indices,
            [], second.fanout, second.requires_left_join,
        )
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers],
            replace(self.contract, path_hops=(first, malformed)),
        ))
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers],
            replace(self.contract, path_hops=(object(),)),
        ))

    def test_rejects_key_indices_not_backed_by_semantic_mapping(self):
        from dataclasses import replace

        first, second = self.contract.path_hops
        malformed = type(first)(
            first.from_table, first.to_table, first.canonical_keys,
            (1,), first.to_column_indices, first.cardinality,
            first.fanout, first.requires_left_join,
        )
        forged = replace(self.contract, path_hops=(malformed, second))
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers], forged
        ))

    def test_rejects_missing_or_duplicate_source_table_identity(self):
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders], self.contract
        ))
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers, self.customers],
            self.contract,
        ))

    def test_rejects_invalid_measure_column_and_malformed_rows(self):
        from dataclasses import replace
        self.assertIsNone(execute_fact_join_contract(
            [self.details, self.orders, self.customers],
            replace(self.contract, measure_column_index=99),
        ))
        malformed_details = Table(
            self.details.name, self.details.headers,
            [["ORD1"]], self.details.source,
        )
        self.assertIsNone(execute_fact_join_contract(
            [malformed_details, self.orders, self.customers],
            self.contract,
        ))


if __name__ == "__main__":
    unittest.main()

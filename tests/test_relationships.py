import unittest

from datamate.relationships import discover_relationships
from datamate.types import Table


class RelationshipDiscoveryTests(unittest.TestCase):
    def test_detail_to_order_is_validated_many_to_one(self):
        details = Table(
            "order_details",
            ["Mã đơn", "Mã sản phẩm"],
            [["A1", "P1"], ["A1", "P2"], ["A2", "P3"]],
            "details.csv",
        )
        orders = Table(
            "orders",
            ["Mã đơn", "Ngày đặt"],
            [["A1", "2026-01-01"], ["A2", "2026-01-02"]],
            "orders.csv",
        )

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.canonical_key, "order_id")
        self.assertEqual(relationship.cardinality, "many_to_one")
        self.assertEqual(relationship.status, "validated")
        self.assertEqual(relationship.confidence, 1.0)
        self.assertEqual(relationship.from_duplicate_excess, 1)
        self.assertEqual(relationship.to_duplicate_excess, 0)
        self.assertIn("all_left_keys_match", relationship.evidence)

    def test_additional_contest_keys_validate_only_exact_cardinality_safe_links(self):
        tables = [
            Table("sales", ["Mã NV bán"], [["E1"], ["E1"], ["E2"]], "sales.xlsx"),
            Table("staff", ["Mã nhân viên"], [["E1"], ["E2"]], "staff.xlsx"),
            Table("purchases", ["Mã NCC"], [["S1"], ["S1"]], "purchases.xlsx"),
            Table("suppliers", ["Mã nhà cung cấp"], [["S1"]], "suppliers.xlsx"),
            Table("purchase_lines", ["Mã phiếu nhập"], [["R1"], ["R1"]], "purchase_lines.xlsx"),
            Table("purchase_headers", ["Mã phiếu nhập"], [["R1"]], "purchase_headers.xlsx"),
            Table("stock_moves", ["Mã lô"], [["L1"], ["L1"]], "stock_moves.xlsx"),
            Table("lots", ["Mã lô"], [["L1"]], "lots.xlsx"),
            Table("sales_by_branch", ["Mã chi nhánh"], [["B1"], ["B1"]], "sales_by_branch.xlsx"),
            Table("branches", ["Mã chi nhánh"], [["B1"]], "branches.xlsx"),
            Table("warranty_visits", ["IMEI"], [["I1"], ["I1"]], "warranty.xlsx"),
            Table("devices", ["IMEI"], [["I1"]], "devices.xlsx"),
        ]

        relationships = discover_relationships(tables)

        self.assertEqual(
            {item.canonical_key for item in relationships},
            {
                "employee_id", "supplier_id", "purchase_receipt_id",
                "batch_id", "branch_id", "imei",
            },
        )
        self.assertTrue(all(item.status == "validated" for item in relationships))
        self.assertTrue(all(item.cardinality == "many_to_one" for item in relationships))

    def test_relationship_identity_distinguishes_same_named_sheets_by_source(self):
        details = Table(
            "Sheet1", ["Mã đơn"], [["A1"], ["A1"], ["A2"]], "details.xlsx"
        )
        orders = Table(
            "Sheet1", ["Mã đơn"], [["A1"], ["A2"]], "orders.xlsx"
        )

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.from_table, "Sheet1")
        self.assertEqual(relationship.from_source, "details.xlsx")
        self.assertEqual(relationship.to_table, "Sheet1")
        self.assertEqual(relationship.to_source, "orders.xlsx")
        self.assertEqual(relationship.status, "validated")
        self.assertEqual(relationship.cardinality, "many_to_one")
        self.assertEqual(relationship.to_dict()["to_source"], "orders.xlsx")

    def test_composite_order_line_key_uses_rulebook_duplicate_policy(self):
        lot_rows = [
            ["A1", 1, "L1"],
            ["A1", 1, "L2"],
            ["A1", 2, "L3"],
            ["A2", 1, "L4"],
        ]
        detail_rows = [
            ["A1", 1, "P1"],
            ["A1", 1, "P1"],  # exact duplicate export row
            ["A1", 2, "P2"],
            ["A2", 1, "P3"],
        ]
        lots = Table(
            "chi_tiet_don_lo",
            ["Mã hóa đơn", "Số thứ tự", "Mã lô"],
            lot_rows,
            "pos.sqlite",
        )
        details = Table(
            "chi_tiet_don",
            ["Mã hóa đơn", "Số thứ tự", "Mã hàng hóa"],
            detail_rows,
            "pos.sqlite",
        )

        without_policy = discover_relationships([lots, details])
        composite_without_policy = next(
            item for item in without_policy
            if item.canonical_key == "order_id+order_line_number"
        )
        self.assertEqual(composite_without_policy.status, "ambiguous")
        self.assertEqual(composite_without_policy.cardinality, "many_to_many")

        with_policy = discover_relationships(
            [lots, details], deduplicate_identical_order_lines=True
        )
        composite = next(
            item for item in with_policy
            if item.canonical_key == "order_id+order_line_number"
        )
        self.assertEqual(composite.canonical_keys, ("order_id", "order_line_number"))
        self.assertEqual(composite.cardinality, "many_to_one")
        self.assertEqual(composite.status, "validated")
        self.assertEqual(composite.from_row_count, 4)
        self.assertEqual(composite.to_row_count, 3)
        self.assertIn("rulebook_exact_duplicate_rows_policy_applied", composite.evidence)
        self.assertIn("exact_duplicate_rows_removed", composite.evidence)
        self.assertEqual(composite.to_dict()["to_column_indices"], [0, 1])

    def test_composite_order_line_key_rejects_unmatched_child_pair(self):
        lots = Table(
            "chi_tiet_don_lo",
            ["Mã hóa đơn", "Số thứ tự", "Mã lô"],
            [["A1", 1, "L1"], ["A9", 1, "L9"]],
            "pos.sqlite",
        )
        details = Table(
            "chi_tiet_don",
            ["Mã hóa đơn", "Số thứ tự", "Mã hàng hóa"],
            [["A1", 1, "P1"]],
            "pos.sqlite",
        )

        composite = next(
            item for item in discover_relationships(
                [lots, details], deduplicate_identical_order_lines=True
            )
            if item.canonical_key == "order_id+order_line_number"
        )

        self.assertEqual(composite.status, "candidate")
        self.assertEqual(composite.from_unmatched_keys, 1)

    def test_unmatched_child_key_is_rejected(self):
        details = Table("details", ["Mã đơn"], [["A1"], ["A1"], ["A3"]], "details.csv")
        orders = Table("orders", ["Mã đơn"], [["A1"], ["A2"]], "orders.csv")

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.status, "rejected")
        self.assertEqual(relationship.from_unmatched_keys, 1)
        self.assertEqual(relationship.to_unmatched_keys, 1)

    def test_duplicate_parent_key_is_rejected_as_many_to_many_risk(self):
        details = Table("details", ["Mã đơn"], [["A1"], ["A1"]], "details.csv")
        orders = Table("orders", ["Mã đơn"], [["A1"], ["A1"]], "orders.csv")

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.status, "ambiguous")
        self.assertEqual(relationship.cardinality, "many_to_many")
        self.assertIn("join_multiplication_risk", relationship.evidence)

    def test_partial_one_to_one_overlap_is_candidate_not_validated(self):
        left = Table("left", ["Mã khách hàng"], [["C1"], ["C2"]], "left.csv")
        right = Table("right", ["Mã khách hàng"], [["C1"], ["C3"]], "right.csv")

        [relationship] = discover_relationships([left, right])

        self.assertEqual(relationship.status, "candidate")
        self.assertEqual(relationship.cardinality, "one_to_one")
        self.assertEqual(relationship.confidence, 0.5)

    def test_blank_child_key_requires_left_join_instead_of_rejecting_safe_cardinality(self):
        details = Table("details", ["Mã đơn"], [["A1"], ["A1"], [None]], "details.csv")
        orders = Table("orders", ["Mã đơn"], [["A1"]], "orders.csv")

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.status, "validated_left_join")
        self.assertEqual(relationship.cardinality, "many_to_one")
        self.assertEqual(relationship.from_blank_keys, 1)
        self.assertIn("blank_source_keys_require_left_join", relationship.evidence)

    def test_one_to_one_blank_source_key_is_left_join_validated(self):
        left = Table("left", ["Mã khách"], [["C1"], [None]], "left.csv")
        right = Table("right", ["Mã khách"], [["C1"]], "right.csv")

        [relationship] = discover_relationships([left, right])

        self.assertEqual(relationship.status, "validated_left_join")
        self.assertEqual(relationship.cardinality, "one_to_one")
        self.assertEqual(relationship.from_blank_keys, 1)

    def test_unmatched_nonblank_child_key_still_rejects_blank_aware_validation(self):
        details = Table("details", ["Mã đơn"], [["A1"], ["A2"], [None]], "details.csv")
        orders = Table("orders", ["Mã đơn"], [["A1"]], "orders.csv")

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.status, "candidate")
        self.assertEqual(relationship.from_unmatched_keys, 1)
        self.assertEqual(relationship.from_blank_keys, 1)

    def test_unmapped_generic_labels_never_create_relationships(self):
        left = Table("left", ["Giá trị"], [["A"], ["B"]], "left.csv")
        right = Table("right", ["Giá trị"], [["A"], ["B"]], "right.csv")

        self.assertEqual(discover_relationships([left, right]), [])

    def test_identifier_matching_preserves_leading_zeroes(self):
        details = Table("details", ["Mã đơn"], [["001"], ["002"]], "details.csv")
        orders = Table("orders", ["Mã đơn"], [["1"], ["2"]], "orders.csv")

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.status, "rejected")
        self.assertEqual(relationship.matched_distinct_keys, 0)


if __name__ == "__main__":
    unittest.main()

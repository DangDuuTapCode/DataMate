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

    def test_blank_child_key_prevents_validation(self):
        details = Table("details", ["Mã đơn"], [["A1"], [None]], "details.csv")
        orders = Table("orders", ["Mã đơn"], [["A1"]], "orders.csv")

        [relationship] = discover_relationships([details, orders])

        self.assertEqual(relationship.status, "rejected")
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

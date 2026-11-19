import unittest

from datamate.schema_catalog import build_schema_catalog
from datamate.types import Table


class BusinessSchemaCatalogTests(unittest.TestCase):
    def test_catalog_combines_semantics_and_relationship_evidence(self):
        details = Table(
            "order_details",
            ["Mã đơn", "Mã sản phẩm", "Số lượng"],
            [["A1", "P1", 2], ["A1", "P2", 1], ["A2", "P3", 4]],
            "details.csv",
        )
        orders = Table(
            "orders",
            ["Mã đơn", "Ngày đặt"],
            [["A1", "2026-01-01"], ["A2", "2026-01-02"]],
            "orders.csv",
        )

        catalog = build_schema_catalog([details, orders], business_id="biz_synthetic")

        self.assertEqual(catalog.business_id, "biz_synthetic")
        self.assertEqual(catalog.get_table_schema("order_details").mapped_fields, {
            "order_id": 0,
            "product_id": 1,
            "quantity": 2,
        })
        [relationship] = catalog.relationships_for(
            canonical_key="order_id", status="validated"
        )
        self.assertEqual(relationship.cardinality, "many_to_one")
        payload = catalog.to_dict()
        self.assertEqual(payload["schema_version"], "1.1.0")
        self.assertEqual(payload["business_id"], "biz_synthetic")
        self.assertEqual(payload["relationships"][0]["status"], "validated")

    def test_catalog_applies_only_explicit_rulebook_duplicate_line_policy(self):
        lots = Table(
            "chi_tiet_don_lo",
            ["Mã hóa đơn", "Số thứ tự", "Mã lô"],
            [["A1", 1, "L1"], ["A1", 1, "L2"]],
            "pos.sqlite",
        )
        details = Table(
            "chi_tiet_don",
            ["Mã hóa đơn", "Số thứ tự", "Mã hàng hóa"],
            [["A1", 1, "P1"], ["A1", 1, "P1"]],
            "pos.sqlite",
        )

        conservative = build_schema_catalog([lots, details])
        reviewed = build_schema_catalog(
            [lots, details], deduplicate_identical_order_lines=True
        )
        conservative_link = next(
            item for item in conservative.relationships
            if item.canonical_key == "order_id+order_line_number"
        )
        reviewed_link = next(
            item for item in reviewed.relationships
            if item.canonical_key == "order_id+order_line_number"
        )

        self.assertEqual(conservative_link.status, "ambiguous")
        self.assertEqual(reviewed_link.status, "validated")
        self.assertEqual(reviewed_link.cardinality, "many_to_one")

    def test_same_table_name_can_be_resolved_by_source(self):
        first = Table("orders", ["Mã đơn"], [["A1"]], "branch_a.csv")
        second = Table("orders", ["Mã khách hàng"], [["C1"]], "branch_b.csv")
        catalog = build_schema_catalog([first, second])

        self.assertIsNone(catalog.get_table_schema("orders"))
        self.assertEqual(catalog.get_table_schema("orders", "branch_a.csv").mapped_fields,
                         {"order_id": 0})
        self.assertEqual(catalog.get_table_schema("orders", "branch_b.csv").mapped_fields,
                         {"customer_id": 0})

    def test_catalog_does_not_infer_relationships_from_generic_headers(self):
        first = Table("payments", ["Giá trị"], [["A1"]], "a.csv")
        second = Table("orders", ["Giá trị"], [["A1"]], "b.csv")
        catalog = build_schema_catalog([first, second])

        self.assertEqual(catalog.relationships, ())
        self.assertEqual(catalog.relationships_for(status="validated"), ())


if __name__ == "__main__":
    unittest.main()

import unittest

from datamate.join_contracts import build_fact_join_contract
from datamate.relationship_paths import resolve_relationship_path
from datamate.relationships import discover_relationships
from datamate.semantic import map_table_schema
from datamate.types import Table


class ContestBiz129JoinContractTests(unittest.TestCase):
    def test_customer_group_revenue_path_preserves_guest_sales_with_left_join(self):
        # Header names and source roles mirror the README-documented
        # biz_129 exports. Rows are synthetic; no contest records are copied.
        details = Table(
            "chi_tiet_don",
            ["Số CT", "Mã hàng bán", "Tiền bán"],
            [
                ["ORD1", "SP1", "50000"],
                ["ORD1", "SP2", "30000"],
                ["ORD2", "SP1", "100000"],
            ],
            "chi_tiet_don.csv",
        )
        orders = Table(
            "don_hang",
            ["Số phiếu", "Mã khách mua", "Ngày bán", "Tình trạng đơn"],
            [
                ["ORD1", "KH1", "2025-10-01", "completed"],
                ["ORD2", "", "2025-10-02", "completed"],
            ],
            "don_hang.csv",
        )
        customers = Table(
            "khach_hang",
            ["Mã khách lẻ/sỉ", "Nhóm"],
            [["KH1", "thân thiết"]],
            "khach_hang.csv",
        )

        schemas = [map_table_schema(table) for table in (details, orders, customers)]
        self.assertEqual(schemas[0].mapped_fields["order_id"], 0)
        self.assertEqual(schemas[1].mapped_fields["order_id"], 0)
        self.assertEqual(schemas[1].mapped_fields["customer_id"], 1)
        self.assertEqual(schemas[2].mapped_fields["customer_id"], 0)

        relationships = discover_relationships([details, orders, customers])
        self.assertEqual(len(relationships), 2)
        self.assertEqual(
            {(item.canonical_key, item.status, item.cardinality) for item in relationships},
            {
                ("order_id", "validated", "many_to_one"),
                ("customer_id", "validated_left_join", "many_to_one"),
            },
        )

        path = resolve_relationship_path(
            relationships,
            ("chi_tiet_don", "chi_tiet_don.csv"),
            ("khach_hang", "khach_hang.csv"),
            max_hops=2,
        )
        self.assertEqual(path.status, "left_join_required")

        contract = build_fact_join_contract(
            path,
            ("chi_tiet_don", "chi_tiet_don.csv"),
            ("khach_hang", "khach_hang.csv"),
            fact_grain="one row per sales order detail line",
            measure_field="Tiền bán",
            measure_column_index=2,
            join_type="left",
        )
        self.assertIsNotNone(contract)
        self.assertEqual(contract.aggregation_stage, "after_join")
        self.assertTrue(contract.path_hops[1].requires_left_join)

        self.assertIsNone(build_fact_join_contract(
            path,
            ("chi_tiet_don", "chi_tiet_don.csv"),
            ("khach_hang", "khach_hang.csv"),
            fact_grain="one row per sales order detail line",
            measure_field="Tiền bán",
            measure_column_index=2,
            join_type="inner",
        ))


if __name__ == "__main__":
    unittest.main()

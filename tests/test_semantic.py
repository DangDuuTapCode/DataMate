import unittest

from datamate.semantic import map_table_schema
from datamate.types import Table


class SemanticMappingTests(unittest.TestCase):
    def test_exact_and_grouped_headers_map_with_evidence(self):
        table = Table(
            "orders",
            [
                "Thông tin đơn hàng / Mã đơn",
                "Thông tin đơn hàng / Ngày đặt",
                "Thanh toán / Giá trị",
                "Số lượng",
            ],
            [],
            "orders.xlsx",
        )

        schema = map_table_schema(table)

        self.assertEqual(schema.mapped_fields, {
            "order_id": 0,
            "order_date": 1,
            "payment_event_amount": 2,
            "quantity": 3,
        })
        self.assertEqual(schema.mappings[2].status, "mapped")
        self.assertIn("exact_group_and_leaf_alias", schema.mappings[2].evidence)
        self.assertEqual(schema.to_dict()["source"], "orders.xlsx")

    def test_contest_business_identifiers_map_only_exact_aliases(self):
        table = Table(
            "business_records",
            [
                "Mã hóa đơn", "Mã KH mua", "Mã hàng hóa", "Mã NV bán",
                "Mã NCC", "Mã phiếu nhập", "Mã lô", "Mã chi nhánh", "IMEI",
                "STT", "Mã tham chiếu",
            ],
            [],
            "business.xlsx",
        )

        schema = map_table_schema(table)

        self.assertEqual(schema.mapped_fields, {
            "order_id": 0,
            "customer_id": 1,
            "product_id": 2,
            "employee_id": 3,
            "supplier_id": 4,
            "purchase_receipt_id": 5,
            "batch_id": 6,
            "branch_id": 7,
            "imei": 8,
        })
        self.assertEqual(schema.mappings[9].status, "unmapped")
        self.assertEqual(schema.mappings[10].status, "unmapped")

    def test_generic_amount_and_total_labels_are_not_guessed(self):
        table = Table(
            "payment_history",
            ["Giá trị", "Thành tiền", "Ngày", "Trạng thái"],
            [],
            "payments.xlsx",
        )

        schema = map_table_schema(table)

        self.assertEqual(schema.mapped_fields, {})
        self.assertTrue(all(item.status == "unmapped" for item in schema.mappings))
        self.assertTrue(all(item.canonical_field is None for item in schema.mappings))

    def test_duplicate_source_columns_for_one_field_are_ambiguous(self):
        table = Table(
            "orders",
            ["Ngày đặt", "Order Date", "Mã đơn"],
            [],
            "orders.csv",
        )

        schema = map_table_schema(table)

        self.assertEqual(schema.mappings[0].status, "ambiguous")
        self.assertEqual(schema.mappings[1].status, "ambiguous")
        self.assertEqual(schema.mappings[0].candidate_field, "order_date")
        self.assertIsNone(schema.mappings[0].canonical_field)
        self.assertEqual(schema.mapped_fields, {"order_id": 2})

    def test_unknown_column_does_not_block_other_exact_mappings(self):
        table = Table(
            "sales",
            ["Mã sản phẩm", "Ghi chú nội bộ", "Tổng sau giảm giá"],
            [],
            "sales.xlsx",
        )

        schema = map_table_schema(table)

        self.assertEqual(schema.mapped_fields, {
            "product_id": 0,
            "order_total_after_discount": 2,
        })
        self.assertEqual(schema.mappings[1].status, "unmapped")


if __name__ == "__main__":
    unittest.main()

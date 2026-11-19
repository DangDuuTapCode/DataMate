import unittest

from datamate.split_rules import SplitRules


class SplitRuleDuplicateLinePolicyTests(unittest.TestCase):
    def test_explicit_same_order_duplicate_clause_enables_deduplication(self):
        rules = SplitRules.from_text(
            "| Hai dòng của **cùng một đơn** giống nhau ở mọi ô "
            "| lỗi xuất file, tính một lần. Hai dòng giống nhau của hai "
            "đơn khác nhau là hai lần bán, tính cả hai |"
        )

        self.assertTrue(rules.deduplicate_identical_order_lines)

    def test_missing_duplicate_clause_does_not_enable_deduplication(self):
        rules = SplitRules.from_text(
            "| Đơn tính vào doanh thu | Đơn không huỷ |\n"
            "| Doanh thu một đơn | Thành tiền các dòng |"
        )

        self.assertFalse(rules.deduplicate_identical_order_lines)

    def test_synthetic_defaults_include_the_explicit_test_policy(self):
        self.assertTrue(SplitRules.test_defaults().deduplicate_identical_order_lines)


if __name__ == "__main__":
    unittest.main()

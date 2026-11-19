import unittest

from datamate.relationship_paths import (
    RelationshipPathHop,
    RelationshipPathResolution,
    resolve_relationship_path,
)
from datamate.relationships import RelationshipCandidate
from datamate.join_contracts import build_fact_join_contract


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
        from_row_count=10,
        to_row_count=5,
        from_distinct_keys=5,
        to_distinct_keys=5,
        matched_distinct_keys=5,
        from_unmatched_keys=0,
        to_unmatched_keys=0,
        from_blank_keys=0,
        to_blank_keys=0,
        from_duplicate_excess=5,
        to_duplicate_excess=0,
        evidence=("synthetic_validated_relationship",),
    )


class FactJoinContractTests(unittest.TestCase):
    def setUp(self):
        self.fact = ("sales_detail", "sales.xlsx")
        self.orders = ("orders", "orders.xlsx")
        self.customers = ("customers", "customers.xlsx")
        self.path = resolve_relationship_path(
            [
                relationship(self.fact, self.orders, "order_id", "many_to_one", left_index=2, right_index=0),
                relationship(self.orders, self.customers, "customer_id", "many_to_one", left_index=3, right_index=1),
            ],
            self.fact,
            self.customers,
            max_hops=2,
        )

    def build(self, **overrides):
        args = {
            "fact_grain": "one row per sales order line",
            "measure_field": "net_line_amount",
            "measure_column_index": 7,
        }
        args.update(overrides)
        return build_fact_join_contract(
            self.path, self.fact, self.customers, **args
        )

    def test_builds_contract_for_unique_many_to_one_chain(self):
        contract = self.build()

        self.assertIsNotNone(contract)
        self.assertEqual(contract.fact_table, self.fact)
        self.assertEqual(contract.target_table, self.customers)
        self.assertEqual(contract.aggregation_stage, "after_join")
        self.assertEqual(contract.join_type, "inner")
        self.assertEqual(len(contract.path_hops), 2)
        self.assertEqual(contract.path_hops[0].from_column_indices, (2,))
        self.assertEqual(contract.path_hops[1].to_column_indices, (1,))

    def test_serialization_preserves_exact_source_and_key_indices(self):
        payload = self.build().to_dict()

        self.assertEqual(payload["fact_table"]["source"], "sales.xlsx")
        self.assertEqual(payload["target_table"]["source"], "customers.xlsx")
        self.assertEqual(payload["path_hops"][0]["from_column_indices"], [2])
        self.assertEqual(payload["path_hops"][1]["to_column_indices"], [1])

    def test_rejects_fanout_path(self):
        fanout = resolve_relationship_path(
            [relationship(self.fact, self.orders, "order_id", "one_to_many")],
            self.fact,
            self.orders,
            max_hops=1,
        )

        contract = build_fact_join_contract(
            fanout, self.fact, self.orders,
            fact_grain="one row per order line",
            measure_field="amount",
            measure_column_index=4,
        )

        self.assertIsNone(contract)

    def test_rejects_ambiguous_path(self):
        ambiguous = resolve_relationship_path(
            [
                relationship(self.fact, self.orders, "order_id", "many_to_one"),
                relationship(self.fact, self.customers, "customer_id", "many_to_one"),
                relationship(self.orders, self.customers, "customer_id", "many_to_one"),
            ],
            self.fact,
            self.customers,
            max_hops=2,
        )

        self.assertEqual(ambiguous.status, "ambiguous")
        self.assertIsNone(build_fact_join_contract(
            ambiguous, self.fact, self.customers,
            fact_grain="order line", measure_field="amount",
            measure_column_index=4,
        ))

    def test_rejects_path_that_does_not_match_declared_endpoints(self):
        self.assertIsNone(build_fact_join_contract(
            self.path, self.orders, self.customers,
            fact_grain="order line", measure_field="amount",
            measure_column_index=4,
        ))

    def test_rejects_pre_join_aggregation_until_supported(self):
        self.assertIsNone(self.build(aggregation_stage="before_join"))

    def test_rejects_invalid_measure_column_index(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value):
                self.assertIsNone(self.build(measure_column_index=value))

    def test_rejects_unknown_join_type_without_raising(self):
        for value in ("cross", [], None):
            with self.subTest(value=value):
                self.assertIsNone(self.build(join_type=value))

    def test_rejects_missing_grain_or_measure_declaration(self):
        self.assertIsNone(self.build(fact_grain=" "))
        self.assertIsNone(self.build(measure_field=" "))

    def test_rejects_unknown_cardinality_even_if_path_flag_claims_safe(self):
        malformed = RelationshipPathResolution(
            "unique_safe",
            hops=(RelationshipPathHop(
                self.fact, self.orders, ("order_id",), (2,), (0,),
                "many_to_many", False,
            ),),
            candidate_count=1,
        )

        self.assertIsNone(build_fact_join_contract(
            malformed, self.fact, self.orders,
            fact_grain="order line", measure_field="amount",
            measure_column_index=4,
        ))

    def test_rejects_candidate_count_that_does_not_prove_uniqueness(self):
        malformed = RelationshipPathResolution(
            "unique_safe",
            hops=(RelationshipPathHop(
                self.fact, self.orders, ("order_id",), (2,), (0,),
                "many_to_one", False,
            ),),
            candidate_count=2,
        )

        self.assertIsNone(build_fact_join_contract(
            malformed, self.fact, self.orders,
            fact_grain="order line", measure_field="amount",
            measure_column_index=4,
        ))

    def test_rejects_malformed_hop_identity_and_duplicate_keys(self):
        malformed_hops = (
            RelationshipPathHop(
                self.fact, ("", "orders.xlsx"), ("order_id",), (2,), (0,),
                "many_to_one", False,
            ),
            RelationshipPathHop(
                self.fact, self.orders, ("order_id", "order_id"), (2, 3), (0, 1),
                "many_to_one", False,
            ),
        )

        for hop in malformed_hops:
            with self.subTest(hop=hop):
                malformed = RelationshipPathResolution(
                    "unique_safe", hops=(hop,), candidate_count=1,
                )
                self.assertIsNone(build_fact_join_contract(
                    malformed, self.fact, self.orders,
                    fact_grain="order line", measure_field="amount",
                    measure_column_index=4,
                ))

    def test_rejects_repeated_table_in_manually_constructed_path(self):
        malformed = RelationshipPathResolution(
            "unique_safe",
            hops=(
                RelationshipPathHop(
                    self.fact, self.orders, ("order_id",), (2,), (0,),
                    "many_to_one", False,
                ),
                RelationshipPathHop(
                    self.orders, self.fact, ("order_id",), (0,), (2,),
                    "many_to_one", False,
                ),
                RelationshipPathHop(
                    self.fact, self.customers, ("customer_id",), (1,), (1,),
                    "many_to_one", False,
                ),
            ),
            candidate_count=1,
        )

        self.assertIsNone(build_fact_join_contract(
            malformed, self.fact, self.customers,
            fact_grain="order line", measure_field="amount",
            measure_column_index=4,
        ))


if __name__ == "__main__":
    unittest.main()

import unittest

from datamate.relationships import RelationshipCandidate
from datamate.relationship_paths import resolve_relationship_path


def edge(
    left, right, key, cardinality, *, status="validated",
    left_index=0, right_index=0,
):
    return RelationshipCandidate(
        from_table=left[0],
        from_source=left[1],
        to_table=right[0],
        to_source=right[1],
        canonical_key=key,
        from_column_index=left_index,
        to_column_index=right_index,
        cardinality=cardinality,
        status=status,
        confidence=1.0 if status == "validated" else 0.0,
        from_row_count=2,
        to_row_count=2,
        from_distinct_keys=2,
        to_distinct_keys=2,
        matched_distinct_keys=2,
        from_unmatched_keys=0,
        to_unmatched_keys=0,
        from_blank_keys=0,
        to_blank_keys=0,
        from_duplicate_excess=0,
        to_duplicate_excess=0,
        evidence=("synthetic_test",),
    )


class RelationshipPathTests(unittest.TestCase):
    def setUp(self):
        self.fact = ("sales", "sales.xlsx")
        self.orders = ("orders", "orders.xlsx")
        self.customers = ("customers", "customers.xlsx")

    def test_unique_many_to_one_chain_preserves_fact_grain(self):
        relationships = [
            edge(self.fact, self.orders, "order_id", "many_to_one"),
            edge(self.orders, self.customers, "customer_id", "many_to_one"),
        ]

        result = resolve_relationship_path(
            relationships, self.fact, self.customers, max_hops=2
        )

        self.assertTrue(result.available)
        self.assertEqual(result.status, "unique_safe")
        self.assertEqual(len(result.hops), 2)
        self.assertEqual(
            [hop.canonical_keys for hop in result.hops],
            [("order_id",), ("customer_id",)],
        )
        self.assertFalse(any(hop.fanout for hop in result.hops))

    def test_one_to_many_traversal_is_rejected_as_fanout_risk(self):
        relationships = [
            edge(self.fact, self.orders, "order_id", "many_to_one"),
            edge(self.orders, self.customers, "customer_id", "one_to_many"),
        ]

        result = resolve_relationship_path(
            relationships, self.fact, self.customers, max_hops=2
        )

        self.assertFalse(result.available)
        self.assertEqual(result.status, "fanout_risk")
        self.assertIn("path_contains_one_to_many_traversal", result.reasons)
        self.assertTrue(result.hops[-1].fanout)

    def test_multiple_validated_paths_are_ambiguous(self):
        bridge_a = ("bridge_a", "a.xlsx")
        bridge_b = ("bridge_b", "b.xlsx")
        relationships = [
            edge(self.fact, bridge_a, "order_id", "many_to_one"),
            edge(bridge_a, self.customers, "customer_id", "many_to_one"),
            edge(self.fact, bridge_b, "order_id", "many_to_one"),
            edge(bridge_b, self.customers, "customer_id", "many_to_one"),
        ]

        result = resolve_relationship_path(
            relationships, self.fact, self.customers, max_hops=2
        )

        self.assertEqual(result.status, "ambiguous")
        self.assertEqual(result.candidate_count, 2)
        self.assertEqual(result.hops, ())

    def test_unvalidated_relationships_are_not_traversable(self):
        relationships = [
            edge(self.fact, self.orders, "order_id", "many_to_one", status="candidate"),
            edge(self.orders, self.customers, "customer_id", "many_to_one"),
        ]

        result = resolve_relationship_path(
            relationships, self.fact, self.customers, max_hops=2
        )

        self.assertEqual(result.status, "no_path")

    def test_table_identity_includes_source_filename(self):
        same_named_table = ("sales", "archive.xlsx")
        relationships = [
            edge(same_named_table, self.orders, "order_id", "many_to_one"),
            edge(self.orders, self.customers, "customer_id", "many_to_one"),
        ]

        result = resolve_relationship_path(
            relationships, self.fact, self.customers, max_hops=2
        )

        self.assertEqual(result.status, "no_path")

    def test_composite_relationship_preserves_all_key_columns(self):
        relationship = edge(
            self.fact, self.orders, "order_id+order_line_number", "many_to_one",
            left_index=1, right_index=2,
        )
        relationship = RelationshipCandidate(
            **{
                **relationship.__dict__,
                "canonical_keys": ("order_id", "order_line_number"),
                "from_column_indices": (1, 3),
                "to_column_indices": (2, 4),
            }
        )

        result = resolve_relationship_path(
            [relationship], self.fact, self.orders, max_hops=1
        )

        self.assertTrue(result.available)
        self.assertEqual(result.hops[0].canonical_keys, ("order_id", "order_line_number"))
        self.assertEqual(result.hops[0].from_column_indices, (1, 3))
        self.assertEqual(result.hops[0].to_column_indices, (2, 4))

    def test_invalid_path_arguments_fail_closed(self):
        result = resolve_relationship_path([], "sales", self.orders)

        self.assertEqual(result.status, "invalid_request")


    def test_candidate_limit_allows_exactly_one_path(self):
        result = resolve_relationship_path(
            [edge(self.fact, self.orders, "order_id", "many_to_one")],
            self.fact,
            self.orders,
            max_candidates=1,
        )

        self.assertTrue(result.available)
        self.assertEqual(result.candidate_count, 1)

    def test_candidate_limit_rejects_more_than_configured_bound(self):
        bridge_a = ("bridge_a", "a.xlsx")
        bridge_b = ("bridge_b", "b.xlsx")
        relationships = [
            edge(self.fact, bridge_a, "order_id", "many_to_one"),
            edge(bridge_a, self.customers, "customer_id", "many_to_one"),
            edge(self.fact, bridge_b, "order_id", "many_to_one"),
            edge(bridge_b, self.customers, "customer_id", "many_to_one"),
        ]

        result = resolve_relationship_path(
            relationships,
            self.fact,
            self.customers,
            max_hops=2,
            max_candidates=1,
        )

        self.assertEqual(result.status, "ambiguous")
        self.assertEqual(result.candidate_count, 2)
        self.assertIn("candidate_path_limit_reached", result.reasons)

    def test_reverse_many_to_one_traversal_is_fanout(self):
        result = resolve_relationship_path(
            [edge(self.fact, self.orders, "order_id", "many_to_one")],
            self.fact,
            self.orders,
            max_hops=1,
        )

        self.assertEqual(result.status, "fanout_risk")
        self.assertTrue(result.hops[0].fanout)

    def test_hop_limit_is_enforced(self):
        result = resolve_relationship_path(
            [
                edge(self.fact, self.orders, "order_id", "many_to_one"),
                edge(self.orders, self.customers, "customer_id", "many_to_one"),
            ],
            self.fact,
            self.customers,
            max_hops=1,
        )

        self.assertEqual(result.status, "no_path")

    def test_nonpositive_or_noninteger_limits_fail_closed(self):
        for kwargs in (
            {"max_hops": 0},
            {"max_hops": True},
            {"max_candidates": 0},
            {"max_candidates": 1.5},
        ):
            with self.subTest(kwargs=kwargs):
                result = resolve_relationship_path(
                    [], self.fact, self.orders, **kwargs
                )
                self.assertEqual(result.status, "invalid_request")

    def test_cycles_do_not_repeat_a_table(self):
        bridge = ("bridge", "bridge.xlsx")
        relationships = [
            edge(self.fact, self.customers, "customer_id", "many_to_one"),
            edge(self.fact, self.orders, "order_id", "many_to_one"),
            edge(self.orders, bridge, "customer_id", "many_to_one"),
            edge(bridge, self.orders, "customer_id", "one_to_many"),
        ]

        result = resolve_relationship_path(
            relationships, self.fact, self.customers, max_hops=3
        )

        self.assertTrue(result.available)
        self.assertEqual(len(result.hops), 3)


if __name__ == "__main__":
    unittest.main()

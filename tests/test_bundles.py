import unittest

from datamate.bundles import BundleDefinition, BundleRegistry, default_bundle_registry


class BundleRegistryTests(unittest.TestCase):
    def test_default_registry_resolves_existing_financial_metrics(self):
        registry = default_bundle_registry()
        revenue = registry.resolve("revenue")
        collection = registry.resolve("collected_amount")
        self.assertEqual((revenue.bundle_id, revenue.executor_intent), ("revenue", "revenue"))
        self.assertEqual((collection.bundle_id, collection.executor_intent),
                         ("collection", "collected_amount"))
        self.assertIn("eligible_sales_amount", revenue.required_capabilities)
        self.assertEqual(collection.rule_profile, "collection_rules")

    def test_unknown_or_duplicate_requirements_do_not_resolve(self):
        registry = default_bundle_registry()
        self.assertIsNone(registry.resolve_many(("revenue", "unknown_metric")))
        self.assertIsNone(registry.resolve_many(("revenue", "revenue")))

    def test_registry_rejects_duplicate_metric_or_bundle_ids(self):
        first = BundleDefinition("sales", "revenue", "revenue")
        duplicate_metric = BundleDefinition("sales_v2", "revenue", "revenue")
        with self.assertRaisesRegex(ValueError, "duplicate metric"):
            BundleRegistry((first, duplicate_metric))
        duplicate_bundle = BundleDefinition("sales", "quantity", "quantity")
        with self.assertRaisesRegex(ValueError, "duplicate bundle"):
            BundleRegistry((first, duplicate_bundle))

    def test_registry_rejects_unsupported_output_types(self):
        invalid = BundleDefinition("custom", "custom_metric", "custom_metric", output_type="object")
        with self.assertRaisesRegex(ValueError, "unsupported bundle output type"):
            BundleRegistry((invalid,))


if __name__ == "__main__":
    unittest.main()

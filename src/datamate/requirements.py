"""Requirement extraction separated from composite plan compilation.

This first version translates only already-recognized QuerySpec intents into
allowlisted metric requirements. It does not split arbitrary conjunctions.
"""
from dataclasses import dataclass

from .bundles import BundleRegistry, default_bundle_registry


@dataclass(frozen=True)
class MetricRequirement:
    requirement_id: str
    metric: str
    bundle_id: str
    executor_intent: str
    expected_type: str
    required_capabilities: tuple[str, ...]
    rule_profile: str


@dataclass(frozen=True)
class RequirementExtraction:
    status: str
    comparison_type: str | None
    requirements: tuple[MetricRequirement, ...]
    reason: str | None = None


class RequirementExtractor:
    """Convert recognized composite intents into explicit bundle requirements."""

    COMPOSITE_INTENTS = {
        "financial_metric_comparison": {
            "metrics": ("revenue", "collected_amount"),
            "comparison_type": "side_by_side",
        },
    }

    def __init__(self, bundle_registry=None):
        self.bundle_registry = bundle_registry or default_bundle_registry()

    def extract(self, spec):
        if spec is None:
            return RequirementExtraction("unsupported", None, (), "missing_query_spec")

        rule = self.COMPOSITE_INTENTS.get(spec.intent)
        if rule is None:
            return RequirementExtraction("unsupported", None, (), "no_composite_requirement_rule")

        definitions = self.bundle_registry.resolve_many(rule["metrics"])
        if definitions is None:
            return RequirementExtraction("unresolved", rule["comparison_type"], (), "bundle_not_resolved")

        requirements = tuple(
            MetricRequirement(
                requirement_id=f"R{index}",
                metric=bundle.metric_id,
                bundle_id=bundle.bundle_id,
                executor_intent=bundle.executor_intent,
                expected_type=bundle.output_type,
                required_capabilities=bundle.required_capabilities,
                rule_profile=bundle.rule_profile,
            )
            for index, bundle in enumerate(definitions, start=1)
        )
        return RequirementExtraction(
            status="resolved",
            comparison_type=rule["comparison_type"],
            requirements=requirements,
        )

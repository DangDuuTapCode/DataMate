"""Requirement extraction separated from composite plan compilation.

This first version translates only already-recognized QuerySpec intents into
allowlisted metric requirements. It does not split arbitrary conjunctions.
"""
from dataclasses import dataclass
import json
from pathlib import Path

from .bundles import BundleRegistry, default_bundle_registry
from .query_schema import validate_payload


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
    schema_version: str = "1.0.0"


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


REQUIREMENT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "requirement_extraction.v1.schema.json"
)


def load_requirement_extraction_schema():
    return json.loads(REQUIREMENT_SCHEMA_PATH.read_text(encoding="utf-8"))


def requirement_extraction_payload(extraction):
    return {
        "schema_version": extraction.schema_version,
        "status": extraction.status,
        "comparison_type": extraction.comparison_type,
        "requirements": [
            {
                "requirement_id": item.requirement_id,
                "metric": item.metric,
                "bundle_id": item.bundle_id,
                "executor_intent": item.executor_intent,
                "expected_type": item.expected_type,
                "required_capabilities": list(item.required_capabilities),
                "rule_profile": item.rule_profile,
            }
            for item in extraction.requirements
        ],
        "reason": extraction.reason,
    }


def validate_requirement_extraction_payload(payload, schema=None):
    """Validate the versioned requirement contract and its cross-field invariants."""
    errors = validate_payload(payload, schema or load_requirement_extraction_schema())
    if errors:
        return errors
    requirements = payload["requirements"]
    if payload["status"] == "resolved" and len(requirements) < 2:
        errors.append("$.requirements: resolved composite requires at least two requirements")
    if payload["status"] != "resolved" and requirements:
        errors.append("$.requirements: unresolved extraction must not contain executable requirements")
    ids = [item["requirement_id"] for item in requirements]
    metrics = [item["metric"] for item in requirements]
    if len(ids) != len(set(ids)):
        errors.append("$.requirements: requirement IDs must be unique")
    if len(metrics) != len(set(metrics)):
        errors.append("$.requirements: metric IDs must be unique")
    if payload["status"] == "resolved" and payload["reason"] is not None:
        errors.append("$.reason: resolved extraction must not include a failure reason")
    if payload["status"] != "resolved" and not payload["reason"]:
        errors.append("$.reason: unresolved extraction requires a reason")
    return errors

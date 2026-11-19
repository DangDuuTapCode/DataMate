"""Composite query planning for questions that require multiple metric bundles.

The first supported vertical slice is a side-by-side comparison of revenue and
collected amount over one explicit period. Existing single-metric executors
remain the source of truth for each component.
"""
from dataclasses import dataclass, replace

from .bundle_capabilities import BundleCapabilityResolver
from .requirements import (
    MetricRequirement,
    RequirementExtractor,
    requirement_extraction_payload,
    validate_requirement_extraction_payload,
)
from .normalise import fold
from .output import valid_record
from .types import QueryPlan, QuerySpec
from .verify import verify_with_reason


@dataclass(frozen=True)
class QueryComponent:
    requirement: MetricRequirement
    query_spec: QuerySpec
    query_plan: QueryPlan


@dataclass(frozen=True)
class CompositeQueryPlan:
    raw_question: str
    comparison_type: str
    period_start: str
    period_end: str
    entity: str | None
    components: tuple[QueryComponent, ...]
    output_columns: tuple[str, ...] = ("metric", "value")


class CompositePlanner:
    """Build a composite plan only for explicitly supported combinations."""

    def __init__(
        self, rule_planner, bundle_registry=None, composite_rule_registry=None,
        schema_catalog=None, rule_evidence=None,
    ):
        self.rule_planner = rule_planner
        self.requirement_extractor = RequirementExtractor(
            bundle_registry, composite_rule_registry
        )
        self.schema_catalog = schema_catalog
        self.rule_evidence = rule_evidence
        self.capability_resolver = BundleCapabilityResolver()
        self.last_capability_resolutions = []

    def plan(self, spec: QuerySpec | None) -> CompositeQueryPlan | None:
        self.last_capability_resolutions = []
        if spec is None:
            return None
        if spec.time is None or spec.time.kind != "period":
            return None
        if not spec.time.start or not spec.time.end:
            return None
        if "entity_unresolved" in spec.ambiguity_flags:
            return None
        if spec.filters:
            return None
        if any(dimension != "metric" for dimension in spec.dimensions):
            return None
        if spec.sort is not None or spec.top_k != 1:
            return None
        if spec.unit and fold(spec.unit) not in {"vnd"}:
            return None

        question = spec.raw_question
        if self.rule_planner._has_unresolved_entity_filter(question) and spec.entity is None:
            return None
        if self.rule_planner._has_unimplemented_breakdown(question):
            return None
        if self.rule_planner._has_unimplemented_monthly_output(question):
            return None

        # This first slice returns both metrics side by side. It does not yet
        # implement arithmetic differences or cross-period comparisons.
        normalized_question = fold(question)
        if any(cue in normalized_question for cue in (
            "chenh lech", "chenhlech", "difference", "cao hon bao nhieu",
            "thap hon bao nhieu", "how much more", "how much less",
        )):
            return None

        extraction = self.requirement_extractor.extract(spec)
        extraction_payload = requirement_extraction_payload(extraction)
        if validate_requirement_extraction_payload(extraction_payload):
            return None
        if extraction.status != "resolved" or len(extraction.requirements) < 2:
            return None
        if extraction.comparison_type != "side_by_side":
            return None
        if any(
            requirement.expected_type != "number"
            for requirement in extraction.requirements
        ):
            return None

        components = []
        for requirement in extraction.requirements:
            bundle = self.requirement_extractor.bundle_registry.resolve(requirement.metric)
            if bundle is None or not bundle.supports_period:
                return None
            if self.schema_catalog is not None:
                resolution = self.capability_resolver.resolve(
                    bundle, self.schema_catalog, self.rule_evidence
                )
                self.last_capability_resolutions.append(resolution.to_dict())
                if not resolution.available:
                    return None
            if spec.entity is not None and not bundle.supports_entity:
                return None
            component_spec = replace(
                spec,
                intent=requirement.executor_intent,
                metric=requirement.metric,
                dimensions=(),
                filters=(),
                executable=True,
                evidence=tuple(spec.evidence) + (f"component:{requirement.metric}",),
                unsupported_reason=None,
                sort=None,
            )
            component_plan = QueryPlan(
                intent=requirement.executor_intent,
                start=spec.time.start,
                end=spec.time.end,
                confidence=spec.confidence,
                entity=spec.entity,
                top_k=1,
                evidence=component_spec.evidence,
            )
            components.append(QueryComponent(requirement, component_spec, component_plan))

        return CompositeQueryPlan(
            raw_question=question,
            comparison_type="side_by_side",
            period_start=spec.time.start,
            period_end=spec.time.end,
            entity=spec.entity,
            components=tuple(components),
        )


def verify_composite_with_reason(question_id, composite_plan, component_results, *, error=None):
    """Verify every component, then validate the complete table as one answer.

    component_results contains ordered (candidate, execution_reason) pairs.
    A required component failure abstains the entire composite query.
    """
    if error is not None:
        return verify_with_reason(question_id, None, None, error=error)

    if len(component_results) != len(composite_plan.components):
        return (
            {"id": question_id, "type": "abstain"},
            {"status": "abstained", "reason_code": "unsupported_intent"},
        )

    verified_rows, evidence, component_decisions = [], [], []
    for component, result in zip(composite_plan.components, component_results):
        candidate, execution_reason = result
        record, decision = verify_with_reason(
            question_id, candidate, component.query_plan,
            spec=component.query_spec, execution_reason=execution_reason,
        )
        if record.get("type") == "abstain":
            return (
                {"id": question_id, "type": "abstain"},
                {
                    "status": "abstained",
                    "reason_code": decision["reason_code"],
                    "failed_requirement": component.requirement.requirement_id,
                    "component_decisions": component_decisions,
                },
            )

        value = record.get("answer")
        if (record.get("type") != component.requirement.expected_type
                or isinstance(value, bool) or not isinstance(value, (int, float))):
            return (
                {"id": question_id, "type": "abstain"},
                {
                    "status": "abstained",
                    "reason_code": "verification_failed",
                    "failed_requirement": component.requirement.requirement_id,
                    "component_decisions": component_decisions,
                },
            )

        verified_rows.append([component.requirement.metric, value])
        evidence.extend(candidate.get("evidence", []))
        component_decisions.append({
            "requirement_id": component.requirement.requirement_id,
            "status": "answered",
            "reason_code": None,
        })

    record = {
        "id": question_id,
        "type": "table",
        "answer": {
            "columns": list(composite_plan.output_columns),
            "rows": verified_rows,
        },
    }
    if not valid_record(record) or len(verified_rows) != len(composite_plan.components):
        return (
            {"id": question_id, "type": "abstain"},
            {"status": "abstained", "reason_code": "verification_failed"},
        )

    return record, {
        "status": "answered",
        "reason_code": None,
        "component_decisions": component_decisions,
        "evidence": list(dict.fromkeys(evidence)),
    }

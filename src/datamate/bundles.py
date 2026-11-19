"""Declarative registry for logical metric bundles used by query planning."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredRelationship:
    """A validated relationship shape a bundle needs before it can be used."""

    canonical_key: str
    cardinality: str = "many_to_one"

    def __post_init__(self):
        if not self.canonical_key:
            raise ValueError("relationship canonical key must be non-empty")
        if self.cardinality not in {"one_to_one", "one_to_many", "many_to_one"}:
            raise ValueError("unsupported required relationship cardinality")


@dataclass(frozen=True)
class BundleDefinition:
    bundle_id: str
    metric_id: str
    executor_intent: str
    output_type: str = "number"
    required_capabilities: tuple[str, ...] = ()
    rule_profile: str = ""
    supports_period: bool = True
    supports_entity: bool = True
    required_fields: tuple[str, ...] = ()
    required_relationships: tuple[RequiredRelationship, ...] = ()


class BundleRegistry:
    """Resolve metric requirements to explicit, allowlisted bundle definitions."""

    def __init__(self, definitions):
        self._by_metric = {}
        bundle_ids = set()
        for definition in definitions:
            if not definition.bundle_id or not definition.metric_id or not definition.executor_intent:
                raise ValueError("bundle identifiers and executor intent must be non-empty")
            if definition.metric_id in self._by_metric:
                raise ValueError(f"duplicate metric definition: {definition.metric_id}")
            if definition.bundle_id in bundle_ids:
                raise ValueError(f"duplicate bundle definition: {definition.bundle_id}")
            if definition.output_type not in {"number", "percent", "date", "string", "table", "list"}:
                raise ValueError(f"unsupported bundle output type: {definition.output_type}")
            if len(set(definition.required_fields)) != len(definition.required_fields):
                raise ValueError("required fields must be unique")
            self._by_metric[definition.metric_id] = definition
            bundle_ids.add(definition.bundle_id)

    def resolve(self, metric_id):
        return self._by_metric.get(metric_id)

    def resolve_many(self, metric_ids):
        requested = tuple(metric_ids)
        if len(set(requested)) != len(requested):
            return None
        definitions = tuple(self.resolve(metric_id) for metric_id in requested)
        if any(definition is None for definition in definitions):
            return None
        return definitions

    @property
    def metric_ids(self):
        return tuple(sorted(self._by_metric))


def default_bundle_registry():
    """Known first-slice bundles; business calculations remain in existing executors."""
    return BundleRegistry((
        BundleDefinition(
            bundle_id="revenue",
            metric_id="revenue",
            executor_intent="revenue",
            required_capabilities=(
                "eligible_sales_amount",
                "sale_period",
                "order_status_semantics",
            ),
            required_fields=("order_total_after_discount", "order_date", "order_status"),
            rule_profile="revenue_rules",
        ),
        BundleDefinition(
            bundle_id="collection",
            metric_id="collected_amount",
            executor_intent="collected_amount",
            required_capabilities=("settled_payment_status",),
            required_fields=("payment_event_amount", "payment_date", "payment_status"),
            rule_profile="collection_rules",
        ),
    ))

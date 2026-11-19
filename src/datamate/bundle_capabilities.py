"""Fail-closed validation of structural and business-rule bundle evidence."""
from dataclasses import dataclass

from .bundles import RequiredRelationship


@dataclass(frozen=True)
class BundleCapabilityResolution:
    bundle_id: str
    status: str
    missing_fields: tuple[str, ...] = ()
    ambiguous_fields: tuple[str, ...] = ()
    field_group_conflicts: tuple[tuple[str, ...], ...] = ()
    missing_relationships: tuple = ()
    rejected_relationships: tuple = ()
    unverified_capabilities: tuple[str, ...] = ()
    rejected_capabilities: tuple[str, ...] = ()
    rule_profile_version: str | None = None
    reasons: tuple[str, ...] = ()

    @property
    def available(self):
        return self.status == "available"

    def to_dict(self):
        return {
            "bundle_id": self.bundle_id,
            "status": self.status,
            "available": self.available,
            "missing_fields": list(self.missing_fields),
            "ambiguous_fields": list(self.ambiguous_fields),
            "field_group_conflicts": [list(group) for group in self.field_group_conflicts],
            "missing_relationships": [
                {"canonical_key": item.canonical_key, "cardinality": item.cardinality}
                for item in self.missing_relationships
            ],
            "rejected_relationships": [item.to_dict() for item in self.rejected_relationships],
            "unverified_capabilities": list(self.unverified_capabilities),
            "rejected_capabilities": list(self.rejected_capabilities),
            "rule_profile_version": self.rule_profile_version,
            "reasons": list(self.reasons),
        }


class BundleCapabilityResolver:
    """Resolve exact schema requirements and reviewed rule evidence.

    Evidence only counts for the matching business and exact scoped table
    identities. This class does not infer business meaning or execute joins.
    """

    @staticmethod
    def _verified_claims(bundle, schema_catalog, rule_evidence):
        if (
            rule_evidence is None
            or not bundle.rule_profile
            or rule_evidence.business_id != schema_catalog.business_id
        ):
            return {}, {}, None

        profile = rule_evidence.profile(bundle.rule_profile)
        if profile is None:
            return {}, {}, None

        known_tables = {
            (item.table_name, item.source)
            for item in schema_catalog.table_schemas
        }
        verified, rejected = {}, {}
        for claim in profile.evidence:
            scope_exists = all(
                (table.table_name, table.source) in known_tables
                for table in claim.table_scope
            )
            if not scope_exists:
                continue
            if claim.status == "verified":
                verified[claim.capability_id] = claim
            elif claim.status == "rejected":
                rejected[claim.capability_id] = claim
        return verified, rejected, profile.version

    def resolve(self, bundle, schema_catalog, rule_evidence=None):
        if schema_catalog is None:
            raise ValueError("schema catalog is required")

        mapped_by_table = []
        all_mappings = []
        for table_schema in schema_catalog.table_schemas:
            mapped = {
                item.canonical_field
                for item in table_schema.mappings
                if item.status == "mapped" and item.canonical_field is not None
            }
            mapped_by_table.append(mapped)
            all_mappings.extend(table_schema.mappings)

        missing_fields = []
        ambiguous_fields = []
        for field in bundle.required_fields:
            if any(
                item.candidate_field == field and item.status == "ambiguous"
                for item in all_mappings
            ):
                ambiguous_fields.append(field)
            elif not any(field in mapped for mapped in mapped_by_table):
                missing_fields.append(field)

        field_group_conflicts = []
        if (bundle.required_fields and not missing_fields and not ambiguous_fields
                and not any(set(bundle.required_fields).issubset(mapped)
                            for mapped in mapped_by_table)):
            field_group_conflicts.append(tuple(bundle.required_fields))

        missing_relationships = []
        rejected_relationships = []
        for required in bundle.required_relationships:
            matching = [
                item for item in schema_catalog.relationships
                if item.canonical_key == required.canonical_key
            ]
            validated = [
                item for item in matching
                if item.status == "validated" and item.cardinality == required.cardinality
            ]
            if validated:
                continue
            rejected = [
                item for item in matching
                if item.status in {"rejected", "ambiguous"}
                or (item.status == "validated" and item.cardinality != required.cardinality)
            ]
            if rejected:
                rejected_relationships.extend(rejected)
            else:
                missing_relationships.append(required)

        verified, rejected, profile_version = self._verified_claims(
            bundle, schema_catalog, rule_evidence
        )
        unverified_capabilities = []
        rejected_capabilities = []
        for capability in bundle.required_capabilities:
            if capability in verified:
                continue
            if capability in rejected:
                rejected_capabilities.append(capability)
            else:
                unverified_capabilities.append(capability)

        shape = verified.get("revenue_executor_source_shape")
        if shape is not None:
            shape_scope = tuple((x.table_name, x.source) for x in shape.table_scope)
            if shape.assertion == "direct_line":
                if len(shape_scope) != 1:
                    unverified_capabilities.append("revenue_executor_source_shape")
            elif shape.assertion == "detail_to_order":
                if len(shape.table_scope) != 2 or len({x.table_name for x in shape.table_scope}) != 2:
                    unverified_capabilities.append("revenue_executor_source_shape")
                else:
                    line_table, order_table = shape.table_scope
                    relation = [
                        item for item in schema_catalog.relationships
                        if item.from_table == line_table.table_name
                        and item.to_table == order_table.table_name
                        and item.canonical_key == "order_id"
                    ]
                    if any(
                        item.status == "validated" and item.cardinality == "many_to_one"
                        for item in relation
                    ):
                        pass
                    elif any(
                        item.status in {"rejected", "ambiguous"}
                        or (item.status == "validated" and item.cardinality != "many_to_one")
                        for item in relation
                    ):
                        rejected_relationships.extend(
                            item for item in relation
                            if item.status in {"rejected", "ambiguous"}
                            or (item.status == "validated" and item.cardinality != "many_to_one")
                        )
                    else:
                        missing_relationships.append(RequiredRelationship("order_id", "many_to_one"))
            else:
                unverified_capabilities.append("revenue_executor_source_shape")

            for capability in (
                "eligible_sales_amount", "sale_period", "order_status_semantics"
            ):
                claim = verified.get(capability)
                if claim is not None:
                    claim_scope = {
                        (x.table_name, x.source) for x in claim.table_scope
                    }
                    if not claim_scope or not claim_scope.issubset(set(shape_scope)):
                        unverified_capabilities.append(capability)

        if bundle.rule_profile == "collection_rules":
            role = verified.get("payment_source_role")
            policy = verified.get("settled_payment_status_policy")
            if role is not None and policy is not None:
                role_scope = tuple((x.table_name, x.source) for x in role.table_scope)
                policy_scope = tuple((x.table_name, x.source) for x in policy.table_scope)
                if len(role_scope) != 1 or role_scope != policy_scope:
                    for capability in ("payment_source_role", "settled_payment_status_policy"):
                        if capability not in unverified_capabilities:
                            unverified_capabilities.append(capability)

        unverified_capabilities = sorted(set(unverified_capabilities))
        rejected_capabilities = sorted(set(rejected_capabilities))
        reasons = []
        if missing_fields:
            reasons.append("missing_required_fields")
        if ambiguous_fields:
            reasons.append("ambiguous_required_fields")
        if field_group_conflicts:
            reasons.append("required_fields_not_co_located")
        if missing_relationships:
            reasons.append("missing_required_relationships")
        if rejected_relationships:
            reasons.append("rejected_required_relationships")
        if rejected_capabilities:
            reasons.append("business_rule_capabilities_rejected")
        if unverified_capabilities:
            reasons.append("business_rule_capabilities_unverified")

        return BundleCapabilityResolution(
            bundle_id=bundle.bundle_id,
            status="available" if not reasons else "unavailable",
            missing_fields=tuple(sorted(missing_fields)),
            ambiguous_fields=tuple(sorted(ambiguous_fields)),
            field_group_conflicts=tuple(field_group_conflicts),
            missing_relationships=tuple(missing_relationships),
            rejected_relationships=tuple(rejected_relationships),
            unverified_capabilities=tuple(unverified_capabilities),
            rejected_capabilities=tuple(rejected_capabilities),
            rule_profile_version=profile_version,
            reasons=tuple(reasons),
        )

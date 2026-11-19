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

    def resolve(self, bundle, schema_catalog, rule_evidence=None, *, split_rules=None):
        if schema_catalog is None:
            raise ValueError("schema catalog is required")

        mapped_by_table = {}
        all_mappings_by_table = {}
        for table_schema in schema_catalog.table_schemas:
            table_id = (table_schema.table_name, table_schema.source)
            all_mappings_by_table[table_id] = table_schema.mappings
            mapped_by_table[table_id] = {
                item.canonical_field
                for item in table_schema.mappings
                if item.status == "mapped" and item.canonical_field is not None
            }

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

        # A provenance claim is not sufficient if the active split rulebook
        # or deterministic executor profile does not implement that policy.
        if bundle.rule_profile == "revenue_rules":
            required_exclusions = {"cancelled", "returned", "delivery_failed"}
            checks = {
                "eligible_sales_amount": (
                    split_rules is not None
                    and split_rules.revenue_amount_basis == "line_amount_after_line_discount"
                ),
                "sale_period": split_rules is not None and split_rules.revenue_period_basis is not None,
                "order_status_semantics": (
                    split_rules is not None
                    and required_exclusions.issubset(split_rules.revenue_excluded_statuses)
                ),
            }
            for capability, compatible in checks.items():
                claim = verified.get(capability)
                if claim is None:
                    continue
                expected_assertion = (
                    split_rules.revenue_period_basis
                    if capability == "sale_period" and split_rules is not None
                    else "line_amount_after_line_discount"
                    if capability == "eligible_sales_amount"
                    else "exclude_cancelled_returned_failed"
                )
                if not compatible or claim.assertion != expected_assertion:
                    verified.pop(capability, None)
                    unverified_capabilities.append(capability)
        elif bundle.rule_profile == "collection_rules":
            claim = verified.get("settled_payment_status_policy")
            if claim is not None and (
                split_rules is None
                or split_rules.collection_status_policy != claim.assertion
            ):
                verified.pop("settled_payment_status_policy", None)
                unverified_capabilities.append("settled_payment_status_policy")

        # Collection fields must be present together in the exact single table
        # reviewed for both payment-source role and settlement policy.
        field_scope = None
        scope_mismatch = False
        if bundle.rule_profile == "collection_rules":
            role = verified.get("payment_source_role")
            policy = verified.get("settled_payment_status_policy")
            if role is not None and policy is not None:
                role_scope = tuple((x.table_name, x.source) for x in role.table_scope)
                policy_scope = tuple((x.table_name, x.source) for x in policy.table_scope)
                if len(role_scope) == 1 and role_scope == policy_scope:
                    field_scope = set(role_scope)
                else:
                    scope_mismatch = True
                    for capability in ("payment_source_role", "settled_payment_status_policy"):
                        if capability not in unverified_capabilities:
                            unverified_capabilities.append(capability)
                    field_scope = set()

        field_table_ids = field_scope if field_scope is not None else set(mapped_by_table)
        missing_fields = []
        ambiguous_fields = []
        for field in bundle.required_fields:
            mappings = [
                item
                for table_id in field_table_ids
                for item in all_mappings_by_table.get(table_id, ())
            ]
            if any(
                item.candidate_field == field and item.status == "ambiguous"
                for item in mappings
            ):
                ambiguous_fields.append(field)
            elif not any(
                field in mapped_by_table.get(table_id, set())
                for table_id in field_table_ids
            ):
                missing_fields.append(field)

        field_group_conflicts = []
        if (bundle.required_fields and not missing_fields and not ambiguous_fields
                and not any(
                    set(bundle.required_fields).issubset(mapped_by_table.get(table_id, set()))
                    for table_id in field_table_ids
                )):
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

        shape = verified.get("revenue_executor_source_shape")
        if shape is not None:
            shape_scope = tuple((x.table_name, x.source) for x in shape.table_scope)
            shape_names = [name for name, _ in shape_scope]
            assertion = shape.assertion
            direct_shape = assertion == "direct_line" and len(shape_scope) == 1
            detail_shape = assertion == "detail_to_order" and len(shape_scope) == 2
            if not (direct_shape or detail_shape) or len(set(shape_names)) != len(shape_names):
                unverified_capabilities.append("revenue_executor_source_shape")
            elif len(shape_scope) == 2:
                line_table, order_table = shape.table_scope
                line_name, order_name = line_table.table_name, order_table.table_name
                matching = [
                    item for item in schema_catalog.relationships
                    if item.canonical_key == "order_id"
                    and {item.from_table, item.to_table} == {line_name, order_name}
                ]
                validated = [
                    item for item in matching
                    if item.status == "validated" and (
                        (
                            item.from_table == line_name
                            and item.to_table == order_name
                            and item.cardinality in {"many_to_one", "one_to_one"}
                        )
                        or (
                            item.from_table == order_name
                            and item.to_table == line_name
                            and item.cardinality in {"one_to_many", "one_to_one"}
                        )
                    )
                ]
                invalid = [
                    item for item in matching
                    if item.status in {"rejected", "ambiguous"}
                    or (item.status == "validated" and item not in validated)
                ]
                if len(validated) == 1 and not invalid:
                    pass
                elif invalid:
                    rejected_relationships.extend(invalid)
                elif len(validated) > 1:
                    unverified_capabilities.append("revenue_executor_source_shape")
                else:
                    missing_relationships.append(
                        RequiredRelationship("order_id", "many_to_one")
                    )

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

        unverified_capabilities = list(dict.fromkeys(unverified_capabilities))
        rejected_capabilities = list(dict.fromkeys(rejected_capabilities))
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
        if scope_mismatch:
            reasons.append("business_rule_scope_mismatch")
        if rejected_capabilities:
            reasons.append("business_rule_capabilities_rejected")
        if unverified_capabilities:
            reasons.append("business_rule_capabilities_unverified")

        return BundleCapabilityResolution(
            bundle_id=bundle.bundle_id,
            status="available" if not reasons else "unavailable",
            missing_fields=tuple(sorted(set(missing_fields))),
            ambiguous_fields=tuple(sorted(set(ambiguous_fields))),
            field_group_conflicts=tuple(field_group_conflicts),
            missing_relationships=tuple(missing_relationships),
            rejected_relationships=tuple(rejected_relationships),
            unverified_capabilities=tuple(unverified_capabilities),
            rejected_capabilities=tuple(rejected_capabilities),
            rule_profile_version=profile_version,
            reasons=tuple(dict.fromkeys(reasons)),
        )

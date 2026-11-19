"""Fail-closed validation of bundle requirements against a business schema.

Schema presence is not proof of business-rule semantics. In particular, a
column named "payment_status" does not establish which values mean settled.
"""
from dataclasses import dataclass

from .bundles import BundleDefinition


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
            "reasons": list(self.reasons),
        }


class BundleCapabilityResolver:
    """Check canonical fields and validated relationship evidence.

    A bundle's required fields must be present together in at least one table.
    This prevents a bundle from passing merely because unrelated tables happen
    to contain different pieces of its required schema.
    """

    def resolve(self, bundle: BundleDefinition, schema_catalog):
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

        # These labels describe business-rule evidence (e.g. settled-status
        # semantics), which a structural schema catalog cannot establish.
        unverified = tuple(bundle.required_capabilities)
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
        if unverified:
            reasons.append("business_rule_capabilities_unverified")

        return BundleCapabilityResolution(
            bundle_id=bundle.bundle_id,
            status="available" if not reasons else "unavailable",
            missing_fields=tuple(sorted(missing_fields)),
            ambiguous_fields=tuple(sorted(ambiguous_fields)),
            field_group_conflicts=tuple(field_group_conflicts),
            missing_relationships=tuple(missing_relationships),
            rejected_relationships=tuple(rejected_relationships),
            unverified_capabilities=unverified,
            reasons=tuple(reasons),
        )

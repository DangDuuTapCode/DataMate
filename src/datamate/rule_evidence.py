"""Versioned, provenance-backed business-rule evidence contracts.

Evidence is supplied by a reviewed rulebook/data dictionary/attestation. It is
never inferred from column names or sample values.
"""
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import re


SCHEMA_VERSION = "1.0.0"
_PROFILE_CAPABILITIES = {
    "revenue_rules": {
        "revenue_executor_source_shape": {
            "direct_line",
            "detail_to_order",
            "direct_line_or_detail_to_order",
        },
        "eligible_sales_amount": {"line_amount_after_line_discount"},
        "sale_period": {"order_date", "delivery_date", "sales_date"},
        "order_status_semantics": {"exclude_cancelled_returned_failed"},
    },
    "collection_rules": {
        "payment_source_role": {"payment_event_or_receipt"},
        "settled_payment_status_policy": {"successful_status_only"},
    },
}
_SOURCE_TYPES = {"rulebook", "data_dictionary", "operator_attestation"}
_STATUSES = {"verified", "unverified", "rejected"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class RuleEvidenceError(ValueError):
    """The business-rule evidence payload is malformed or unsupported."""


@dataclass(frozen=True)
class EvidenceTable:
    table_name: str
    source: str

    def to_dict(self):
        return {"table_name": self.table_name, "source": self.source}


@dataclass(frozen=True)
class EvidenceProvenance:
    source_type: str
    reference: str
    sha256: str
    reviewed_by: str
    reviewed_at: str

    def to_dict(self):
        return {
            "source_type": self.source_type,
            "reference": self.reference,
            "sha256": self.sha256,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
        }


@dataclass(frozen=True)
class CapabilityEvidence:
    capability_id: str
    status: str
    assertion: str | None
    table_scope: tuple[EvidenceTable, ...]
    provenance: EvidenceProvenance

    def to_dict(self):
        return {
            "capability_id": self.capability_id,
            "status": self.status,
            "assertion": self.assertion,
            "table_scope": [item.to_dict() for item in self.table_scope],
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True)
class RuleProfileEvidence:
    profile_id: str
    version: str
    evidence: tuple[CapabilityEvidence, ...]

    def to_dict(self):
        return {
            "profile_id": self.profile_id,
            "version": self.version,
            "evidence": [item.to_dict() for item in self.evidence],
        }

    def verified_capabilities(self, schema_catalog):
        """Return verified claims only when every scoped table exists exactly."""
        if schema_catalog is None:
            return frozenset()
        known = {
            (item.table_name, item.source)
            for item in schema_catalog.table_schemas
        }
        return frozenset(
            item.capability_id
            for item in self.evidence
            if item.status == "verified"
            and all(
                (table.table_name, table.source) in known
                for table in item.table_scope
            )
        )


@dataclass(frozen=True)
class BusinessRuleEvidence:
    business_id: str
    profiles: tuple[RuleProfileEvidence, ...]
    schema_version: str = SCHEMA_VERSION

    def profile(self, profile_id):
        matches = [item for item in self.profiles if item.profile_id == profile_id]
        return matches[0] if len(matches) == 1 else None

    def verified_capabilities(self, profile_id, schema_catalog):
        profile = self.profile(profile_id)
        if profile is None or schema_catalog is None:
            return frozenset()
        if schema_catalog.business_id != self.business_id:
            return frozenset()
        return profile.verified_capabilities(schema_catalog)

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "business_id": self.business_id,
            "profiles": [item.to_dict() for item in self.profiles],
        }

    @classmethod
    def from_dict(cls, payload, *, expected_business_id=None):
        error = validate_business_rule_evidence_payload(
            payload, expected_business_id=expected_business_id
        )
        if error:
            raise RuleEvidenceError(error)

        profiles = []
        for profile in payload["profiles"]:
            records = []
            for item in profile["evidence"]:
                provenance = EvidenceProvenance(**item["provenance"])
                records.append(CapabilityEvidence(
                    capability_id=item["capability_id"],
                    status=item["status"],
                    assertion=item["assertion"],
                    table_scope=tuple(EvidenceTable(**table) for table in item["table_scope"]),
                    provenance=provenance,
                ))
            profiles.append(RuleProfileEvidence(
                profile_id=profile["profile_id"],
                version=profile["version"],
                evidence=tuple(records),
            ))
        return cls(
            business_id=payload["business_id"],
            profiles=tuple(profiles),
            schema_version=payload["schema_version"],
        )

    @classmethod
    def read(cls, path, *, expected_business_id=None):
        path = Path(path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise RuleEvidenceError(f"cannot read business-rule evidence: {path.name}") from error
        return cls.from_dict(payload, expected_business_id=expected_business_id)


def validate_business_rule_evidence_payload(payload, *, expected_business_id=None):
    """Return an error string or None; strict stdlib validation, no dependencies."""
    if not isinstance(payload, dict):
        return "payload must be an object"
    if set(payload) != {"schema_version", "business_id", "profiles"}:
        return "payload must contain only schema_version, business_id, and profiles"
    if payload["schema_version"] != SCHEMA_VERSION:
        return "unsupported business-rule evidence schema_version"
    business_id = payload["business_id"]
    if not isinstance(business_id, str) or not business_id.strip():
        return "business_id must be a non-empty string"
    if expected_business_id is not None and business_id != expected_business_id:
        return "business_id does not match the requested business"
    profiles = payload["profiles"]
    if not isinstance(profiles, list):
        return "profiles must be an array"

    seen_profiles = set()
    for profile in profiles:
        if not isinstance(profile, dict) or set(profile) != {"profile_id", "version", "evidence"}:
            return "each profile must contain only profile_id, version, and evidence"
        profile_id, version, evidence = profile["profile_id"], profile["version"], profile["evidence"]
        if not isinstance(profile_id, str) or profile_id not in _PROFILE_CAPABILITIES:
            return f"unsupported rule profile: {profile_id}"
        if profile_id in seen_profiles:
            return f"duplicate rule profile: {profile_id}"
        seen_profiles.add(profile_id)
        if not isinstance(version, str) or not version.strip():
            return f"profile {profile_id} requires a non-empty version"
        if not isinstance(evidence, list):
            return f"profile {profile_id} evidence must be an array"

        seen_capabilities = set()
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {
                "capability_id", "status", "assertion", "table_scope", "provenance"
            }:
                return f"profile {profile_id} contains a malformed evidence record"
            capability = item["capability_id"]
            if not isinstance(capability, str) or capability not in _PROFILE_CAPABILITIES[profile_id]:
                return f"unsupported capability {capability!r} in profile {profile_id}"
            if capability in seen_capabilities:
                return f"duplicate capability evidence: {capability}"
            seen_capabilities.add(capability)
            status, assertion = item["status"], item["assertion"]
            if not isinstance(status, str) or status not in _STATUSES:
                return f"unsupported evidence status for {capability}"
            allowed_assertions = _PROFILE_CAPABILITIES[profile_id][capability]
            if status == "verified" and (
                not isinstance(assertion, str) or assertion not in allowed_assertions
            ):
                return f"verified capability {capability} requires a supported assertion"
            if assertion is not None and (
                not isinstance(assertion, str) or assertion not in allowed_assertions
            ):
                return f"unsupported assertion for capability {capability}"

            scope = item["table_scope"]
            if not isinstance(scope, list) or not scope:
                return f"capability {capability} requires a non-empty table_scope"
            seen_tables = set()
            for table in scope:
                if not isinstance(table, dict) or set(table) != {"table_name", "source"}:
                    return f"capability {capability} has malformed table scope"
                name, source = table["table_name"], table["source"]
                if not isinstance(name, str) or not name.strip() or not isinstance(source, str) or not source.strip():
                    return f"capability {capability} table scope must identify table_name and source"
                key = (name, source)
                if key in seen_tables:
                    return f"capability {capability} has duplicate table scope"
                seen_tables.add(key)

            provenance = item["provenance"]
            if not isinstance(provenance, dict) or set(provenance) != {
                "source_type", "reference", "sha256", "reviewed_by", "reviewed_at"
            }:
                return f"capability {capability} requires complete provenance"
            if not isinstance(provenance["source_type"], str) or provenance["source_type"] not in _SOURCE_TYPES:
                return f"unsupported provenance source_type for {capability}"
            for field in ("reference", "reviewed_by", "reviewed_at"):
                if not isinstance(provenance[field], str) or not provenance[field].strip():
                    return f"provenance {field} is required for {capability}"
            if not isinstance(provenance["sha256"], str) or not _SHA256.fullmatch(provenance["sha256"]):
                return f"provenance sha256 must be a lowercase SHA-256 hex digest for {capability}"
            try:
                reviewed_at = datetime.fromisoformat(provenance["reviewed_at"].replace("Z", "+00:00"))
            except ValueError:
                return f"provenance reviewed_at must be an ISO-8601 timestamp for {capability}"
            if reviewed_at.tzinfo is None:
                return f"provenance reviewed_at must include a timezone for {capability}"

    return None

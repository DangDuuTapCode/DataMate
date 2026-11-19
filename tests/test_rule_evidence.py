import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from datamate.rule_evidence import (
    BusinessRuleEvidence,
    RuleEvidenceError,
    validate_business_rule_evidence_payload,
    verify_business_rule_evidence_provenance,
)
from datamate.schema_catalog import build_schema_catalog
from datamate.types import Table


def _record(capability, assertion, *, status="verified", table_name="payments", source="payments.xlsx"):
    return {
        "capability_id": capability,
        "status": status,
        "assertion": assertion,
        "table_scope": [{"table_name": table_name, "source": source}],
        "provenance": {
            "source_type": "rulebook",
            "reference": "rulebook.md#collection-policy",
            "sha256": hashlib.sha256(b"reviewed-rulebook-fixture").hexdigest(),
            "reviewed_by": "synthetic-reviewer",
            "reviewed_at": "2026-11-19T10:00:00+07:00",
        },
    }


def _payload():
    return {
        "schema_version": "1.0.0",
        "business_id": "biz-1",
        "profiles": [{
            "profile_id": "collection_rules",
            "version": "1.2.0",
            "evidence": [
                _record("payment_source_role", "payment_event_or_receipt"),
                _record("settled_payment_status_policy", "successful_status_only"),
            ],
        }],
    }


class BusinessRuleEvidenceTests(unittest.TestCase):
    def test_round_trip_preserves_versioned_provenance(self):
        evidence = BusinessRuleEvidence.from_dict(_payload(), expected_business_id="biz-1")
        self.assertEqual(evidence.to_dict(), _payload())
        self.assertEqual(evidence.profile("collection_rules").version, "1.2.0")

    def test_verified_capabilities_require_exact_scoped_tables(self):
        evidence = BusinessRuleEvidence.from_dict(_payload())
        matching = build_schema_catalog([
            Table("payments", ["Ngày thu"], [["2026-01-01"]], "payments.xlsx"),
        ], business_id="biz-1")
        wrong_source = build_schema_catalog([
            Table("payments", ["Ngày thu"], [["2026-01-01"]], "other.xlsx"),
        ], business_id="biz-1")
        wrong_business = build_schema_catalog([
            Table("payments", ["Ngày thu"], [["2026-01-01"]], "payments.xlsx"),
        ], business_id="biz-2")

        self.assertEqual(
            evidence.verified_capabilities("collection_rules", matching),
            frozenset({"payment_source_role", "settled_payment_status_policy"}),
        )
        self.assertEqual(evidence.verified_capabilities("collection_rules", wrong_source), frozenset())
        self.assertEqual(evidence.verified_capabilities("collection_rules", wrong_business), frozenset())

    def test_unverified_and_rejected_claims_never_count_as_verified(self):
        payload = _payload()
        payload["profiles"][0]["evidence"][0]["status"] = "unverified"
        payload["profiles"][0]["evidence"][0]["assertion"] = None
        payload["profiles"][0]["evidence"][1]["status"] = "rejected"
        payload["profiles"][0]["evidence"][1]["assertion"] = None
        evidence = BusinessRuleEvidence.from_dict(payload)
        catalog = build_schema_catalog([
            Table("payments", ["Ngày thu"], [["2026-01-01"]], "payments.xlsx"),
        ], business_id="biz-1")
        self.assertEqual(evidence.verified_capabilities("collection_rules", catalog), frozenset())

    def test_business_id_mismatch_is_rejected(self):
        with self.assertRaisesRegex(RuleEvidenceError, "does not match"):
            BusinessRuleEvidence.from_dict(_payload(), expected_business_id="another-business")

    def test_unknown_capability_and_unsupported_assertion_are_rejected(self):
        payload = _payload()
        payload["profiles"][0]["evidence"][0]["capability_id"] = "payment_status_guess"
        self.assertIn("unsupported capability", validate_business_rule_evidence_payload(payload))

        payload = _payload()
        payload["profiles"][0]["evidence"][0]["assertion"] = "status_means_paid"
        self.assertIn("requires a supported assertion", validate_business_rule_evidence_payload(payload))

    def test_duplicate_profiles_and_capabilities_are_rejected(self):
        payload = _payload()
        payload["profiles"].append(payload["profiles"][0])
        self.assertIn("duplicate rule profile", validate_business_rule_evidence_payload(payload))

        payload = _payload()
        payload["profiles"][0]["evidence"].append(payload["profiles"][0]["evidence"][0])
        self.assertIn("duplicate capability evidence", validate_business_rule_evidence_payload(payload))

    def test_verified_claim_requires_provenance_and_timezone(self):
        payload = _payload()
        payload["profiles"][0]["evidence"][0]["provenance"]["sha256"] = "not-a-digest"
        self.assertIn("sha256", validate_business_rule_evidence_payload(payload))

        payload = _payload()
        payload["profiles"][0]["evidence"][0]["provenance"]["reviewed_at"] = "2026-11-19T10:00:00"
        self.assertIn("timezone", validate_business_rule_evidence_payload(payload))

    def test_provenance_verification_hashes_only_allowlisted_local_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            business_dir = root / "data" / "biz-1"
            business_dir.mkdir(parents=True)
            rulebook = root / "rulebook.md"
            rulebook.write_bytes(b"reviewed rulebook bytes")
            payload = _payload()
            digest = hashlib.sha256(rulebook.read_bytes()).hexdigest()
            for claim in payload["profiles"][0]["evidence"]:
                claim["provenance"]["sha256"] = digest
            evidence = BusinessRuleEvidence.from_dict(payload)
            self.assertTrue(
                verify_business_rule_evidence_provenance(evidence, root, business_dir)
            )

    def test_provenance_verification_rejects_digest_mismatch_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            business_dir = root / "data" / "biz-1"
            business_dir.mkdir(parents=True)
            (root / "rulebook.md").write_bytes(b"actual bytes")
            evidence = BusinessRuleEvidence.from_dict(_payload())
            with self.assertRaisesRegex(RuleEvidenceError, "SHA-256 mismatch"):
                verify_business_rule_evidence_provenance(evidence, root, business_dir)

            payload = _payload()
            payload["profiles"][0]["evidence"][0]["provenance"]["reference"] = "../rulebook.md#section"
            unsafe = BusinessRuleEvidence.from_dict(payload)
            with self.assertRaisesRegex(RuleEvidenceError, "unsafe provenance"):
                verify_business_rule_evidence_provenance(unsafe, root, business_dir)

    def test_provenance_verification_supports_only_named_business_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            business_dir = root / "data" / "biz-1"
            business_dir.mkdir(parents=True)
            dictionary = business_dir / "data_dictionary.csv"
            attestation = business_dir / "operator_attestation.json"
            dictionary.write_bytes(b"column dictionary")
            attestation.write_bytes(b'{"reviewed": true}')
            payload = _payload()
            first, second = payload["profiles"][0]["evidence"]
            first["provenance"].update({
                "source_type": "data_dictionary",
                "reference": "data_dictionary.csv#payments",
                "sha256": hashlib.sha256(dictionary.read_bytes()).hexdigest(),
            })
            second["provenance"].update({
                "source_type": "operator_attestation",
                "reference": "operator_attestation.json",
                "sha256": hashlib.sha256(attestation.read_bytes()).hexdigest(),
            })
            evidence = BusinessRuleEvidence.from_dict(payload)
            self.assertTrue(
                verify_business_rule_evidence_provenance(evidence, root, business_dir)
            )

    def test_provenance_verification_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "input"
            business_dir = root / "data" / "biz-1"
            business_dir.mkdir(parents=True)
            outside = Path(directory) / "outside.md"
            outside.write_bytes(b"outside the input root")
            (root / "rulebook.md").symlink_to(outside)
            payload = _payload()
            payload["profiles"][0]["evidence"][0]["provenance"]["sha256"] = (
                hashlib.sha256(outside.read_bytes()).hexdigest()
            )
            evidence = BusinessRuleEvidence.from_dict(payload)
            with self.assertRaisesRegex(RuleEvidenceError, "cannot safely verify"):
                verify_business_rule_evidence_provenance(evidence, root, business_dir)

    def test_provenance_verification_rejects_external_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            business_dir = root / "data" / "biz-1"
            business_dir.mkdir(parents=True)
            payload = _payload()
            payload["profiles"][0]["evidence"][0]["provenance"]["reference"] = (
                "https://example.invalid/rulebook.md"
            )
            evidence = BusinessRuleEvidence.from_dict(payload)
            with self.assertRaisesRegex(RuleEvidenceError, "unsafe provenance"):
                verify_business_rule_evidence_provenance(evidence, root, business_dir)

    def test_read_rejects_invalid_json_and_writes_no_implicit_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(RuleEvidenceError):
                BusinessRuleEvidence.read(path)
            path.write_text(json.dumps(_payload()), encoding="utf-8")
            loaded = BusinessRuleEvidence.read(path, expected_business_id="biz-1")
            self.assertEqual(loaded.business_id, "biz-1")


if __name__ == "__main__":
    unittest.main()

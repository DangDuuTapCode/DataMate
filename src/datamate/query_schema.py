"""Versioned QuerySpec payload serialization and Draft 2020-12 subset validation."""
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "query_spec.v1.schema.json"


def load_query_spec_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def query_spec_payload(spec):
    """Convert QuerySpec dataclasses and tuple slots to JSON-native values."""
    payload = asdict(spec)
    for key in ("dimensions", "evidence", "ambiguity_flags"):
        payload[key] = list(payload[key])
    payload["filters"] = [list(item) for item in payload["filters"]]
    return payload


def _matches_type(value, expected):
    types = expected if isinstance(expected, list) else [expected]
    for kind in types:
        if kind == "null" and value is None:
            return True
        if kind == "object" and isinstance(value, dict):
            return True
        if kind == "array" and isinstance(value, list):
            return True
        if kind == "string" and isinstance(value, str):
            return True
        if kind == "boolean" and isinstance(value, bool):
            return True
        if kind == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def _validate(value, schema, path="$", errors=None):
    """Validate the keywords used by the checked-in QuerySpec schema."""
    errors = [] if errors is None else errors
    if "type" in schema and not _matches_type(value, schema["type"]):
        errors.append(f"{path}: expected {schema['type']}")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is outside the allowed set")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: value is above maximum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{path}: expected an ISO calendar date")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: array has too many items")
        if schema.get("uniqueItems") and len(value) != len(set(value)):
            errors.append(f"{path}: array items must be unique")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate(item, schema["items"], f"{path}[{index}]", errors)
    if isinstance(value, dict):
        missing = set(schema.get("required", ())) - set(value)
        for key in sorted(missing):
            errors.append(f"{path}.{key}: required property is missing")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in sorted(set(value) - set(properties)):
                errors.append(f"{path}.{key}: unexpected property")
        for key, child in properties.items():
            if key in value:
                _validate(value[key], child, f"{path}.{key}", errors)
    return errors


def validate_query_spec_payload(payload, schema=None):
    """Return validation errors for the supported Draft 2020-12 schema keywords."""
    return _validate(payload, schema or load_query_spec_schema())

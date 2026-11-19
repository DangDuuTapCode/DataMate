"""Business-level catalog combining table semantics and validated key relationships."""
from dataclasses import dataclass

from .relationships import discover_relationships
from .semantic import map_table_schema


@dataclass(frozen=True)
class BusinessSchemaCatalog:
    business_id: str | None
    table_schemas: tuple
    relationships: tuple
    schema_version: str = "1.1.0"

    def get_table_schema(self, table_name, source=None):
        matches = [
            item for item in self.table_schemas
            if item.table_name == table_name and (source is None or item.source == source)
        ]
        if len(matches) != 1:
            return None
        return matches[0]

    def relationships_for(self, *, canonical_key=None, status=None):
        return tuple(
            item for item in self.relationships
            if (canonical_key is None or item.canonical_key == canonical_key)
            and (status is None or item.status == status)
        )

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "business_id": self.business_id,
            "tables": [item.to_dict() for item in self.table_schemas],
            "relationships": [item.to_dict() for item in self.relationships],
        }


def build_schema_catalog(
    tables, *, business_id=None, deduplicate_identical_order_lines=False
):
    """Build deterministic schema metadata without changing or joining tables."""
    tables = tuple(tables)
    table_schemas = tuple(map_table_schema(table) for table in tables)
    relationships = tuple(discover_relationships(
        tables,
        deduplicate_identical_order_lines=deduplicate_identical_order_lines,
    ))
    return BusinessSchemaCatalog(
        business_id=business_id,
        table_schemas=table_schemas,
        relationships=relationships,
    )

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Question:
    id: str
    business_id: str
    question: str
    as_of_date: str


@dataclass(frozen=True)
class SourceLocation:
    """Stable origin information for a table row or parsed cell."""

    source: str
    table: str | None = None
    row: int | None = None
    column: str | None = None


@dataclass
class Table:
    name: str
    headers: list[str]
    rows: list[list]
    source: str = ""
    row_locations: list[SourceLocation] = field(default_factory=list)
    date_system: str | None = None
    issues: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QueryPlan:
    intent: str
    start: str
    end: str
    confidence: float
    entity: str | None = None
    top_k: int = 1
    evidence: tuple[str, ...] = field(default_factory=tuple)

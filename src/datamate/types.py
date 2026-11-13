from dataclasses import dataclass, field


@dataclass(frozen=True)
class Question:
    id: str
    business_id: str
    question: str
    as_of_date: str


@dataclass
class Table:
    name: str
    headers: list[str]
    rows: list[list]
    source: str = ""


@dataclass(frozen=True)
class QueryPlan:
    intent: str
    start: str
    end: str
    confidence: float
    entity: str | None = None
    top_k: int = 1
    evidence: tuple[str, ...] = field(default_factory=tuple)

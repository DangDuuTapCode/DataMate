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
class IngestionStats:
    """Reconciliation counters for non-header source records."""

    source_records: int = 0
    accepted_rows: int = 0
    rejected_rows: int = 0
    skipped_rows: int = 0
    header_rows: int = 0
    blank_rows_skipped: int = 0
    preamble_rows_skipped: int = 0
    repeated_header_rows_skipped: int = 0
    scan_complete: bool = True

    @property
    def reconciled(self):
        return (
            self.scan_complete
            and self.source_records == self.accepted_rows + self.rejected_rows + self.skipped_rows
        )


@dataclass
class Table:
    name: str
    headers: list[str]
    rows: list[list]
    source: str = ""
    row_locations: list[SourceLocation] = field(default_factory=list)
    date_system: str | None = None
    issues: list[str] = field(default_factory=list)
    ingestion_stats: IngestionStats = field(default_factory=IngestionStats)


@dataclass(frozen=True)
class QueryPlan:
    intent: str
    start: str
    end: str
    confidence: float
    entity: str | None = None
    top_k: int = 1
    evidence: tuple[str, ...] = field(default_factory=tuple)
    compare_start: str | None = None
    compare_end: str | None = None
    threshold: str | None = None


@dataclass(frozen=True)
class TemporalScope:
    """Time meaning extracted from a question, without guessing missing dates."""

    kind: str
    start: str | None = None
    end: str | None = None
    as_of: str | None = None
    comparison_start: str | None = None
    comparison_end: str | None = None


@dataclass(frozen=True)
class SortSpec:
    field: str
    direction: str


@dataclass(frozen=True)
class QuerySpec:
    """Normalized question intent and evidence, including unsupported work.

    `QuerySpec` records what the planner understood even when the executor
    cannot safely answer it yet. `QueryPlan` remains the allowlisted executable
    subset used by the current engine.
    """

    intent: str
    time: TemporalScope | None
    confidence: float
    entity: str | None = None
    top_k: int = 1
    dimensions: tuple[str, ...] = field(default_factory=tuple)
    filters: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    executable: bool = False
    schema_version: str = "1.0.0"
    raw_question: str = ""
    business_id: str | None = None
    metric: str | None = None
    unit: str | None = None
    sort: SortSpec | None = None
    ambiguity_flags: tuple[str, ...] = field(default_factory=tuple)
    unsupported_reason: str | None = None

"""Render the business-level matrix from the train-only profile JSON."""
import argparse
import json
from pathlib import Path


def render(profile_path):
    report = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    businesses = report["businesses"]
    rows = [
        "# Train Business Profile and Coverage Matrix",
        "",
        "This is structural profile coverage (L1), not proof that any business/intent is release-supported.",
        "Question intent figures are rule-parser coverage diagnostics, not reviewed accuracy. No answer labels or public-test content are used.",
        "",
        f"- Businesses profiled: {sum(bool(b['readme_present']) for b in businesses)}/{len(businesses)}",
        f"- Structured files: {sum(len(b['files']) for b in businesses)}; tables/sheets: {sum(len(b['tables']) for b in businesses)}",
        f"- Rows from prior full ingestion census: {sum((b.get('ingestion_census') or {}).get('rows', 0) for b in businesses):,}",
        f"- Questions profiled: {sum((b.get('question_diagnostics') or {}).get('question_count', 0) for b in businesses):,}",
        "",
        "| Business | Formats | Files | Tables/sheets | Ingested rows | Questions | Intent coverage | Profile level |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for business in businesses:
        formats = ", ".join(sorted({f".{f['kind']}" for f in business["files"]})) or "none"
        census = business.get("ingestion_census") or {}
        questions = business.get("question_diagnostics") or {}
        q_count = questions.get("question_count", 0)
        coverage = questions.get("interpreted", 0) / q_count if q_count else 0
        rows.append(
            f"| {business['business_id']} | {formats} | {len(business['files'])} | {len(business['tables'])} "
            f"| {census.get('rows', 0):,} | {q_count} | {coverage:.1%} | L1 structural |"
        )
    rows.extend([
        "",
        "## README caveats for later operator work",
        "",
        "- `biz_107`, `biz_113`, and `biz_126` are handwritten sales books without invoice IDs or customer names; invoice/customer metrics cannot be inferred from rows.",
        "- `biz_110` contains invoice-level rows only and has no product-line detail; product quantity/ranking must abstain.",
        "- `biz_102`–`biz_104`, `biz_112`, `biz_115`–`biz_116`, `biz_118`, and `biz_130` include sales details without a stable product code; some joins rely on product name and require an explicit uniqueness check.",
        "- `biz_105` and `biz_117` encode returns as negative quantities on the original invoice; revenue and quantity rules must preserve that sign and cancellation semantics.",
        "- `biz_119`–`biz_122` and `biz_123`–`biz_124` contain lot/expiry or medication metadata. Lot-level sales may span multiple lots, and returned goods go back to the sold lot.",
        "- `biz_115`, `biz_116`, and `biz_118` contain delivery ledgers with 1–3 delivery rounds; only qualifying non-cancelled building-material orders are delivered, and latest orders may not yet appear.",
        "- `biz_123` is SQLite with stock-movement history; as-of inventory must use the last product movement at or before the requested date.",
        "- `biz_124` combines POS exports, handwritten purchase/expense ledgers, and inventory CSV; the sources require separate declared joins.",
        "- `biz_125`–`biz_130` have restaurant service-fee lines for eligible cold-room dining orders; do not count them as merchandise quantity.",
        "- Many README conversion factors are product-specific; unit conversion must not be generalized from a shared unit name.",
        "",
        "## Interpretation",
        "",
        "The matrix establishes L1 structural profiling only. Higher business levels (ingestion tests, intent-specific golden tests, replay evaluation, release support) are not implied. Candidate joins in the JSON profile are header-name matches only and are not approved execution keys.",
    ])
    return "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile_json")
    parser.add_argument("output_markdown")
    args = parser.parse_args()
    Path(args.output_markdown).write_text(render(args.profile_json), encoding="utf-8")
    print(f"wrote {args.output_markdown}")


if __name__ == "__main__":
    main()

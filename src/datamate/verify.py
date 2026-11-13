"""Verification firewall: only exact schema-safe, evidenced values pass."""
from .output import valid_record


def verify(question_id, candidate, plan):
    if candidate is None or not candidate.get("evidence") or plan.confidence < 0.5:
        return {"id": question_id, "type": "abstain"}
    record = {"id": question_id, "type": candidate["type"], "answer": candidate["answer"]}
    return record if valid_record(record) else {"id": question_id, "type": "abstain"}

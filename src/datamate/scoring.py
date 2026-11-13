"""Reference-style local scorer for labelled training data only."""
import math
import re
import unicodedata
from collections import Counter

from .normalise import fold


def _display_key(value):
    # Evaluation ignores case, spaces and punctuation, but Vietnamese diacritics
    # remain significant.
    value = unicodedata.normalize("NFC", value).lower()
    return re.sub(r"[^\w]", "", value, flags=re.UNICODE)


def _same_value(left, right):
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        return math.isclose(left, right, rel_tol=0, abs_tol=1e-9)
    if isinstance(left, str) and isinstance(right, str):
        return _display_key(left) == _display_key(right)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_same_value(a, b) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        if left.get("columns") != right.get("columns"):
            return False
        # Rulebook: row order does not affect table scoring.
        unmatched = list(right.get("rows", []))
        for row in left.get("rows", []):
            for index, candidate in enumerate(unmatched):
                if _same_value(row, candidate):
                    unmatched.pop(index)
                    break
            else:
                return False
        return not unmatched
    return left == right


def correct(prediction, reference):
    if prediction.get("type") != reference.get("type"):
        return False
    if prediction["type"] in ("abstain", "unanswerable"):
        return prediction["type"] == reference["type"]
    return _same_value(prediction.get("answer"), reference.get("answer"))


def penalized_accuracy(predictions, references):
    truth = {row["id"]: row for row in references}
    guessed = {row["id"]: row for row in predictions}
    correct_count = wrong = abstain = 0
    for ident, reference in truth.items():
        item = guessed.get(ident, {"id": ident, "type": "abstain"})
        if item.get("type") == "abstain":
            abstain += 1
        elif correct(item, reference):
            correct_count += 1
        else:
            wrong += 1
    return {"questions": len(truth), "correct": correct_count, "wrong": wrong, "abstain": abstain,
            "penalized_accuracy": (correct_count - wrong) / len(truth) if truth else 0.0}

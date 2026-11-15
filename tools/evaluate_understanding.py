"""Measure question-understanding coverage using train questions only.

This utility intentionally reads no answer file and no public-test data.
It reports rule coverage, intent/time counts, and a deterministic small sample
for human review; coverage is not an answer-accuracy metric.
"""
import collections
import argparse
import json
import random
import sys
from pathlib import Path

from datamate.query_schema import query_spec_payload, validate_query_spec_payload
from datamate.understanding import RulePlanner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="print two question-only examples per intent")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path("data/train/questions.jsonl")
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    planner = RulePlanner()
    evaluated = [
        (row, planner.interpret(row["question"], row["as_of_date"], row["business_id"]))
        for row in rows
    ]
    interpreted = [(row, spec) for row, spec in evaluated if spec is not None]
    intent_counts = collections.Counter(spec.intent for _, spec in interpreted)
    time_counts = collections.Counter(spec.time.kind for _, spec in interpreted if spec.time)
    executable = sum(bool(spec and spec.executable) for _, spec in evaluated)
    schema_errors = [
        validate_query_spec_payload(query_spec_payload(spec))
        for _, spec in interpreted
    ]
    schema_valid = sum(not errors for errors in schema_errors)

    print(f"source={path.as_posix()} questions={len(rows)}")
    print(f"interpreted={len(interpreted)} coverage={len(interpreted) / len(rows):.4%}")
    print(f"executable={executable} coverage={executable / len(rows):.4%}")
    print(f"schema_valid={schema_valid}/{len(interpreted)} rate={schema_valid / len(interpreted) if interpreted else 0:.4%}")
    print(f"schema_invalid={len(interpreted) - schema_valid}")
    print("time_scopes=" + json.dumps(dict(sorted(time_counts.items())), ensure_ascii=False))
    print("intents=" + json.dumps(dict(intent_counts.most_common()), ensure_ascii=False))

    if args.sample:
        rng = random.Random(20261115)
        by_intent = collections.defaultdict(list)
        for row, spec in interpreted:
            by_intent[spec.intent].append((row, spec))
        print("stratified_question_sample_seed=20261115 sample_per_intent=2")
        for intent in sorted(by_intent):
            candidates = by_intent[intent]
            for row, spec in rng.sample(candidates, min(2, len(candidates))):
                print(f"[{intent}] {row['question']} | time={spec.time.kind} | executable={spec.executable}")


if __name__ == "__main__":
    main()

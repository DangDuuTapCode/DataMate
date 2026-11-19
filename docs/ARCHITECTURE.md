# Architecture

## Inference flow

1. ingest.py loads the question list and business tables from the supplied input tree.
2. normalization.py and timeparse.py standardize values and interpret supported dates.
3. understanding.py converts Vietnamese wording into a constrained query representation.
4. query_schema.py validates the representation; deterministic rules select supported operations.
5. metrics.py, scoring.py, and related execution helpers compute candidate values from the loaded tables.
6. verify.py and abstention logic guard results that lack adequate evidence.
7. output.py serializes answer and per-question trace records. main.py coordinates the command-line run and writes outputs incrementally.

## Determinism and model boundary

The shipped inference path is rule-based Python. It does not call a hosted model or load local model weights. The manifest records zero parameters. The vLLM base image is used because it is the base recommended by the competition Docker guide; it does not mean this implementation performs LLM inference.

## Extension boundary

New query types should be represented in the query schema, parsed into the constrained representation, computed by deterministic code, verified against source rows, and covered by synthetic regression tests. Do not add public/private evaluation examples or answer-specific rules to the runtime.


## Composite query extension

The single-query path remains the compatibility path for supported single-metric questions. Composite questions are routed through `datamate.composite.CompositePlanner` before the single-plan compiler.

The first supported composite is a same-period, side-by-side comparison of `revenue` and `collected_amount`. Each component receives its own `QuerySpec` and `QueryPlan`, shares the resolved period and entity context, and reuses the existing metric-specific executor. The composite verifier checks every component and abstains on the complete question if any required component fails.

Arithmetic differences, cross-period comparisons, arbitrary conjunction splitting, and dynamic bundle discovery remain unsupported in this first slice. See `docs/DATA_INGESTION.md` and `docs/MULTI_BUNDLE_QUERY.md`.

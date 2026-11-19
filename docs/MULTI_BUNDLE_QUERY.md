# DataMate — Multi-Bundle Query Processing

## Goal

Allow one natural-language question to contain multiple independently resolved requirements.

```text
Question
  -> Requirement Extraction
  -> Requirement Resolution
  -> Bundle Resolution
  -> Composite Plan
  -> Component Execution
  -> Component Verification
  -> Composite Verification
  -> Answer
```

## Terminology

- **Requirement:** one operation needed to answer a question, with metric, time, entity, filters, dimensions, expected type, and resolution status.
- **Facet:** one aspect of a requirement, such as metric, time, entity, filter, dimension, comparison, or aggregation.
- **Bundle:** a logical query capability containing tables, semantic mappings, relationships, metric definitions, business rules, and provenance. It is not synonymous with a file or table.
- **Composite plan:** multiple component plans plus shared context.

## First vertical slice

The first supported composite is “Doanh thu và tiền thực thu tháng này”.

| Requirement | Metric | Bundle |
|---|---|---|
| R1 | `revenue` | `revenue` |
| R2 | `collected_amount` | `collection` |

Both components share the same resolved period and entity context. They retain separate metric-specific calculation rules.

## Current implementation boundary

`src/datamate/composite.py` contains:

- `CompositePlanner`, which accepts the existing `financial_metric_comparison` intent.
- Requirement, component, and composite-plan data structures.
- Explicit-period and unresolved-entity checks.
- Two ordinary `QuerySpec`/`QueryPlan` component pairs.
- Side-by-side output only.

The main pipeline routes this composite before the ordinary single-plan path. Other supported single intents retain the existing execution path.

## Execution and verification

Each component reuses `Executor.execute_with_reason`. Each candidate is passed through `verify_with_reason`. The composite verifier checks component count, expected numeric type, evidence, and final table shape.

**All-or-nothing:** if one required component fails execution or verification, the complete answer abstains. The engine must not silently return only the successful component.

## Output contract

```json
{
  "id": "question-id",
  "type": "table",
  "answer": {
    "columns": ["metric", "value"],
    "rows": [
      ["revenue", 15000000],
      ["collected_amount", 12000000]
    ]
  }
}
```

Component candidates, execution reasons, and evidence remain in the trace.

## Deliberate non-goals

- Arbitrary splitting on `and` or `và`.
- Three or more metrics.
- Arithmetic differences or ratios.
- Cross-period comparisons.
- Dynamic bundle discovery.
- Partial answers when a required component fails.
- Joins based only on similar column names.

## Next stages

1. Add a versioned composite query-spec schema.
2. Generalize requirement extraction beyond the fixed financial pair.
3. Add a bundle registry with declared inputs, rules, and supported metrics.
4. Add relationship resolution and safe shared-data reuse.
5. Add dependency-aware plan composition.
6. Add derived metrics only after all inputs are verified.
7. Add synthetic regression fixtures.
8. Evaluate against permitted training data only; do not tune against protected public-test labels.

## Regression requirements

Test component ordering, shared context, unchanged single-metric behavior, implicit time abstention, unresolved entities, unsupported breakdowns, all-or-nothing failure, evidence preservation, table output schema, and the existing regression suite.


## Relationship evidence before bundle composition

The initial relationship validator lives in `src/datamate/relationships.py`. It requires shared, unambiguous canonical key mappings and exact key-value overlap. It reports cardinality and refuses partial child-key coverage, blank child keys, and many-to-many join risks. It does not execute joins.

This is a prerequisite for future multi-bundle plans, not an authorization to join tables automatically. Metric-specific business rules and query-specific join approval remain mandatory.


## Declarative bundle registry

`src/datamate/bundles.py` now provides an explicit `BundleRegistry` mapping metric IDs to logical bundle IDs, existing executor intents, output types, required capability labels, and rule-profile labels.

The first registry contains only:
- `revenue` → `revenue` bundle → existing `revenue` executor.
- `collected_amount` → `collection` bundle → existing `collected_amount` executor.

`CompositePlanner` resolves the fixed first-slice pair through this registry. Unknown or duplicate requirements fail closed. This is a registry foundation, not yet general multi-intent extraction or dynamic bundle discovery.


### Bundle registry implementation status

The composite planner now resolves its existing revenue/collected-amount pair through `BundleRegistry`. Unknown metrics, duplicate requirements, unsupported output types, or bundle definitions that do not support the shared period/entity context fail closed. This remains a fixed first-slice pair; it is not arbitrary multi-intent parsing.

CI run `44547696247`: 216 tests, 214 passed; the only two failures are the pre-existing repository-hygiene checks against `CODEX PROGRESS`. See https://github.com/pl2n/DataMate/actions/runs/44547696247.


## Schema catalog integration status

The versioned `BusinessSchemaCatalog` now combines exact semantic column mappings with key/cardinality relationship evidence. It keeps table identity source-qualified and serializes all mapping and relationship evidence. This catalog is a metadata layer only; it does not perform joins or make metrics executable.

CI run `44548265235`: 219 tests, 217 passed. The only two failures are pre-existing repository-hygiene checks on `CODEX PROGRESS`.


## Requirement extraction

`src/datamate/requirements.py` separates requirement extraction from plan compilation. The initial allowlisted rule translates the already-recognized `financial_metric_comparison` QuerySpec into two independent requirements: `revenue` and `collected_amount`.

The composite planner consumes these requirements, resolves each through `BundleRegistry`, and creates separate existing executor plans. Single intents and unknown/unresolved requirements do not enter the composite path. Arbitrary conjunction splitting remains explicitly unsupported.


## Requirement extraction status

The requirement model and extraction layer are now separate from composite plan compilation. The first rule remains limited to the parser's existing `financial_metric_comparison` intent. Follow-up CI run `44548881088` executed 222 tests with no code/test errors; 220 passed, while the two pre-existing `CODEX PROGRESS` hygiene assertions remain failing.


## Versioned requirement payload

The output of `RequirementExtractor` is serialized and validated against `schemas/requirement_extraction.v1.schema.json` before plan compilation. The contract enforces typed requirement fields, unique metric IDs and requirement IDs, and consistency between resolved/unresolved status and failure reason. Invalid payloads fail closed.


## Versioned requirement contract status

The composite requirement payload is versioned at `1.0.0` and validated before component planning. CI run `44549585604` executed 226 tests with no code/test errors; 224 passed. Only two pre-existing repository-hygiene checks against `CODEX PROGRESS` remain failing.


## Explicit composite rule registry

`RequirementExtractor` now resolves QuerySpec intents through `CompositeRuleRegistry`. Each rule declares the recognized intent, ordered metric IDs, and comparison type. The default registry contains only the current financial pair. This permits future reviewed combinations without embedding more metric pairs inside the planner, but does not itself add new parser cues or arbitrary text splitting.


## Composite rule registry status

Composite intent-to-metric combinations are now data-driven through an explicit `CompositeRuleRegistry`. The default rule remains the existing revenue + collected-amount pair; a synthetic custom-rule test demonstrates plan composition for another allowlisted metric pair without adding natural-language splitting. CI run `44550215128`: 230 tests, no code/test errors, 228 passed; only the two existing `CODEX PROGRESS` hygiene checks remain failing.


## Shared-context compatibility gate

Before creating component plans, the composite planner now rejects populated filters, non-metric dimensions, sort options, and top-k settings. This prevents the previous component-spec construction from silently clearing a constraint that the user asked for. The parser's internal `metric` dimension marker remains allowed.

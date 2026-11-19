# Fact join contract — structural prototype

## Purpose

The relationship-path resolver can identify one unique path composed only of validated relationships. That is not, by itself, enough to authorize metric execution. A query must also declare its fact table, row grain, measure field and physical column, aggregation stage, and join type.

The new module `src/datamate/join_contracts.py` introduces a structural `FactJoinContract` for that purpose.

## Current validation

The builder accepts only:

- one `RelationshipPathResolution` with status `unique_safe`;
- exact source-qualified fact and target table identities;
- a connected path whose first and last nodes match those identities;
- only many-to-one or one-to-one traversals;
- nonempty canonical join keys with matching key/index tuple lengths;
- nonnegative physical key-column indices;
- no repeated table identity in the path;
- an explicit nonblank fact-grain declaration and measure-field declaration;
- a nonnegative physical measure-column index;
- aggregation stage `after_join`;
- join type `inner` or `left`.

The contract serializes each exact path edge, including source filenames, canonical keys, and endpoint column indices.

## Important limits

This is a structural prototype, not a runtime feature:

- It is not wired into `CompositePlanner`, `BundleCapabilityResolver`, or `Executor`.
- It does not execute joins or change any current query result.
- The declared fact grain and measure semantics are not independently proven by this module. They must come from reviewed query/source evidence.
- The current relationship validator's validated edges require complete key coverage and no blank keys. If those invariants change, the inner/left join preservation assumption must be revisited.
- No one-to-many traversal is accepted. Such a path requires an explicit allocation/aggregation rule and cannot be made safe by merely adding a flag.
- Pre-join aggregation is rejected because the repository has no query-specific proof that it preserves the required measure semantics.

## Regression coverage

Synthetic tests cover a unique two-hop many-to-one chain, exact source/key-index serialization, fan-out rejection, ambiguous path rejection, endpoint mismatch, aggregation-stage rejection, invalid measure indices, unsupported join types, missing declarations, unknown cardinality, and manually constructed cyclic paths.

The next step is to connect this contract to one real, rulebook-backed query family only after its source grain and measure semantics are explicitly established. Do not generalize this prototype into arbitrary JOIN execution.

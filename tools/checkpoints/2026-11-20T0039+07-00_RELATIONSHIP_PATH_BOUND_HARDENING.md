# Relationship path bound hardening — 2026-11-20

## Scope

Harden the discovery-only multi-hop relationship resolver without enabling JOIN execution.

## Findings and changes

The resolver previously marked overflow as soon as it collected exactly `max_candidates` paths. That was an off-by-one error: with a configured limit of one, a graph containing exactly one valid path was incorrectly reported ambiguous. It now collects up to one path beyond the limit, so exactly-at-limit remains eligible for normal unique-path evaluation and actual overflow remains ambiguous.

Request validation now rejects malformed/blank source or target identities and non-positive, boolean, or non-integer hop/candidate limits with `invalid_request`.

## Regression coverage

Six synthetic tests cover:

- exactly one path at `max_candidates=1` remains eligible;
- a second path exceeds the configured bound and fails closed;
- reverse traversal of a one-to-many edge is recognized as fanout;
- `max_hops` is enforced;
- invalid limits fail closed;
- cycles do not revisit a table within one path.

## Commits

- `4212165cece5a9167095984865aca98ae6362890` — resolver hardening.
- `fe799c55ac9757a64007fbe03ef0a9028e6ff1f2` — regression tests.

## Verification and limitations

GitHub Actions verification is pending. No local checkout or local test execution was available. The resolver remains discovery-only and is not connected to the planner or Executor. No arbitrary join, new metric, or capability enablement was introduced.

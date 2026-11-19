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


## Follow-up CI result

The initial edge-case CI run revealed two fixture mistakes, not implementation defects: the reverse traversal test used the forward direction, and the cycle test asserted three hops while its graph included a direct one-hop target edge. Both fixtures were corrected in commit `2522abbafdccb6bb930d3f79f9f0f13af8302d4f`.

GitHub Actions run `44580683573` executed 299 tests: 297 passed, including all relationship-path tests. The only two failures are the inherited `CODEX PROGRESS` hygiene checks. Run: https://github.com/pl2n/DataMate/actions/runs/44580683573

The branch is also the head of existing upstream PR #1 targeting `main`; no PR mutation or merge was performed here. GitHub currently reports `mergeable=false`.

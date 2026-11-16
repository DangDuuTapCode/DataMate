# Verifier and execution reason codes

These codes are internal trace metadata. The submission interface continues to serialize an abstention as `{"id":"…","type":"abstain"}`. A reason code describes why the system withheld an answer; it is not an answer or a confidence score.

| Code | Meaning |
|---|---|
| `unsupported_intent` | The requested operation is outside the executable intent contract. |
| `ambiguous_entity` | A referenced business entity could not be resolved safely. |
| `missing_time_range` | The request requires a time range that could not be established. |
| `missing_column` | The selected source lacks a required field. |
| `parse_failure` | A source file could not be ingested or parsed. |
| `source_unavailable` | A required source file is absent or unavailable. |
| `invalid_unit` | The requested unit cannot be produced by the selected metric. |
| `join_unsafe` | A required relationship cannot be joined without risking incorrect aggregation. |
| `insufficient_evidence` | Evidence is malformed, ambiguous, incomplete, or otherwise insufficient to support a value. |
| `no_data` | A unique supported source has no raw records in the requested period. This is distinct from a valid aggregate of zero. |
| `missing_order_status` | A status-rate calculation has no usable order-status field. |
| `unknown_order_status` | At least one relevant order has an unrecognized status. |
| `conflicting_order_status` | One order has contradictory status classes in the relevant evidence. |
| `verification_failed` | A candidate failed a generic verification or output-contract check. |
| `rulebook_unavailable` | The active split rulebook is missing, unreadable, or lacks a supported rule needed by the current executor. |

## No data versus zero

- Emit `no_data` when a unique, structurally supported source has no raw rows in the requested period.
- Return numeric zero only when matching rows exist, the selected measure is valid, and their aggregate is zero.
- Keep missing columns, unavailable files, malformed dates, ambiguous source selection, and unsafe joins under their specific failure reasons; do not convert them to zero or `no_data`.
- `no_data` is covered by synthetic regression tests. It did not occur in the v11 train replay traces, so that replay provides no real-trace frequency evidence for the new code.

The canonical allowlist is `REASON_CODES` in `src/datamate/verify.py`; structured executor diagnostics originate in `src/datamate/metrics.py`.

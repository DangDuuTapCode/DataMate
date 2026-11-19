# Checkpoint — composite shared-context safety gate (2026-11-19)

## Finding

Component specs are created from one source QuerySpec. Clearing filters/dimensions while building component specs could silently discard a user constraint if an unsupported query reached the composite path.

## Change

- Composite planning rejects any non-empty source filters.
- Only the parser's internal `metric` dimension marker is allowed; all other dimensions fail closed.
- Sort and top-k settings are rejected.
- Existing period, entity, unit, and unsupported-breakdown checks remain.

## Tests

Added synthetic regressions for explicit filters, unsupported dimensions, and ranking options.

## Boundary

This is a compatibility gate only. It does not add filter-aware multi-bundle execution or ranking composites.

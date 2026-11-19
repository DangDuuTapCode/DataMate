# Checkpoint — controlled provenance digest verification (2026-11-19)

## Contract

Every verified business-rule claim must prove that its recorded SHA-256 matches the exact bytes of an allowlisted local source file.

## Runtime allowlist

- source_type `rulebook`: input-root `rulebook.md`
- source_type `data_dictionary`: business-scoped `data_dictionary.csv`, `data_dictionary.xlsx`, or `data_dictionary.md`
- source_type `operator_attestation`: business-scoped `operator_attestation.json`

A reference may include a fragment after `#`; only the basename before the fragment is considered. No external URL or arbitrary path is followed. All resolved paths must remain under the input root, including after symlink resolution.

## Runtime behavior

- `main.run` parses the evidence file, verifies every claim digest, then marks evidence loaded.
- Missing source, unknown filename, traversal, path separators, external URL, symlink escape, or digest mismatch marks evidence invalid and removes it from planning.
- Composite planning remains fail-closed. Ordinary single-metric execution remains available.
- No file contents are fetched from external services.

## Tests

- Valid digest against local rulebook bytes.
- Digest mismatch.
- Path traversal and external URL rejection.
- Allowlisted data dictionary and operator-attestation files.
- Symlink resolving outside the input root.
- Runner-level digest mismatch abstention.

## Verification

CI pending for this checkpoint commit. Previous evidence-scoped execution CI run `44562435501`: 265 tests, 263 passed; only the two inherited `CODEX PROGRESS` hygiene checks failed.

## Next

Inspect CI. Then assess whether the mounted dataset actually uses the current allowlisted filenames. Expand the allowlist only for specific documented source types and exact filenames, never arbitrary reference paths.

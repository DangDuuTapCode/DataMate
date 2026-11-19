# Checkpoint — controlled provenance digest verification (2026-11-19)

## Contract

Every verified business-rule claim must prove that its recorded SHA-256 matches the exact bytes of an allowlisted local source file.

## Runtime allowlist

- source_type `rulebook`: input-root `rulebook.md`
- source_type `data_dictionary`: business-scoped `data_dictionary.csv`, `data_dictionary.xlsx`, or `data_dictionary.md`
- source_type `operator_attestation`: business-scoped `operator_attestation.json`

A reference may include a fragment after `#`; only the basename before the fragment is considered. No external URL or arbitrary path is followed. All resolved paths must remain under the input root, including after path resolution. Symlink source files themselves are rejected.

## Runtime behavior

- `main.run` parses the evidence file, verifies every claim digest, then marks evidence loaded.
- Missing source, unknown filename, traversal, path separators, external URL, any symlink source, or digest mismatch marks evidence invalid and removes it from planning.
- Composite planning remains fail-closed. Ordinary single-metric execution remains available.
- No file contents are fetched from external services.

## Tests

- Valid digest against local rulebook bytes.
- Digest mismatch.
- Path traversal and external URL rejection.
- Allowlisted data dictionary and operator-attestation files.
- Internal and external symlink source rejection.
- Runner-level digest mismatch abstention.

## Verification

GitHub Actions run `44563864531` on commit `bcada84044c4d38bc144d8eaa27099bdd148feeb` executed 272 tests; 270 passed. All feature tests passed, including digest, path-safety, and internal/external symlink checks. The only two failures are inherited `CODEX PROGRESS` hygiene checks.

Run: https://github.com/pl2n/DataMate/actions/runs/44563864531

## Next

Inspect CI. Then assess whether the mounted dataset actually uses the current allowlisted filenames. Expand the allowlist only for specific documented source types and exact filenames, never arbitrary reference paths.

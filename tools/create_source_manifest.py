"""Create reproducible SHA-256 provenance files for a source release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--base-commit",
        default="24cfa0908bd20f6e5b210366e956cae0d665b56e",
    )
    parser.add_argument("--base-branch", default="feature/offline-core")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"source root does not exist: {root}")

    excluded = {"source_manifest.json", "SHA256SUMS.txt"}
    paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name not in excluded
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )
    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    ]
    tree_input = "".join(f"{item['path']}\0{item['sha256']}\n" for item in entries)
    tree_sha = hashlib.sha256(tree_input.encode("utf-8")).hexdigest()
    model_manifest = json.loads(
        (root / "models" / "manifest.json").read_text(encoding="utf-8")
    )
    manifest = {
        "schema_version": 1,
        "repository": "https://github.com/DangDuuTapCode/DataMate",
        "base_branch": args.base_branch,
        "base_commit": args.base_commit,
        "release_git_commit": None,
        "release_git_commit_note": "No release commit was created; this is an isolated source package.",
        "source_tree_sha256": tree_sha,
        "file_count": len(entries),
        "files": entries,
        "model_declaration": model_manifest,
        "training_performed": False,
        "competition_datasets_in_source_package": False,
    }
    manifest_path = root / "source_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    checksum_lines = [
        f"{sha256_file(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.name != "SHA256SUMS.txt"
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]
    (root / "SHA256SUMS.txt").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Source files recorded: {len(entries)}")
    print(f"Source tree SHA-256: {tree_sha}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

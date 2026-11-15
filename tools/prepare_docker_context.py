"""Prepare a clean Docker context from source plus the official train.zip."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--train-archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    train_archive = args.train_archive.resolve()
    output = args.output.resolve()
    if not source.is_dir():
        parser.error(f"source directory does not exist: {source}")
    if not train_archive.is_file():
        parser.error(f"training archive does not exist: {train_archive}")
    try:
        output.relative_to(source)
    except ValueError:
        pass
    else:
        parser.error("output must be outside the source directory")
    if output.exists():
        parser.error(f"refusing to overwrite existing output: {output}")

    data_manifest_path = source / "training_code" / "data_manifest.json"
    source_manifest_path = source / "source_manifest.json"
    model_manifest_path = source / "models" / "manifest.json"
    for required in (data_manifest_path, source_manifest_path, model_manifest_path):
        if not required.is_file():
            parser.error(f"required release manifest is missing: {required.relative_to(source)}")

    data_manifest = json.loads(data_manifest_path.read_text(encoding="utf-8"))
    expected_sha = data_manifest.get("archive_sha256")
    actual_sha = sha256_file(train_archive)
    if not expected_sha or actual_sha != expected_sha:
        parser.error("train.zip SHA-256 does not match training_code/data_manifest.json")

    blocked_parts = {"public_test", "private_test"}
    for item in source.rglob("*"):
        if item.is_file() and any(part.lower() in blocked_parts for part in item.relative_to(source).parts):
            parser.error(f"test-split path is not allowed in source release: {item.relative_to(source)}")

    shutil.copytree(
        source,
        output,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    train_target = output / "training_code" / "data" / "train.zip"
    train_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(train_archive, train_target)

    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    files = []
    for path in sorted(p for p in output.rglob("*") if p.is_file() and p.name != "submission_manifest.json"):
        relative = path.relative_to(output).as_posix()
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    manifest = {
        "schema_version": 1,
        "source_base_commit": source_manifest["base_commit"],
        "source_manifest_sha256": sha256_file(source_manifest_path),
        "inference_entrypoint": "/code/predict.sh",
        "inference_declaration": model_manifest,
        "training_performed": False,
        "training_archive": {
            "path": "training_code/data/train.zip",
            "bytes": train_target.stat().st_size,
            "sha256": sha256_file(train_target),
        },
        "public_or_private_test_data_included": False,
        "files": files,
    }
    (output / "submission_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Build context prepared: {output}")
    print(f"Files: {len(files) + 1}; train.zip SHA-256: {actual_sha}")
    print("This is a Docker build context, not a built or tested Docker image.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

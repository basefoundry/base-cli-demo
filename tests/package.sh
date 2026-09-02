#!/usr/bin/env bash
set -euo pipefail

artifact_dir="$(mktemp -d "${TMPDIR:-/tmp}/base-cli-demo-package.XXXXXX")"
trap 'rm -rf "$artifact_dir"' EXIT

python -m build --sdist --wheel --outdir "$artifact_dir" .
python -m twine check "$artifact_dir"/*

wheel_path="$(find "$artifact_dir" -maxdepth 1 -name '*.whl' -print -quit)"
sdist_path="$(find "$artifact_dir" -maxdepth 1 -name '*.tar.gz' -print -quit)"
[[ -n "$wheel_path" ]] || { printf 'Wheel was not built.\n' >&2; exit 1; }
[[ -n "$sdist_path" ]] || { printf 'Source distribution was not built.\n' >&2; exit 1; }

python - "$wheel_path" "$sdist_path" <<'PY'
from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

wheel_path = Path(sys.argv[1])
sdist_path = Path(sys.argv[2])

with zipfile.ZipFile(wheel_path) as wheel:
    wheel_names = set(wheel.namelist())
required_wheel_files = {
    "base_cli_demo/__init__.py",
    "base_cli_demo/cli.py",
    "base_cli_demo/fixtures/services.json",
}
missing_wheel = required_wheel_files - wheel_names
if missing_wheel:
    raise SystemExit(f"Wheel is missing: {sorted(missing_wheel)}")

with tarfile.open(sdist_path, "r:gz") as sdist:
    sdist_names = set(sdist.getnames())
sdist_root = sdist_path.name.removesuffix(".tar.gz")
required_sdist_files = {
    f"{sdist_root}/README.md",
    f"{sdist_root}/pyproject.toml",
    f"{sdist_root}/src/base_cli_demo/cli.py",
    f"{sdist_root}/src/base_cli_demo/fixtures/services.json",
}
missing_sdist = required_sdist_files - sdist_names
if missing_sdist:
    raise SystemExit(f"Source distribution is missing: {sorted(missing_sdist)}")

print(f"Validated {wheel_path.name} and {sdist_path.name}.")
PY

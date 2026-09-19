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

python tests/package_validation.py "$wheel_path" "$sdist_path"

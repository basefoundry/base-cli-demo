#!/usr/bin/env bash
set -euo pipefail

required_files=(
  README.md
  VERSION
  CHANGELOG.md
  CONTRIBUTING.md
  .github/pull_request_template.md
  .github/base-project.yml
  LICENSE
  base_manifest.yaml
  .github/workflows/issue-branch-policy.yml
  .github/workflows/project-intake.yml
  .github/workflows/tests.yml
)

for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || {
    printf 'Missing required file: %s\n' "$file" >&2
    exit 1
  }
done

command -v python >/dev/null || {
  printf 'Python is required; install the project development extra first.\n' >&2
  exit 1
}

python - <<'PY'
from importlib.metadata import PackageNotFoundError, version

for distribution in ("base-cli-demo", "base-cli", "pytest"):
    try:
        installed_version = version(distribution)
    except PackageNotFoundError as exc:
        raise SystemExit(
            f"Missing installed distribution {distribution!r}; "
            'run `python -m pip install ".[dev]"` first.'
        ) from exc
    print(f"Found {distribution} {installed_version}.")
PY

printf 'Running the complete consumer and documentation-command suite.\n'
exec python -m pytest -q

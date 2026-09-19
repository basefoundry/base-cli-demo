# Project Skills for base-cli-demo

Use this file as the repo-local index for project-specific agent workflows.
Keep entries short, concrete, and owned by this repository.

## Development workflow

- Start from a GitHub issue and use its single category label in the branch:
  `<category>/<issue>-<YYYYMMDD>-<slug>`.
- Use a dedicated worktree from `origin/main`; keep each PR scoped to one issue.
- Link a completing PR with `Fixes #<number>`. Do not merge unless the user
  explicitly asks for it.
- Preserve existing changes and leave the main checkout clean.

## Validation workflow

- Run `./tests/validate.sh` for the authoritative consumer gate.
- Run `uv run --extra dev pytest -q` for the complete default suite.
- Run `uv run --extra dev tests/package.sh` for wheel, sdist, and Twine checks.
- Run `uv lock --check` when changing dependencies or extras.
- Optional scenarios should be checked both without extras and with
  `uv run --extra dev --extra typer --extra rich --extra telemetry pytest -q`.

## Product boundary

- Keep Northstar deterministic, offline, and independent of the Base workspace
  runtime. It consumes released `base-cli` APIs only.
- Keep parser commands, service fixtures, and domain policy in this repository;
  keep lifecycle behavior at the public `base_cli` boundary.
- Do not make ecosystem/catalog examples depend on unreleased platform
  contracts.

## Release workflow

- Read `docs/release-process.md` before editing `VERSION`, release notes, tags,
  or GitHub Releases.
- Verify package contents and `basectl release check/plan/notes` first.
- Use `basectl release publish --version X.Y.Z --dry-run` to review the plan.
  Never create a tag or publish a GitHub Release without explicit user
  authorization.

## Boundaries

Do not vendor third-party methodology files here. Link to external guidance or
copy only repo-owned instructions that the project intends to maintain.
The branch convention is tool-independent; `feat/`, `agent/`, `codex/`, and
bare issue-number prefixes are invalid.

# Workflows

Install the development extra in an isolated Python environment, then run the
consumer's authoritative check:

```bash
python -m pip install '.[dev]'
./tests/validate.sh
northstar --help
northstar --quiet --environment dev status --format json
northstar --quiet --environment dev release plan --version 2.5.0
northstar --quiet --environment dev --dry-run release reconcile --version 2.5.0 --format json
```

The validator verifies installed distributions before running the complete
pytest suite, including documented-command tests. Follow the configuration guide
for `--config` inputs and the learning path for expected output. Use temporary
local state when experimenting with real reconciliation.

Use a single issue, matching category branch, and a dedicated worktree. PRs
record current validation and link their issue. Consumer release artifacts and
compatibility evidence are separate from framework releases; a documentation PR
does not update either version or publish packages.

Sources: [contribution guide](../CONTRIBUTING.md), [agent guidance](../AGENTS.md),
[learning path](../docs/learning-path.md), [validation](../tests/validate.sh), and
[release process](../docs/release-process.md).

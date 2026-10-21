# Contributing to base-cli-demo

Thank you for improving this project.

## Workflow

1. Create or choose a GitHub issue before starting implementation work.
2. Use exactly one standard issue category label: `bug`, `enhancement`,
   `documentation`, `ci`, or `security`.
3. Create an issue-backed branch:

   ```text
   <category>/<issue>-<YYYYMMDD>-<slug>
   ```

   The category prefix must match the issue's single standard category label.
   This branch shape is tool-independent; `feat/`, `agent/`, `codex/`, and
   bare issue-number prefixes are invalid.

4. Use a dedicated Git worktree for each pull request so the main checkout can
   stay on the default branch:

   ```bash
   git fetch origin
   git worktree add -b <branch> ../base-cli-demo-worktrees/<slug> origin/<default-branch>
   ```

5. Keep the pull request scoped to the issue and link it with
   `Fixes #<issue>` or `Closes #<issue>` when merge should close the issue.
6. Run the project checks before opening or updating a pull request.
7. Update `CHANGELOG.md` only for notable user-visible or release-worthy
   changes.
8. After merge, sync the default branch, remove the worktree, and delete merged
   local and remote branches when safe:

   ```bash
   git pull --ff-only origin <default-branch>
   git worktree remove ../base-cli-demo-worktrees/<slug>
   git branch -d <branch>
   git push origin --delete <branch>
   ```

Useful commands:

```bash
basectl check base-cli-demo
basectl doctor base-cli-demo
basectl test base-cli-demo
```

## AI Context Maintenance

Start AI-assisted orientation with [.ai-context/INDEX.md](.ai-context/INDEX.md).
Maintain these curated summaries alongside meaningful changes to product scope,
architecture, commands, or contributor workflows. Canonical docs and code remain
the source of truth; update the pack when they disagree. State context impact in
the PR, including a reason when no update is needed. Typo-only and internal changes
without behavioral or architectural impact usually need no context update.

Validate changes with `basectl export-context --list-files` and
`basectl export-context --print` from the checkout, plus `git diff --check`.
Keep the pack self-contained enough for offline reading, free of secrets and
private runtime data, and independent of generated timestamps or export bundles.

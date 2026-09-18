# Release Process

This repository uses the Base release contract. The machine-readable release
metadata lives in `base_manifest.yaml`; `basectl release check/plan/notes` use
that contract for readiness and release notes. GitHub immutable releases must
be prepared as drafts so validated assets are attached before publication.

## Standard Sequence

1. Create or choose a release issue and keep its Project metadata current.
2. Create a release-preparation branch and dedicated worktree from
   `origin/main`.
3. Update `VERSION`, the README release reference, and `CHANGELOG.md`.
   Keep ordinary pull requests under `[Unreleased]`; only release-preparation
   work changes the published version.
4. Run the repository validation command, `git diff --check`, and any package
   or integration checks required by this repository. For package checks, run
   `./tests/package.sh`; it builds a wheel and source distribution in a
   temporary directory and validates their contents with `twine`.
5. Open and merge the release-preparation pull request.
6. Sync local `main`, then inspect the release:

   ```bash
   basectl release check --version X.Y.Z
   basectl release plan --version X.Y.Z
   basectl release notes --version X.Y.Z > RELEASE_NOTES.md
   basectl release publish --version X.Y.Z --dry-run
   ```

7. After separate publication authorization, verify immutable releases are
   enabled for the repository, then create the annotated version tag for the
   exact reviewed `main` commit. Create a GitHub Release draft for that existing
   tag and add the release notes from step 6 (`RELEASE_NOTES.md`). Do not run
   `basectl release publish --yes` for this immutable-release path: it creates
   a published release directly, leaving no draft stage for attaching the
   validated assets.

   ```bash
   git tag -a vX.Y.Z -m "base-cli-demo vX.Y.Z"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --verify-tag --draft --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
   ```

8. Dispatch `Prepare draft release assets` with the tag and draft release ID
   (`gh release view vX.Y.Z --json databaseId --jq .databaseId`). The workflow
   verifies that the selected release is still a draft for that tag, tests the
   wheel against the minimum and latest supported Base-CLI releases on Python
   3.10 and 3.13, then attaches the wheel, sdist, exact compatibility evidence,
   and SHA-256 checksums. It never creates a tag or release and never publishes
   the draft.
9. Review the draft assets and verify the repository has immutable releases
   enabled. Then publish the draft in GitHub. When immutable releases are
   enabled, GitHub locks the tag and assets at publication; see the official
   [immutable releases guidance](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).
10. Confirm the README's version-pinned installation path in a clean
    environment, download the checksum/evidence files, and verify package
    filenames and hashes against the published assets.
11. Complete every declared downstream handoff. For Homebrew, update the tap
   formula to the published archive and checksum, run the formula tests and
   audit, publish required bottles, and verify install and upgrade paths. If a
   downstream repository pins this project by commit, update and validate that
   pin after the release.
12. Record the release and downstream URLs on the release issue, then remove
    the release worktree and merged branches when safe.

## Repository Contract

- Project: `base-cli-demo`
- GitHub repository: `basefoundry/base-cli-demo`
- Version file: `VERSION`
- Changelog: `CHANGELOG.md`
- Tag prefix: `v`

Do not publish a release when the repository is dirty, the version metadata is
inconsistent, the changelog section is missing, or a required downstream handoff
has not been identified.

# Required Pull Request Checks

The default branch should require these stable GitHub Actions check contexts:

- `Tests / required-consumer`
- `Compatibility / required-compatibility`

The aggregate jobs always run and fail if their underlying validation job or
supported-version matrix is skipped, cancelled, or unsuccessful. The optional
Typer/Rich/OpenTelemetry job remains useful coverage, but is not a merge
requirement for contributors who have not installed those extras.

Keep pull requests and both required checks mandatory. If the repository has a
single maintainer, the narrow exception is review approval only: configure no
required approval count (or allow that maintainer to self-approve), while still
requiring both checks to pass. Do not use a broad ruleset bypass for a failed or
pending check.

After this workflow change is merged, select both contexts in the
`Base default branch protection` ruleset and read the ruleset back to confirm
they are required. Until that external settings step is complete, this document
and the workflow alone do not enforce the checks at merge time.

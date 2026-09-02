# Released-package compatibility

The demo is a consumer of the published `base-cli` package, not a source
checkout consumer. Its declared support range is visible in `pyproject.toml`:

```text
base-cli>=0.4.3,<0.5
```

The [Compatibility workflow](../.github/workflows/compatibility.yml) builds a
wheel from this repository, installs the minimum released Base-CLI (`0.4.3`)
and the latest release in the supported `<0.5` line, then installs the demo
wheel without dependencies before running the tests. It covers Python 3.10
and 3.13, the ends of the supported interpreter range used by this repository.

The same tests execute every `northstar` command in the README through the
installed console script. They also parse the documented record output and
the optional JSON lifecycle envelope, so a source-tree import cannot make the
quickstart appear healthy.

The update policy is intentionally explicit:

- `0.4.3` is the minimum compatibility floor and changes only with a support
  decision.
- `<0.5` keeps the demo on the released 0.4 API line until a future issue
  evaluates the next minor API boundary.
- A pull request or release should update the range, tests, and this document
  together when the supported Base-CLI line changes.

## Upcoming builds

Run the workflow manually and provide a pip requirement suffix such as
`==0.4.4rc1` in the `upcoming_base_cli` input. The `upcoming` job is explicitly
non-blocking, so it provides early compatibility evidence without turning an
unreleased framework build into the supported release gate.

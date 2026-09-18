# Should I use base-cli?

## Status and compatibility

As of this guide, the newest published Base-CLI release is `0.4.3`; the package
is pre-1.0 and classified as Beta. The demo currently tests the released
`>=0.4.3,<0.5` line. This is not a promise that every future pre-1.0 minor line
is compatible: Base-CLI's published policy treats patch releases as compatible
and allows a minor release before 1.0 to be a compatibility boundary. Read the
[API stability policy](https://github.com/basefoundry/base-cli/blob/main/docs/api-stability.md)
and [migration notes](https://github.com/basefoundry/base-cli/blob/main/docs/migrations.md)
when changing the dependency range. The demo's lockfile records a reproducible
resolved environment; library consumers should choose a range that matches
their own upgrade policy.

Base-CLI does not replace Click or Typer. It composes with their command
surfaces to provide shared invocation lifecycle behavior; the application
continues to own its commands, configuration policy, and domain logic.

## Good fit

Base-CLI is worth evaluating when a team ships a Python CLI that has several
commands or consumers and needs a consistent operational contract across them:

- both interactive users and scripts need predictable output and exit status;
- operators need repeatable logging, diagnostics, temporary paths, and cleanup;
- commands benefit from shared dry-run, configuration, or lifecycle behavior;
- the team is willing to track the framework's supported release line and test
  upgrades.

The [Northstar walkthrough](learning-path.md) shows the smallest examples in
this repository. The [framework boundary](why-base-cli.md) explains which
decisions remain consumer-owned.

## Poor fit

Keep a simpler stack when a program is a one-off script, has one small command,
does not need machine-facing output or shared lifecycle behavior, or has a
policy against adding a framework dependency. Base-CLI is also not a fit for a
non-Python application, and a team that requires a frozen 1.0 API today should
account for its pre-1.0 status before adopting it.

## What adoption costs

You add `base-cli` as a runtime dependency and use its lifecycle/context and
public integration boundary. The application still owns its parser commands
and domain policy, but its entry point and tests now follow Base-CLI's
invocation model. The consuming team must maintain its supported dependency
range, lock or otherwise reproduce the environment, and run compatibility
tests when upgrading. Before 1.0, a minor framework upgrade may require a
compatibility review or code changes; this demo's `<0.5` bound deliberately
does not follow a future 0.5 line automatically.

## Alternatives and trade-offs

| Choice | What it gives you | What you take on |
| --- | --- | --- |
| `argparse` | A command-line parser in Python's standard library, with no third-party parser dependency. | Your application composes the command lifecycle, shared policy, and machine-output contract it needs. |
| Click | A composable command/group/option system with help and parsing behavior. | You choose and maintain the cross-command lifecycle, runtime state, logging, and output conventions. |
| Typer | A Click-based interface that derives command parameters from Python type hints. | You still decide whether to add a lifecycle layer and how to keep its operational behavior consistent. |
| Base-CLI with Click or Typer | A shared lifecycle and documented automation/output boundary around a familiar parser. | One more dependency, an integration model to learn, and compatibility work as the framework evolves. |

For the parser-focused comparison maintained by the framework project, see its
[framework choice guide](https://github.com/basefoundry/base-cli/blob/main/docs/framework-choice.md).
For primary references, see the official
[argparse documentation](https://docs.python.org/3/library/argparse.html),
[Click documentation](https://click.palletsprojects.com/), and
[Typer documentation](https://typer.tiangolo.com/).

# base-cli-demo

Reference consumer and learning application for the `base-cli` Python framework.

This repository contains Northstar, a small offline operational CLI. It is
designed to show how an application embeds Base-CLI while keeping its own
command tree, domain policy, and local data model.

Northstar does not require Base, Docker, cloud credentials, or network access
after its dependencies are installed.

## Quick start

From a fresh checkout:

```bash
$ python3 -m venv .venv
. .venv/bin/activate
$ python -m pip install .
$ northstar --help
$ northstar --quiet status
```

The default environment is `dev`. Select another fixture environment with the
framework lifecycle option:

```bash
$ northstar --quiet --environment staging status
$ northstar --quiet --environment dev status --format json
$ northstar --quiet --environment dev release plan --version 2.5.0
$ northstar --quiet --environment dev --dry-run release reconcile --version 2.5.0 --format json
```

Base-CLI also provides the optional versioned lifecycle envelope:

```bash
$ northstar --quiet --environment dev --json status --format json
```

For a guided five-minute walkthrough with expected output and the framework
boundary explained beside each scenario, see the
[scenario-driven learning path](docs/learning-path.md).

## What this demonstrates

- `northstar status` reads consumer-owned, deterministic service fixtures.
- `northstar release plan` is a nested command that produces a machine-readable
  release plan.
- `northstar release reconcile` uses the Base-CLI dry-run lifecycle boundary and
  explicitly reports that the demo performs no external changes.
- `--environment`, `--quiet`, `--debug`, `--config`, `--keep-temp`, and
  `--log-file` are lifecycle options supplied by Base-CLI.
- `--format` is a consumer-owned option that delegates rendering to the public
  Base-CLI output API.
- The `--json` option wraps command output in Base-CLI's versioned success or
  error envelope.

## Framework boundary

The application uses only the public `import base_cli` facade. Base-CLI owns the
invocation lifecycle, context, logging, runtime paths, cleanup, and structured
output. Northstar owns the Click command tree, service fixture schema, release
planning policy, and domain-facing messages.

The generic consumer profile is explicit in `src/base_cli_demo/cli.py`. The demo
does not inherit Base-specific manifest, project, history, or cache conventions.

## Development

Install the development extra and run the focused suite:

```bash
python -m pip install ".[dev]"
python -m pytest
./tests/validate.sh
```

The package requires Python 3.10 or newer and pins the supported Base-CLI line
to `>=0.4.3,<0.5`. The repository intentionally keeps demo versioning separate
from framework versioning.

## Repository shape

- `src/base_cli_demo/cli.py` contains the consumer-owned Click tree and the
  Base-CLI attachment boundary.
- `src/base_cli_demo/fixtures/services.json` contains deterministic local data.
- `tests/test_cli.py` exercises the installed lifecycle through the public
  testing helper.
- `pyproject.toml` defines the installable `northstar` console script.
- The generated Base repository files provide the project workflow and release
  contract; the demo itself does not require Base at runtime.

## Base

This repository is managed by [Base](https://github.com/basefoundry/base).

Common commands:

```bash
basectl setup base-cli-demo
basectl check base-cli-demo
basectl doctor base-cli-demo
basectl test base-cli-demo
```

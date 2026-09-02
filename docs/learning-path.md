# Five-minute Base-CLI learning path

Northstar is a small, offline reference consumer. The goal of this guide is
to show where an application uses Base-CLI and where the application keeps its
own domain behavior.

The examples use the published `base-cli` dependency declared by this
repository. They do not require Base, Docker, cloud credentials, or network
access after installation.

## 1. Install the consumer

From a fresh checkout, create an environment and install the demo with its
development checks:

```console
$ python3 -m venv .venv
$ . .venv/bin/activate
$ python -m pip install ".[dev]"
```

The package exposes the `northstar` command. Confirm that the nested command
tree and lifecycle options are available:

```console
$ northstar --help
Usage: northstar [OPTIONS] COMMAND [ARGS]...
```

The help text also lists `status`, `release`, `--environment`, `--dry-run`,
and the other lifecycle options.

## 2. Run a human-oriented snapshot

Start with the default `dev` fixture environment:

```console
$ northstar --quiet status
orders-api	ready	2.4.0	commerce
billing-worker	ready	1.8.2	finance
web	degraded	3.1.0	commerce
```

The service records and their schema are Northstar behavior. Base-CLI supplies
the invocation lifecycle, context, logging, runtime directory, cleanup, and
output boundary around that behavior.

## 3. Request automation-friendly output

The `--format` option is consumer-owned, while rendering is delegated to the
public Base-CLI output API:

```console
$ northstar --quiet --environment staging release plan --service orders-api --version 2.5.0 --format json
[{"environment":"staging","service":"orders-api","current_version":"2.3.9","target_version":"2.5.0","action":"update"}]
```

Use `--format csv`, `--format tsv`, `--format yaml`, or `--format ndjson` for
other automation boundaries. The command stays deterministic because its
input is the packaged local fixture.

## 4. Explore a nested workflow safely

`release reconcile` represents a state-changing workflow without performing
an external change. Add the Base-CLI lifecycle flag to see the dry-run
contract explicitly:

```console
$ northstar --quiet --environment dev --dry-run release reconcile --version 2.5.0 --format json
[{"environment":"dev","services":3,"target_version":"2.5.0","action":"would-reconcile","external_changes":false}]
```

The same command without `--dry-run` reports `"action":"reconciled"`, but it
still changes no external system. This is a teaching fixture, not a cloud
provider adapter.

## 5. See the lifecycle envelope

Automation can opt into the versioned Base-CLI success/error envelope:

```console
$ northstar --quiet --environment dev --json status --format json
{"schema_version":1,"schema":"base-cli.output","code":"ok",...}
```

The `run_id` is unique for each invocation, so it is intentionally abbreviated
above. The stable fields are the schema name, success code, exit code, and the
consumer command's serialized stdout. Use the unwrapped `--format json` form
when an integration needs only the command records.

## Read the boundary in the code

Open `src/base_cli_demo/cli.py` while following the examples:

- `cli`, `status`, `release`, `plan`, and `reconcile` are the consumer-owned
  Click command tree.
- `_load_services` and `_services_for_environment` define the local fixture
  model and selection policy.
- `base_cli.App`, `base_cli.CliProfile.generic()`,
  `base_cli.LifecycleOptions`, `base_cli.get_current_context()`, and
  `base_cli.render_records` are the public framework boundary.
- The demo does not import private Base-CLI modules and does not make Base
  repository conventions mandatory.

For deeper framework context, continue with the Base-CLI
[API reference](https://github.com/basefoundry/base-cli/blob/main/docs/api-reference.md),
[consumer profiles](https://github.com/basefoundry/base-cli/blob/main/docs/consumer-profiles.md),
[output contracts](https://github.com/basefoundry/base-cli/blob/main/docs/output-contracts.md),
[JSON contracts](https://github.com/basefoundry/base-cli/blob/main/docs/json-contracts.md),
and [testing guide](https://github.com/basefoundry/base-cli/blob/main/docs/testing.md).

## Current behavior and future scope

Everything demonstrated here is available in the released `base-cli` line
declared in `pyproject.toml`. Future Base-CLI ecosystem capabilities such as
Catalog discovery, cross-CLI metadata, and universal multi-language
conformance are deliberately not part of this learning path. They should be
documented here only after their contracts are released and documented.

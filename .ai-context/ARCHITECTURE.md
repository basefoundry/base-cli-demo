# Architecture

`src/base_cli_demo/cli.py` declares the Northstar Click tree and attaches a
generic Base-CLI profile through the public `base_cli` facade. Service fixtures
live under `src/base_cli_demo/fixtures/`; packaging declares the `northstar`
console script in `pyproject.toml`.

`status` renders fixture service state. `release plan` builds a release plan,
and `release reconcile` demonstrates consumer-owned reconciliation with a dry-run
boundary. `config show` reports normalized configuration and its provenance.
An explicit JSON configuration can filter services by owner and select a default
release target; no explicit configuration preserves generic defaults.

Global lifecycle options such as `--environment`, `--quiet`, and `--dry-run`
belong before the subcommand. Consumer `--format` chooses a payload renderer;
framework `--json` adds the separate lifecycle envelope. Optional YAML, Typer,
Rich, and OpenTelemetry scenarios have explicit dependency boundaries. Tests
exercise public framework behavior rather than private imports.

Sources: [consumer CLI](../src/base_cli_demo/cli.py),
[configuration](../docs/configuration.md), [lifecycle](../docs/lifecycle-safety.md),
[YAML](../docs/yaml-output.md), and [optional integrations](../docs/optional-integrations.md).

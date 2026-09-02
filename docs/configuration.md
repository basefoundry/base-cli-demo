# Northstar configuration

Northstar demonstrates a consumer-owned configuration adapter on top of the
generic Base-CLI profile. It deliberately does not discover a manifest or
read machine-local files implicitly.

## Configuration file

Pass an explicit JSON object with the lifecycle-owned `--config` option:

```json
{
  "service_owner": "commerce",
  "release_version": "2.6.0"
}
```

The checked-in [commerce example](../examples/northstar-commerce.json) uses
this schema. `service_owner` limits service snapshots and release plans to
one fixture owner. `release_version` supplies the default target for release
commands; a command-line `--version` still overrides it.

The no-file path is also intentional:

```console
$ northstar --quiet config show --format json
[{"setting":"service_owner","value":null,"source":"consumer-default"},{"setting":"release_version","value":"2.5.0","source":"consumer-default"}]
```

The configured path shows the same lifecycle with consumer policy layered in:

```console
$ northstar --quiet --config examples/northstar-commerce.json config show --format json
[{"setting":"service_owner","value":"commerce","source":"explicit"},{"setting":"release_version","value":"2.6.0","source":"explicit"}]
$ northstar --quiet --config examples/northstar-commerce.json status --format json
[{"service":"orders-api","status":"ready","version":"2.4.0","owner":"commerce"},{"service":"web","status":"degraded","version":"3.1.0","owner":"commerce"}]
```

`NorthstarConfig` validates the two consumer settings before command logic
runs. It returns a public Base-CLI `ConfigSnapshot`, so the framework keeps
the consumer values in `Context.config` and the winning source for each field
in `Context.config_provenance`. The framework's own lifecycle configuration
remains separate in `Context.framework_config`.

Try a safe failure:

```console
$ northstar --quiet --config /tmp/invalid-northstar.json status
Error: Northstar config file '/tmp/invalid-northstar.json' contains invalid JSON: ...
```

The exact parser detail depends on the malformed input, but the command exits
with status 2 and does not print a traceback unless debugging is requested.

## Public extension boundary

`src/base_cli_demo/profile.py` contains the consumer adapter:

- `NorthstarConfig` is the consumer-owned typed model and validator.
- `load_config` is the consumer-owned explicit file policy.
- `northstar_profile()` calls the public `base_cli.CliProfile.generic()`
  factory and supplies only that policy.
- `get_config()` is the single typed accessor used by commands.

Base-CLI still owns lifecycle option parsing, runtime placement, logging,
cleanup, and structured output. Northstar owns the fixture schema, service
owner filter, release target default, JSON serialization, and user-facing
configuration messages.

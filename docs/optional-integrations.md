# Optional integration scenarios

The default `base-cli-demo` install remains a small Click application with no
Typer, Rich, or OpenTelemetry SDK dependency. Each optional scenario is a
separate console entry point and degrades to a successful minimal path when
its integration is not installed.

## Typer

Install the Typer extra and run the adapter scenario:

```console
$ python -m pip install ".[typer]"
$ northstar-typer --quiet --name Ada --count 2
adapter=typer
hello Ada
hello Ada
```

The scenario uses `base_cli.attach_typer()` when Typer is present. Without the
extra, the same command uses a native Click fallback and reports
`adapter=click-fallback`; its exit status and output contract remain usable.

## Rich

Install Rich to opt into polished human tables:

```console
$ python -m pip install ".[rich]"
$ northstar-rich --quiet status
```

The app is constructed with `rich=True`. Base-CLI lazily uses Rich only for
interactive human text and falls back to its deterministic renderer if Rich is
missing. Machine formats are unchanged:

```console
$ northstar-rich --quiet status --format json
[{"service":"orders-api","status":"ready"},{"service":"web","status":"degraded"}]
```

## OpenTelemetry

Install the optional API package to enable the lifecycle integration:

```console
$ python -m pip install ".[telemetry]"
$ northstar-telemetry --quiet
telemetry=enabled
```

Without the extra, the command reports `telemetry=unavailable (install
[telemetry])` and still exits successfully. With the extra, Base-CLI owns the
`base_cli.run` lifecycle span and its bounded safe attributes; the scenario
does not attach argv, configuration, paths, or secrets.

The focused tests run in both modes: the normal CI job exercises the minimal
fallbacks, while the optional-integration CI job installs all three extras and
exercises the enabled adapters.

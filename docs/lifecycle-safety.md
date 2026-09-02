# Lifecycle safety and automation contracts

Northstar uses a local reconciliation fixture to show the boundaries a
production-shaped command should make explicit. It never calls a cloud API or
changes an external system.

## Dry-run is side-effect free

The regular command persists a local `last-reconciliation.json` state record
under the Base-CLI runtime state directory and uses a managed temporary input
while it runs:

```console
$ northstar --quiet release reconcile --version 2.5.0 --format json
[{"environment":"dev","services":3,"target_version":"2.5.0","action":"reconciled","external_changes":false}]
```

The lifecycle dry-run flag changes the action and skips the local state write:

```console
$ northstar --quiet --dry-run release reconcile --version 2.5.0 --format json
[{"environment":"dev","services":3,"target_version":"2.5.0","action":"would-reconcile","external_changes":false}]
```

Both paths report `external_changes: false` because this repository is an
offline teaching consumer. The tests distinguish the local state file and
assert that dry-run leaves it absent. Base-CLI removes the temporary input
through the consumer cleanup hook after a normal run.

## Human and machine contracts

Human output remains the default. A consumer can select a record format and,
when needed, the versioned lifecycle envelope:

```console
$ northstar --quiet --json release reconcile --dry-run --format json
{"schema":"base-cli.output","code":"ok",...}
```

The envelope's `run_id` is unique per invocation. Its stable fields identify a
successful command, preserve the numeric exit code, and carry the command's
serialized output. The unwrapped `--format json` form is useful when a script
needs only the records.

## Structured errors and exit status

An invalid environment is a user-correctable command failure. In JSON mode it
is represented as a Base-CLI error envelope and retains a non-zero exit code:

```console
$ northstar --quiet --json --environment unknown status
{"schema":"base-cli.error","type":"error","code":"click_error",...}
```

Unexpected application failures remain hidden behind the framework's generic
error boundary unless `--debug` is requested. Consumer validation errors should
use the public `base_cli.ConfigurationError` or Click exception types so they
are safe to show and test.

## Diagnostics and sensitive inputs

Base-CLI owns debug logging, log-file selection, and redaction of the hidden
approval token declared by Northstar:

```console
$ northstar --debug --log-file /tmp/northstar.log release reconcile --approval-token demo-secret
```

The command succeeds, but `demo-secret` is not written to the log. The
recorded invocation contains `[REDACTED]`. A real consumer must mark every
domain-specific secret-bearing option and must not treat log redaction as a
secrets manager.

## What belongs where

Northstar owns the reconciliation record, its local state path, and the
cleanup hook. Base-CLI owns the lifecycle context, dry-run flag, runtime and
temporary directory placement, logging, redaction, structured envelopes,
exit-code boundary, and final cleanup. Keeping those responsibilities visible
is the point of the example.

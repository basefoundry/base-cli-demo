# Why base-cli?

Every CLI application chooses how to define commands. A production CLI also
needs a repeatable contract around each command: where logs go, how errors map
to exit status, where temporary and run data live, how cleanup runs, and how
automation requests structured output. Without a shared lifecycle layer, each
application decides, implements, and tests those details for itself.

Base-CLI composes with Click (and can attach to Typer); it is not a replacement
parser. It supplies the invocation lifecycle and public output/runtime APIs,
while the consumer keeps its command tree, configuration policy, and domain
behavior.

| Shared concern | Northstar example | What the framework supplies |
| --- | --- | --- |
| Human and machine output | `northstar status --format json` | Public record renderers and stable JSON records. |
| Automation envelope | `northstar --json status --format json` | A versioned success/error envelope and the command's exit status. |
| Safe state-changing workflow | `northstar --dry-run release reconcile` | A lifecycle dry-run flag and consistent invocation context; Northstar decides what its local demo operation means. |
| Diagnostics | `northstar --debug --log-file ... release reconcile` | Lifecycle logging, log placement, and registered sensitive-argument redaction. |
| Per-run files and cleanup | `release reconcile` | Managed runtime/temp paths and cleanup hooks; Northstar owns its state record. |

## What would otherwise be hand-written

The small consumer entry point in [`src/base_cli_demo/cli.py`](../src/base_cli_demo/cli.py)
still owns the Click command tree and domain behavior. Without Base-CLI, that
same file would also need to hand-write and test the surrounding lifecycle:

- turn `--environment`, `--dry-run`, `--json`, `--debug`, `--log-file`, and
  `--keep-temp` into a consistent invocation context;
- choose state and temporary directories, run cleanup callbacks, and preserve
  the dry-run boundary around `release reconcile`;
- route records through text/JSON/CSV/TSV/NDJSON output and emit the structured
  success/error envelope used by automation; and
- configure logging, redact `approval_token`, and map command failures to stable
  exit status.

Those are the production-shaped behaviors supplied by Base-CLI and exercised
through its public facade. Northstar still decides its service fixture schema,
environment selection, target-version policy, and the meaning of
`release reconcile`; those decisions remain in the Click commands and
[`src/base_cli_demo/profile.py`](../src/base_cli_demo/profile.py). The README's
[framework boundary](../README.md#framework-boundary) is the concise ownership
summary.

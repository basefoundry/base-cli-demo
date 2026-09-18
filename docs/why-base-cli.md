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
| Diagnostics | `--debug --log-file ... release reconcile` | Lifecycle logging, log placement, and registered sensitive-argument redaction. |
| Per-run files and cleanup | `release reconcile` | Managed runtime/temp paths and cleanup hooks; Northstar owns its state record. |

## What this demo still owns

The framework does not decide Northstar's service schema, which services belong
to an environment, the default target version, or the meaning of
`release reconcile`. Those choices remain in the consumer's Click commands,
fixtures, and configuration adapter. The boundary is visible in
[`src/base_cli_demo/cli.py`](../src/base_cli_demo/cli.py) and
[`src/base_cli_demo/profile.py`](../src/base_cli_demo/profile.py).

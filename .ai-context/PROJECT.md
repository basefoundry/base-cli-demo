# Northstar reference consumer

Northstar is a small offline operational CLI that demonstrates embedding
`base-cli` in a real consumer. It uses deterministic service fixtures and local
release planning/reconciliation to explain lifecycle, machine output,
configuration, dry-run, and error behavior.

It requires its Python dependencies, not Base, Docker, cloud credentials, or
network services at runtime. Its package/release version is independent of the
framework version. `pyproject.toml` records the supported framework range;
compatibility tests establish the installed-package behavior.

Northstar owns its Click command tree, fixture schema, domain policy, and
messages. Base-CLI owns reusable invocation context, logging, runtime paths,
cleanup, and output contracts. Demonstrated reconciliation does not deploy
software or mutate external services. Local reconciliation state has its own
application contract and should not be mistaken for an external release.

Sources: [README](../README.md), [metadata](../pyproject.toml),
[framework value/boundary](../docs/why-base-cli.md), and
[compatibility](../docs/compatibility.md).

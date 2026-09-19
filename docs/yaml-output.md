# Optional YAML Output

YAML is a supported Base-CLI renderer, but it is intentionally not part of the
demo's minimal dependencies. Install the optional extra before using
`--format yaml`:

```console
$ python -m pip install "base-cli-demo[yaml]"
$ northstar --quiet status --format yaml
```

Without the extra, Northstar reports this install command before running the
consumer command. In particular, a reconciliation does not persist local state
and then fail while trying to render YAML.

# Use Base-CLI in your project

Northstar is intentionally production-shaped. If you want the smallest
transferable pattern, start with one Click command and let Base-CLI own the
invocation lifecycle.

Install the released framework line used by this demo:

```bash
python -m pip install "base-cli>=0.4.3,<0.5" "click>=8.1,<9"
```

Save this as `hello.py`:

```python
from __future__ import annotations

import base_cli
import click


@click.command()
@click.option("--name", default="world", show_default=True)
def hello(name: str) -> None:
    click.echo(f"hello {name}")


app = base_cli.App(name="hello", version="0.1.0")
command = app.attach(hello)


if __name__ == "__main__":
    raise SystemExit(base_cli.run_app(command))
```

Run it:

```console
$ python hello.py --name Ada
hello Ada
```

The runnable copy in [`examples/minimal_cli.py`](../examples/minimal_cli.py)
is exercised by the test suite. From the example, continue with the
[five-minute Northstar tour](learning-path.md) to see nested commands,
consumer-owned configuration, and structured output.

The `App` and `attach` calls establish the framework boundary; the Click
function remains your command. See the framework's
[consumer quickstart](https://github.com/basefoundry/base-cli/blob/main/docs/consumer-quickstart.md)
and [API reference](https://github.com/basefoundry/base-cli/blob/main/docs/api-reference.md)
for the public interfaces.

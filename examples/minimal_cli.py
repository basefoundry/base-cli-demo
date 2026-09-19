"""Smallest runnable Click command attached to the Base-CLI lifecycle."""

from __future__ import annotations

import base_cli
import click


@click.command()
@click.option("--name", default="world", show_default=True)
def hello(name: str) -> None:
    """Greet one person."""

    click.echo(f"hello {name}")


app = base_cli.App(name="hello", version="0.1.0")
command = app.attach(hello)


def main() -> int:
    """Run the minimal example through Base-CLI."""

    return base_cli.run_app(command)


if __name__ == "__main__":
    raise SystemExit(main())

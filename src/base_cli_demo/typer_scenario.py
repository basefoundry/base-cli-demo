"""Optional Typer adapter scenario with a Click fallback."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import base_cli
import click


def _hello(output: Callable[[str], Any], name: str, count: int, adapter: str) -> None:
    context = base_cli.get_current_context()
    context.log.info("running the %s adapter", adapter)
    output(f"adapter={adapter}")
    for _ in range(count):
        output(f"hello {name}")


def _click_command() -> Any:
    @click.command(name="northstar-typer")
    @click.option("--name", default="Ada", show_default=True)
    @click.option("--count", default=1, type=click.IntRange(min=1), show_default=True)
    def cli(name: str, count: int) -> None:
        """Run the Typer learning scenario through its fallback path."""
        _hello(click.echo, name, count, "click-fallback")

    return base_cli.attach(cli, name="northstar-typer", log_to_file=False)


def main() -> int:
    """Run native Typer when installed, otherwise use the Click fallback."""

    try:
        import typer
    except ImportError:
        command = _click_command()
    else:
        typer_app = typer.Typer(
            name="northstar-typer",
            help="Run the Typer adapter learning scenario.",
            no_args_is_help=True,
        )

        @typer_app.command()
        def hello(
            name: str = typer.Option("Ada", "--name", help="Name to greet."),
            count: int = typer.Option(1, "--count", min=1, help="Greeting count."),
        ) -> None:
            _hello(typer.echo, name, count, "typer")

        command = base_cli.attach_typer(
            typer_app,
            name="northstar-typer",
            log_to_file=False,
        )
    return base_cli.run_app(command)


if __name__ == "__main__":
    raise SystemExit(main())

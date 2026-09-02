"""Optional Rich output scenario."""

from __future__ import annotations

from typing import Any

import base_cli
import click

OUTPUT_FORMAT = click.Choice(
    base_cli.output_format_choices().split("|"),
    case_sensitive=False,
)


@click.group(name="northstar-rich", help="Run the optional Rich output scenario.")
def cli() -> None:
    """Keep Rich an optional presentation layer."""


@cli.command()
@click.option(
    "--format",
    "output_format",
    type=OUTPUT_FORMAT,
    default="text",
    show_default=True,
)
def status(output_format: str) -> None:
    """Render a human table or a normal machine format."""

    context = base_cli.get_current_context()
    records: tuple[dict[str, Any], ...] = (
        {"service": "orders-api", "status": "ready"},
        {"service": "web", "status": "degraded"},
    )
    base_cli.render_records(
        records,
        requested_format=output_format,
        columns=(("SERVICE", "service"), ("STATUS", "status")),
        rich=context.rich,
    )


app = base_cli.App(name="northstar-rich", rich=True, log_to_file=False)
command = app.attach(cli)


def main() -> int:
    """Use Rich when present and built-in output otherwise."""

    return base_cli.run_app(command)


if __name__ == "__main__":
    raise SystemExit(main())

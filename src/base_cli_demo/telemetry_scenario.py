"""Optional OpenTelemetry lifecycle scenario."""

from __future__ import annotations

import importlib.util

import base_cli
import click

TELEMETRY_AVAILABLE = importlib.util.find_spec("opentelemetry") is not None


@click.command(name="northstar-telemetry", help="Run the optional telemetry scenario.")
def status() -> None:
    """Report whether the optional lifecycle span integration is configured."""

    context = base_cli.get_current_context()
    context.log.info("telemetry scenario invoked")
    state = "enabled" if TELEMETRY_AVAILABLE else "unavailable (install [telemetry])"
    click.echo(f"telemetry={state}")


app = base_cli.App(
    name="northstar-telemetry",
    log_to_file=False,
    telemetry=base_cli.TelemetryOptions() if TELEMETRY_AVAILABLE else None,
)
command = app.attach(status)


def main() -> int:
    """Run telemetry without making its SDK a core dependency."""

    return base_cli.run_app(command)


if __name__ == "__main__":
    raise SystemExit(main())

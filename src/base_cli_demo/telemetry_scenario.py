"""Optional OpenTelemetry lifecycle scenario."""

from __future__ import annotations

import importlib.util

import base_cli
import click

API_AVAILABLE = importlib.util.find_spec("opentelemetry") is not None
SDK_AVAILABLE = API_AVAILABLE and importlib.util.find_spec("opentelemetry.sdk") is not None
TELEMETRY_AVAILABLE = SDK_AVAILABLE

if SDK_AVAILABLE:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    SPAN_EXPORTER = InMemorySpanExporter()
    TRACER_PROVIDER = TracerProvider()
    TRACER_PROVIDER.add_span_processor(SimpleSpanProcessor(SPAN_EXPORTER))
else:
    SPAN_EXPORTER = None
    TRACER_PROVIDER = None


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
    telemetry=(
        base_cli.TelemetryOptions(tracer_provider=TRACER_PROVIDER)
        if SDK_AVAILABLE
        else None
    ),
)
command = app.attach(status)


def main() -> int:
    """Run telemetry without making its SDK a core dependency."""

    exit_code = base_cli.run_app(command)
    if SPAN_EXPORTER is not None and TRACER_PROVIDER is not None:
        TRACER_PROVIDER.force_flush()
        spans = SPAN_EXPORTER.get_finished_spans()
        click.echo(f"recorded_spans={len(spans)}")
        for span in spans:
            click.echo(f"span={span.name} status={span.status.status_code.name}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

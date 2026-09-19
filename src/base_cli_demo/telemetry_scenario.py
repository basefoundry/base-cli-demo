"""Optional OpenTelemetry lifecycle scenario."""

from __future__ import annotations

from typing import Any

import base_cli
import click

def _configure_telemetry() -> tuple[Any | None, Any | None]:
    """Create the demo SDK objects without making import failures fatal."""

    try:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )

        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        return exporter, provider
    except BaseException:
        # Optional integration setup must not change the consumer's normal
        # command behavior when the plugin is missing or broken.
        return None, None


SPAN_EXPORTER, TRACER_PROVIDER = _configure_telemetry()
TELEMETRY_AVAILABLE = SPAN_EXPORTER is not None and TRACER_PROVIDER is not None


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
        if TELEMETRY_AVAILABLE
        else None
    ),
)
command = app.attach(status)


def main() -> int:
    """Run telemetry without making its SDK a core dependency."""

    exit_code = base_cli.run_app(command)
    if SPAN_EXPORTER is not None and TRACER_PROVIDER is not None:
        try:
            TRACER_PROVIDER.force_flush()
            spans = SPAN_EXPORTER.get_finished_spans()
            click.echo(f"recorded_spans={len(spans)}")
            for span in spans:
                click.echo(f"span={span.name} status={span.status.status_code.name}")
        except BaseException:
            # Exporter teardown is best-effort after the command outcome is
            # already known; it must not turn a successful invocation into a
            # failed CLI run.
            pass
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

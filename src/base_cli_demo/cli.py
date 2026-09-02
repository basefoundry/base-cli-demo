"""Northstar, an offline reference consumer for base-cli."""

from __future__ import annotations

import json
from collections.abc import Mapping
from importlib.resources import files
from typing import Any

import base_cli
import click

from .profile import get_config, northstar_profile

SERVICE_NAMES = ("orders-api", "billing-worker", "web")
OUTPUT_FORMAT = click.Choice(
    base_cli.output_format_choices().split("|"),
    case_sensitive=False,
)


def _load_services() -> tuple[dict[str, str], ...]:
    """Load and validate the application-owned deterministic fixture."""

    fixture_path = files("base_cli_demo.fixtures").joinpath("services.json")
    payload: Any = json.loads(fixture_path.read_text(encoding="utf-8"))
    entries = payload.get("services") if isinstance(payload, Mapping) else None
    if not isinstance(entries, list):
        raise TypeError("The services fixture must contain a services list.")

    services: list[dict[str, str]] = []
    required_fields = ("name", "environment", "version", "status", "owner")
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise TypeError("Every service fixture entry must be an object.")
        record = {field: entry.get(field) for field in required_fields}
        if not all(isinstance(value, str) and value for value in record.values()):
            raise RuntimeError(
                "Every service fixture entry must contain string fields."
            )
        services.append({field: str(record[field]) for field in required_fields})
    return tuple(services)


def _services_for_environment(
    environment: str,
    requested_service: str = "all",
    service_owner: str | None = None,
) -> tuple[dict[str, str], ...]:
    """Return fixture services selected by the consumer-owned domain policy."""

    services = tuple(
        service
        for service in _load_services()
        if service["environment"] == environment
        and (requested_service == "all" or service["name"] == requested_service)
        and (service_owner is None or service["owner"] == service_owner)
    )
    if not services:
        if requested_service == "all":
            raise click.ClickException(
                f"No fixture services are defined for environment '{environment}'."
            )
        raise click.ClickException(
            f"Service '{requested_service}' is not defined for environment '{environment}'."
        )
    return services


def _render(
    context: base_cli.Context[Any, Any, Any],
    records: tuple[Mapping[str, Any], ...],
    output_format: str,
    columns: tuple[tuple[str, str], ...],
) -> None:
    """Render records through the framework-owned output boundary."""

    base_cli.render_records(
        records,
        requested_format=output_format,
        columns=columns,
        rich=context.rich,
    )


def _persist_reconciliation(
    context: base_cli.Context[Any, Any, Any], record: Mapping[str, Any]
) -> None:
    """Persist local demo state and clean its temporary input after the run."""

    if context.dry_run:
        return

    state_path = context.state_dir / "last-reconciliation.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(dict(record), sort_keys=True) + "\n",
        encoding="utf-8",
    )

    temporary_input = context.temp_dir / "reconciliation-input.json"
    temporary_input.write_text(
        json.dumps(dict(record), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    context.on_cleanup(lambda: temporary_input.unlink(missing_ok=True))


def _service_option(function: Any) -> Any:
    return click.option(
        "--service",
        type=click.Choice(("all",) + SERVICE_NAMES, case_sensitive=False),
        default="all",
        show_default=True,
        help="Limit the command to one service.",
    )(function)


def _format_option(function: Any) -> Any:
    return click.option(
        "--format",
        "output_format",
        type=OUTPUT_FORMAT,
        default="text",
        show_default=True,
        help="Render text, CSV, TSV, YAML, JSON, or NDJSON.",
    )(function)


@click.group(
    name="northstar", help="Explore a production-shaped base-cli consumer offline."
)
def cli() -> None:
    """Keep the command tree and domain policy owned by the consumer."""


@cli.command()
@_format_option
def status(output_format: str) -> None:
    """Show the local service snapshot for the selected environment."""

    context = base_cli.get_current_context()
    config = get_config(context)
    services = _services_for_environment(
        context.environment,
        service_owner=config.service_owner,
    )
    context.log.info("status requested for %s", context.environment)
    records = tuple(
        {
            "service": service["name"],
            "status": service["status"],
            "version": service["version"],
            "owner": service["owner"],
        }
        for service in services
    )
    _render(
        context,
        records,
        output_format,
        (
            ("SERVICE", "service"),
            ("STATUS", "status"),
            ("VERSION", "version"),
            ("OWNER", "owner"),
        ),
    )


@cli.group()
def release() -> None:
    """Plan and reconcile a local release snapshot."""


@release.command("plan")
@_format_option
@click.option(
    "--version",
    "target_version",
    default=None,
    help="Override the configured target release version.",
)
@_service_option
def plan(service: str, target_version: str | None, output_format: str) -> None:
    """Create a deterministic release plan without external changes."""

    context = base_cli.get_current_context()
    config = get_config(context)
    selected = _services_for_environment(
        context.environment,
        service,
        service_owner=config.service_owner,
    )
    target_version = target_version or config.release_version
    context.log.info("release plan requested for %s", context.environment)
    records = tuple(
        {
            "environment": context.environment,
            "service": item["name"],
            "current_version": item["version"],
            "target_version": target_version,
            "action": "update" if item["version"] != target_version else "unchanged",
        }
        for item in selected
    )
    _render(
        context,
        records,
        output_format,
        (
            ("ENVIRONMENT", "environment"),
            ("SERVICE", "service"),
            ("CURRENT", "current_version"),
            ("TARGET", "target_version"),
            ("ACTION", "action"),
        ),
    )


@release.command("reconcile")
@_format_option
@click.option(
    "--version",
    "target_version",
    default=None,
    help="Override the configured target release version.",
)
@_service_option
@click.option(
    "--approval-token", hidden=True, help="Example sensitive adapter credential."
)
def reconcile(
    service: str,
    target_version: str | None,
    output_format: str,
    approval_token: str | None,
) -> None:
    """Reconcile a local snapshot, with dry-run controlled by base-cli."""

    del approval_token
    context = base_cli.get_current_context()
    config = get_config(context)
    selected = _services_for_environment(
        context.environment,
        service,
        service_owner=config.service_owner,
    )
    target_version = target_version or config.release_version
    action = "would-reconcile" if context.dry_run else "reconciled"
    context.log.info(
        "%s %d service(s) in %s", action, len(selected), context.environment
    )
    record = {
        "environment": context.environment,
        "services": len(selected),
        "target_version": target_version,
        "action": action,
        "external_changes": False,
    }
    _persist_reconciliation(context, record)
    _render(
        context,
        (record,),
        output_format,
        (
            ("ENVIRONMENT", "environment"),
            ("SERVICES", "services"),
            ("TARGET", "target_version"),
            ("ACTION", "action"),
            ("EXTERNAL CHANGES", "external_changes"),
        ),
    )


@cli.group()
def config() -> None:
    """Inspect the consumer-owned Northstar configuration policy."""


@config.command("show")
@_format_option
def show_config(output_format: str) -> None:
    """Show normalized consumer settings and their source layers."""

    context = base_cli.get_current_context()
    records = tuple(
        {
            "setting": key,
            "value": value,
            "source": context.config_provenance.get(key, "consumer-default"),
        }
        for key, value in context.config.items()
    )
    _render(
        context,
        records,
        output_format,
        (("SETTING", "setting"), ("VALUE", "value"), ("SOURCE", "source")),
    )


app = base_cli.App(
    name="northstar",
    version="0.1.0",
    profile=northstar_profile(),
    lifecycle_options=base_cli.LifecycleOptions(
        environment=base_cli.LifecycleOption(
            "--environment",
            default="dev",
            show_default=True,
            help="Select the local fixture environment.",
        ),
        dry_run=base_cli.LifecycleOption(
            "--dry-run",
            help="Describe reconciliation without applying local changes.",
        ),
        json=base_cli.LifecycleOption(
            "--json",
            help="Wrap command output in the versioned base-cli JSON envelope.",
        ),
    ),
)

command = app.attach(cli, sensitive_parameters={"approval_token"})


def main() -> int:
    """Run Northstar through the production base-cli lifecycle."""

    return base_cli.run_app(command)


if __name__ == "__main__":
    raise SystemExit(main())

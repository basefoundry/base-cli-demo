from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import base_cli

from base_cli_demo.cli import command


def invoke(args: list[str], home: Path) -> Any:
    return base_cli.testing.invoke(command, ["--quiet", *args], home=home)


def test_help_exposes_nested_consumer_commands_and_lifecycle_options() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(["--help"], Path(directory))

    assert result.exit_code == 0, result.output
    assert "status" in result.stdout
    assert "release" in result.stdout
    assert "--environment" in result.stdout
    assert "--dry-run" in result.stdout


def test_status_reads_the_selected_local_fixture_environment() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            ["--environment", "dev", "status", "--format", "json"], Path(directory)
        )

    assert result.exit_code == 0, result.output
    records = json.loads(result.stdout)
    assert [record["service"] for record in records] == [
        "orders-api",
        "billing-worker",
        "web",
    ]
    assert records[-1]["status"] == "degraded"


def test_release_plan_is_nested_and_machine_readable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            [
                "--environment",
                "staging",
                "release",
                "plan",
                "--service",
                "orders-api",
                "--version",
                "2.5.0",
                "--format",
                "json",
            ],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {
            "environment": "staging",
            "service": "orders-api",
            "current_version": "2.3.9",
            "target_version": "2.5.0",
            "action": "update",
        }
    ]


def test_reconcile_dry_run_reports_no_external_changes() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            [
                "--environment",
                "dev",
                "--dry-run",
                "release",
                "reconcile",
                "--version",
                "2.5.0",
                "--format",
                "json",
            ],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {
            "environment": "dev",
            "services": 3,
            "target_version": "2.5.0",
            "action": "would-reconcile",
            "external_changes": False,
        }
    ]


def test_json_lifecycle_envelope_is_available_to_consumers() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            ["--environment", "dev", "--json", "status", "--format", "json"],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["schema"] == "base-cli.output"
    assert payload["code"] == "ok"
    assert '"orders-api"' in payload["details"]["stdout"]

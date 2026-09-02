from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def run_scenario(
    module: str, args: list[str], home: Path
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "HOME": str(home / "home"),
            "BASE_CLI_CACHE_DIR": str(home / "cache"),
            "USERPROFILE": str(home / "home"),
            "LOCALAPPDATA": str(home / "home" / "AppData" / "Local"),
        }
    )
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        capture_output=True,
        cwd=home,
        env=environment,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("module", "args", "expected"),
    [
        ("base_cli_demo.typer_scenario", ["--quiet", "--name", "Ada"], "hello Ada"),
        ("base_cli_demo.rich_scenario", ["--quiet", "status"], "orders-api"),
        (
            "base_cli_demo.telemetry_scenario",
            ["--quiet"],
            "telemetry=",
        ),
    ],
)
def test_optional_scenarios_succeed_on_the_minimal_install(
    module: str, args: list[str], expected: str, tmp_path: Path
) -> None:
    result = run_scenario(module, args, tmp_path)

    assert result.returncode == 0, f"{module}: {result.stdout}\n{result.stderr}"
    assert expected in result.stdout


def test_rich_machine_output_remains_plain_json(tmp_path: Path) -> None:
    result = run_scenario(
        "base_cli_demo.rich_scenario",
        ["--quiet", "status", "--format", "json"],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0] == {"service": "orders-api", "status": "ready"}


def test_typer_adapter_path_is_used_when_the_optional_dependency_is_installed(
    tmp_path: Path,
) -> None:
    if importlib.util.find_spec("typer") is None:
        pytest.skip("Typer is not installed in the minimal test environment")

    result = run_scenario(
        "base_cli_demo.typer_scenario",
        ["--quiet", "--name", "Ada"],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert "adapter=typer" in result.stdout


def test_telemetry_reports_the_optional_state_without_affecting_exit_status(
    tmp_path: Path,
) -> None:
    result = run_scenario(
        "base_cli_demo.telemetry_scenario",
        ["--quiet"],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("telemetry=")

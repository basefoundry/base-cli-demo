from __future__ import annotations

import importlib.util
import json
import os
import pty
import select
import subprocess
import sys
import time
from pathlib import Path

import pytest


def module_available(name: str) -> bool:
    """Treat a missing parent package as an unavailable optional module."""

    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


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


def test_telemetry_sdk_records_the_base_cli_lifecycle_span(tmp_path: Path) -> None:
    if not module_available("opentelemetry.sdk"):
        pytest.skip("OpenTelemetry SDK is installed by the optional telemetry extra")

    result = run_scenario("base_cli_demo.telemetry_scenario", ["--quiet"], tmp_path)

    assert result.returncode == 0, result.stderr
    assert "recorded_spans=1" in result.stdout
    assert "span=base_cli.run" in result.stdout
    assert "status=UNSET" in result.stdout


def test_rich_human_renderer_runs_on_a_real_terminal(tmp_path: Path) -> None:
    if os.name != "posix" or importlib.util.find_spec("rich") is None:
        pytest.skip("Rich TTY integration requires POSIX and the Rich extra")

    master_fd, slave_fd = pty.openpty()
    environment = os.environ.copy()
    environment.update(
        {
            "HOME": str(tmp_path / "home"),
            "BASE_CLI_CACHE_DIR": str(tmp_path / "cache"),
            "USERPROFILE": str(tmp_path / "home"),
            "TERM": "xterm-256color",
            "COLUMNS": "80",
        }
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "base_cli_demo.rich_scenario", "--quiet", "status"],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=tmp_path,
        env=environment,
        close_fds=True,
    )
    os.close(slave_fd)
    output = bytearray()
    deadline = time.monotonic() + 20
    try:
        while process.poll() is None:
            if time.monotonic() >= deadline:
                process.kill()
                pytest.fail("Rich TTY command did not finish within 20 seconds")
            readable, _, _ = select.select([master_fd], [], [], 0.1)
            if readable:
                try:
                    output.extend(os.read(master_fd, 4096))
                except OSError:
                    break
        process.wait(timeout=20)
        while select.select([master_fd], [], [], 0.1)[0]:
            try:
                chunk = os.read(master_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output.extend(chunk)
    finally:
        os.close(master_fd)

    rendered = output.decode("utf-8", errors="replace")
    assert process.returncode == 0, rendered
    assert "orders-api" in rendered
    assert "degraded" in rendered
    assert "─" in rendered

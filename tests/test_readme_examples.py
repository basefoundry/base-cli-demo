from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def readme_commands() -> list[list[str]]:
    commands: list[list[str]] = []
    in_shell_block = False
    for line in Path("README.md").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_shell_block = not in_shell_block
            continue
        if in_shell_block and line.strip().startswith("northstar"):
            commands.append(shlex.split(line.strip()))
    return commands


def run_installed_command(
    args: list[str], home: Path
) -> subprocess.CompletedProcess[str]:
    venv_executable = Path(sys.executable).with_name(args[0])
    executable = (
        str(venv_executable) if venv_executable.is_file() else shutil.which(args[0])
    )
    assert executable is not None, "the installed northstar console script is required"
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
        [executable, *args[1:]],
        capture_output=True,
        cwd=home,
        env=environment,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("args", readme_commands(), ids=lambda args: " ".join(args))
def test_readme_northstar_commands_run_from_the_installed_wheel(
    args: list[str], tmp_path: Path
) -> None:
    result = run_installed_command(args, tmp_path)

    assert result.returncode == 0, (
        f"{args!r}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_readme_json_output_is_machine_readable(tmp_path: Path) -> None:
    result = run_installed_command(
        ["northstar", "--quiet", "--environment", "dev", "status", "--format", "json"],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    records = json.loads(result.stdout)
    assert records[0]["service"] == "orders-api"
    assert records[-1]["status"] == "degraded"


def test_readme_json_envelope_is_machine_readable(tmp_path: Path) -> None:
    result = run_installed_command(
        [
            "northstar",
            "--quiet",
            "--environment",
            "dev",
            "--json",
            "status",
            "--format",
            "json",
        ],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema"] == "base-cli.output"
    assert payload["code"] == "ok"

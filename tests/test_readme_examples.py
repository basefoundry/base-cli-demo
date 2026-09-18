from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


README_PATH = Path(__file__).parents[1] / "README.md"
EXAMPLES_PATH = Path(__file__).parents[1] / "examples"


def parse_readme_commands(markdown: str) -> list[list[str]]:
    commands: list[list[str]] = []
    in_shell_block = False
    for line in markdown.splitlines():
        fence = re.match(r"^\s*```([^`]*)", line)
        if fence:
            language = fence.group(1).strip().lower()
            if in_shell_block:
                in_shell_block = False
            else:
                in_shell_block = language in {"bash", "sh", "shell", "console"}
            continue
        if not in_shell_block:
            continue
        command_line = line.strip()
        if command_line.startswith("$ "):
            command_line = command_line[2:].lstrip()
        if re.match(r"^northstar(?:-[a-z0-9-]+)?(?:\s|$)", command_line):
            commands.append(shlex.split(command_line))
    return commands


def readme_commands() -> list[list[str]]:
    commands = parse_readme_commands(README_PATH.read_text(encoding="utf-8"))
    if len(commands) < 10:
        raise AssertionError(
            f"README command discovery found only {len(commands)} Northstar commands."
        )
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
    shutil.copytree(EXAMPLES_PATH, home / "examples")
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


def test_readme_command_parser_fails_closed_on_an_invalid_documented_command(
    tmp_path: Path,
) -> None:
    markdown = README_PATH.read_text(encoding="utf-8").replace(
        "$ northstar --help", "$ northstar --definitely-invalid"
    )
    commands = parse_readme_commands(markdown)
    invalid = next(args for args in commands if "--definitely-invalid" in args)
    result = run_installed_command(invalid, tmp_path)

    assert result.returncode != 0
    assert commands


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

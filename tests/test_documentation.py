from __future__ import annotations

import tempfile
from pathlib import Path

import base_cli
import pytest

from base_cli_demo.cli import command
from documentation_commands import parse_documented_commands


DOCUMENTS = (Path("README.md"), Path("docs/learning-path.md"))


def documented_commands() -> list[tuple[str, list[str]]]:
    examples: list[tuple[str, list[str]]] = []
    for document in DOCUMENTS:
        commands = parse_documented_commands(document.read_text(encoding="utf-8"))
        examples.extend((str(document), command) for command in commands)
    return examples


@pytest.mark.parametrize(
    ("document", "args"), documented_commands(), ids=lambda value: str(value)
)
def test_documented_northstar_commands_are_executable(
    document: str, args: list[str]
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = base_cli.testing.invoke(command, args[1:], home=Path(directory))

    assert result.exit_code == 0, f"{document}: {args!r}\n{result.output}"


def test_documented_dependency_windows_match_project_metadata() -> None:
    metadata = Path("pyproject.toml").read_text(encoding="utf-8")
    starter = Path("docs/use-in-your-project.md").read_text(encoding="utf-8")

    for requirement in ('"base-cli>=0.5.0,<0.6"', '"click>=8.1,<8.6"'):
        assert requirement in metadata
        assert requirement.strip('"') in starter

    yaml_guide = Path("docs/yaml-output.md").read_text(encoding="utf-8")
    assert 'python -m pip install ".[yaml]"' in yaml_guide
    assert 'base-cli-demo[yaml]' not in yaml_guide

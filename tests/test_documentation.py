from __future__ import annotations

import re
import shlex
import tempfile
from pathlib import Path

import base_cli
import pytest

from base_cli_demo.cli import command


COMMAND_PATTERN = re.compile(r"^\$\s+(northstar(?:\s+.*)?)$")
DOCUMENTS = (Path("README.md"), Path("docs/learning-path.md"))


def documented_commands() -> list[tuple[str, list[str]]]:
    examples: list[tuple[str, list[str]]] = []
    for document in DOCUMENTS:
        for line in document.read_text(encoding="utf-8").splitlines():
            match = COMMAND_PATTERN.match(line)
            if match:
                examples.append((str(document), shlex.split(match.group(1))))
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

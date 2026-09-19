"""Shared extraction of executable shell examples from Markdown documents."""

from __future__ import annotations

import re
import shlex


_FENCE_PATTERN = re.compile(r"^\s*```")
_COMMAND_PATTERN = re.compile(r"^northstar(?:-[a-z0-9-]+)?(?:\s|$)")


def parse_documented_commands(markdown: str) -> list[list[str]]:
    """Return Northstar commands from any fenced Markdown code block."""

    commands: list[list[str]] = []
    in_code_block = False
    for line in markdown.splitlines():
        if _FENCE_PATTERN.match(line):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            continue
        command_line = line.strip()
        if command_line.startswith("$ "):
            command_line = command_line[2:].lstrip()
        if _COMMAND_PATTERN.match(command_line):
            commands.append(shlex.split(command_line))
    return commands

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import base_cli
import base_cli_demo.cli as cli_module
import pytest

from base_cli_demo.cli import command


def invoke(args: list[str], home: Path) -> Any:
    return base_cli.testing.invoke(command, ["--quiet", *args], home=home)


def test_yaml_without_optional_renderer_fails_before_reconciliation_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli_module, "find_spec", lambda _name: None)
    result = invoke(["release", "reconcile", "--format", "yaml"], tmp_path)

    assert result.exit_code == 1
    assert "base-cli-demo[yaml]" in result.output
    assert list(tmp_path.rglob("last-reconciliation.json")) == []


def test_yaml_output_renders_with_the_optional_extra(tmp_path: Path) -> None:
    if importlib.util.find_spec("yaml") is None:
        pytest.skip("PyYAML is installed by the optional yaml extra")

    result = base_cli.testing.invoke(
        command,
        ["--quiet", "status", "--format", "yaml"],
        home=tmp_path,
    )

    assert result.exit_code == 0, result.output
    assert "service: orders-api" in result.stdout

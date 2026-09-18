from __future__ import annotations

import importlib.util

import base_cli
import pytest

from base_cli_demo.cli import command


def test_yaml_output_renders_with_the_optional_extra(tmp_path) -> None:
    if importlib.util.find_spec("yaml") is None:
        pytest.skip("PyYAML is installed by the optional yaml extra")

    result = base_cli.testing.invoke(
        command,
        ["--quiet", "status", "--format", "yaml"],
        home=tmp_path,
    )

    assert result.exit_code == 0, result.output
    assert "service: orders-api" in result.stdout

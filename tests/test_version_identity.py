from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import base_cli

from base_cli_demo import __version__
from version_identity import assert_versions_match


def test_source_version_matches_installed_metadata_and_cli() -> None:
    from base_cli_demo.cli import command

    expected = Path("VERSION").read_text(encoding="utf-8").strip()
    with TemporaryDirectory() as directory:
        result = base_cli.testing.invoke(
            command, ["--quiet", "--version"], home=Path(directory)
        )

    assert result.exit_code == 0, result.output
    cli_version = result.stdout.strip().rsplit(" ", maxsplit=1)[-1]
    assert_versions_match(
        expected,
        module=__version__,
        distribution=version("base-cli-demo"),
        cli=cli_version,
    )


@pytest.mark.parametrize("representation", ["tag", "wheel", "sdist", "cli"])
def test_release_gate_rejects_a_mismatched_version_representation(
    representation: str,
) -> None:
    with pytest.raises(ValueError, match="Release version mismatch"):
        assert_versions_match("0.1.0", **{representation: "0.2.0"})

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_minimal_starter_runs_with_the_installed_framework(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "examples" / "minimal_cli.py"
    environment = os.environ.copy()
    environment["BASE_CLI_CACHE_DIR"] = str(tmp_path / "cache")
    environment["HOME"] = str(tmp_path / "home")
    environment["USERPROFILE"] = str(tmp_path / "home")

    result = subprocess.run(
        [sys.executable, str(script), "--name", "Ada"],
        capture_output=True,
        cwd=tmp_path,
        env=environment,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "hello Ada"

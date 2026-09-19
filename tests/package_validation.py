"""Validate the contents and metadata of built demo distributions."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path

from version_identity import assert_versions_match, source_version


def _metadata_name(
    names: set[str], suffix: str, archive: str, *, preferred: str | None = None
) -> str:
    if preferred is not None and preferred in names:
        return preferred
    matches = sorted(name for name in names if name.endswith(suffix))
    if not matches:
        raise SystemExit(f"{archive} is missing metadata entry {suffix!r}.")
    if len(matches) > 1:
        raise SystemExit(f"{archive} contains multiple metadata entries: {matches}")
    return matches[0]


def validate(wheel_path: Path, sdist_path: Path) -> None:
    expected_version = source_version()

    with zipfile.ZipFile(wheel_path) as wheel:
        wheel_names = set(wheel.namelist())
        metadata_name = _metadata_name(
            wheel_names, ".dist-info/METADATA", wheel_path.name
        )
        wheel_metadata = Parser().parsestr(
            wheel.read(metadata_name).decode("utf-8")
        )
    required_wheel_files = {
        "base_cli_demo/__init__.py",
        "base_cli_demo/cli.py",
        "base_cli_demo/fixtures/services.json",
    }
    missing_wheel = required_wheel_files - wheel_names
    if missing_wheel:
        raise SystemExit(f"Wheel is missing: {sorted(missing_wheel)}")

    with tarfile.open(sdist_path, "r:gz") as sdist:
        sdist_names = set(sdist.getnames())
        sdist_root = sdist_path.name.removesuffix(".tar.gz")
        metadata_name = _metadata_name(
            sdist_names,
            "/PKG-INFO",
            sdist_path.name,
            preferred=f"{sdist_root}/PKG-INFO",
        )
        metadata_file = sdist.extractfile(metadata_name)
        if metadata_file is None:
            raise SystemExit(f"Unable to read source metadata entry {metadata_name!r}.")
        sdist_metadata = Parser().parsestr(
            metadata_file.read().decode("utf-8")
        )
    required_sdist_files = {
        f"{sdist_root}/README.md",
        f"{sdist_root}/pyproject.toml",
        f"{sdist_root}/VERSION",
        f"{sdist_root}/src/base_cli_demo/cli.py",
        f"{sdist_root}/src/base_cli_demo/fixtures/services.json",
    }
    missing_sdist = required_sdist_files - sdist_names
    if missing_sdist:
        raise SystemExit(f"Source distribution is missing: {sorted(missing_sdist)}")

    assert_versions_match(
        expected_version,
        **{
            "wheel metadata": wheel_metadata["Version"],
            "sdist metadata": sdist_metadata["Version"],
        },
    )
    print(f"Validated {wheel_path.name} and {sdist_path.name}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: package_validation.py WHEEL SDIST")
    validate(Path(sys.argv[1]), Path(sys.argv[2]))

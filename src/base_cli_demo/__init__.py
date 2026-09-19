"""A small, realistic consumer application for the base-cli framework."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from pathlib import Path

__all__ = ["__version__"]


def _resolve_version() -> str:
    """Use VERSION in a checkout and installed metadata in a built package."""

    checkout_root = Path(__file__).resolve().parents[2]
    version_file = checkout_root / "VERSION"
    if (checkout_root / "pyproject.toml").is_file() and version_file.is_file():
        value = version_file.read_text(encoding="utf-8").splitlines()[0].strip()
        if value:
            return value

    try:
        return distribution_version("base-cli-demo")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = _resolve_version()

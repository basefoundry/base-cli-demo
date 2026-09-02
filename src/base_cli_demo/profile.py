"""Northstar-owned configuration and profile policies."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import base_cli


@dataclass(frozen=True)
class NorthstarConfig:
    """Validated settings owned by the Northstar consumer."""

    service_owner: str | None = None
    release_version: str = "2.5.0"

    @classmethod
    def from_mapping(cls, values: object) -> NorthstarConfig:
        """Validate consumer configuration without changing lifecycle policy."""

        if not isinstance(values, Mapping):
            raise base_cli.ConfigurationError(
                "Northstar config must contain a JSON object."
            )

        unknown = sorted(set(values) - {"service_owner", "release_version"})
        if unknown:
            names = ", ".join(unknown)
            raise base_cli.ConfigurationError(
                f"Northstar config contains unsupported key(s): {names}."
            )

        service_owner = values.get("service_owner")
        if service_owner is not None:
            if not isinstance(service_owner, str) or not service_owner.strip():
                raise base_cli.ConfigurationError(
                    "Northstar config key 'service_owner' must be a non-empty string or null."
                )
            service_owner = service_owner.strip()

        release_version = values.get("release_version", cls.release_version)
        if not isinstance(release_version, str) or not release_version.strip():
            raise base_cli.ConfigurationError(
                "Northstar config key 'release_version' must be a non-empty string."
            )

        return cls(
            service_owner=service_owner,
            release_version=release_version.strip(),
        )

    def as_mapping(self) -> dict[str, Any]:
        """Return normalized consumer settings exposed through Context."""

        return {
            "service_owner": self.service_owner,
            "release_version": self.release_version,
        }


def _load_json(path: Path) -> dict[str, Any]:
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise base_cli.ConfigurationError(
            f"Unable to read Northstar config file '{path}': {exc}"
        ) from exc

    try:
        payload = json.loads(contents)
    except json.JSONDecodeError as exc:
        raise base_cli.ConfigurationError(
            f"Northstar config file '{path}' contains invalid JSON: {exc.msg}."
        ) from exc

    if not isinstance(payload, Mapping):
        raise base_cli.ConfigurationError(
            f"Northstar config file '{path}' must contain a JSON object."
        )
    return dict(payload)


def load_config(
    _project: base_cli.ProjectInfo | None,
    explicit_path: Path | None,
) -> base_cli.ConfigSnapshot:
    """Load optional explicit consumer config and preserve field provenance."""

    raw = _load_json(explicit_path) if explicit_path is not None else {}
    config = NorthstarConfig.from_mapping(raw)
    provenance = {
        key: "explicit" if key in raw else "consumer-default"
        for key in config.as_mapping()
    }
    return base_cli.ConfigSnapshot(
        config=config.as_mapping(),
        framework=base_cli.FrameworkConfig(),
        provenance=provenance,
    )


def northstar_profile() -> base_cli.CliProfile:
    """Build the explicit generic-lifecycle profile used by Northstar."""

    return base_cli.CliProfile.generic(load_config=load_config)


def get_config(context: base_cli.Context[Any, Any, Any]) -> NorthstarConfig:
    """Return validated consumer settings from an active invocation."""

    return NorthstarConfig.from_mapping(context.config)

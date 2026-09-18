"""Shared assertion for the release version identity test and package gate."""

from __future__ import annotations


def assert_versions_match(expected: str, **representations: str) -> None:
    """Fail with all conflicting representations instead of choosing one."""

    mismatches = {
        source: value
        for source, value in representations.items()
        if value != expected
    }
    if not expected or mismatches:
        raise ValueError(
            f"Release version mismatch: expected {expected!r}; "
            f"conflicting representations: {mismatches}."
        )

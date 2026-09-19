"""Verify VERSION, the release tag, and the requested release version agree."""

from __future__ import annotations

import os

from version_identity import assert_versions_match, source_version


def main() -> None:
    expected = os.environ.get("RELEASE_VERSION", "")
    ref_type = os.environ.get("GITHUB_REF_TYPE", "")
    ref_name = os.environ.get("GITHUB_REF_NAME", "")
    if not expected and ref_type == "tag":
        expected = ref_name.removeprefix("v")
    if not expected:
        raise SystemExit("RELEASE_VERSION or a v-prefixed release tag is required.")

    representations = {"VERSION": source_version()}
    if ref_type == "tag":
        representations["tag"] = ref_name.removeprefix("v")
    assert_versions_match(expected, **representations)
    print(f"Validated release version {expected}.")


if __name__ == "__main__":
    main()

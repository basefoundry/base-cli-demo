#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=tests python tests/verify_release_version.py

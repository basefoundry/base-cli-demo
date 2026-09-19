from __future__ import annotations

import json
import stat
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import base_cli
import base_cli_demo.cli as cli_module

from base_cli_demo.cli import command


def invoke(args: list[str], home: Path) -> Any:
    return base_cli.testing.invoke(command, ["--quiet", *args], home=home)


def test_help_exposes_nested_consumer_commands_and_lifecycle_options() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(["--help"], Path(directory))

    assert result.exit_code == 0, result.output
    assert "status" in result.stdout
    assert "release" in result.stdout
    assert "--environment" in result.stdout
    assert "--dry-run" in result.stdout


def test_cli_version_matches_the_installed_package_metadata() -> None:
    from importlib.metadata import version

    from base_cli_demo import __version__

    with tempfile.TemporaryDirectory() as directory:
        result = invoke(["--version"], Path(directory))

    assert result.exit_code == 0, result.output
    assert __version__ == version("base-cli-demo")
    assert __version__ in result.stdout


def test_status_reads_the_selected_local_fixture_environment() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            ["--environment", "dev", "status", "--format", "json"], Path(directory)
        )

    assert result.exit_code == 0, result.output
    records = json.loads(result.stdout)
    assert [record["service"] for record in records] == [
        "orders-api",
        "billing-worker",
        "web",
    ]
    assert records[-1]["status"] == "degraded"


def test_release_plan_is_nested_and_machine_readable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            [
                "--environment",
                "staging",
                "release",
                "plan",
                "--service",
                "orders-api",
                "--version",
                "2.5.0",
                "--format",
                "json",
            ],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {
            "environment": "staging",
            "service": "orders-api",
            "current_version": "2.3.9",
            "target_version": "2.5.0",
            "action": "update",
        }
    ]


def test_reconcile_dry_run_reports_no_external_changes() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            [
                "--environment",
                "dev",
                "--dry-run",
                "release",
                "reconcile",
                "--version",
                "2.5.0",
                "--format",
                "json",
            ],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {
            "environment": "dev",
            "services": 3,
            "target_version": "2.5.0",
            "action": "would-reconcile",
            "external_changes": False,
        }
    ]


def test_reconcile_dry_run_does_not_persist_consumer_state() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        result = invoke(
            ["--dry-run", "release", "reconcile", "--format", "json"],
            root,
        )

        assert result.exit_code == 0, result.output
        assert list(root.rglob("last-reconciliation.json")) == []


def test_reconcile_persists_state_and_cleans_temporary_input() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        result = invoke(
            ["release", "reconcile", "--format", "json"],
            root,
        )

        assert result.exit_code == 0, result.output
        state_files = list(root.rglob("last-reconciliation.json"))
        assert len(state_files) == 1
        assert (
            json.loads(state_files[0].read_text(encoding="utf-8"))["action"]
            == "reconciled"
        )
        assert list(root.rglob("reconciliation-input.json")) == []


def test_reconcile_preserves_existing_snapshot_permissions() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = invoke(["release", "reconcile"], root)
        assert first.exit_code == 0, first.output
        state_path = next(root.rglob("last-reconciliation.json"))
        os_mode = 0o640
        state_path.chmod(os_mode)

        second = invoke(["release", "reconcile", "--version", "2.6.0"], root)

        assert second.exit_code == 0, second.output
        assert stat.S_IMODE(state_path.stat().st_mode) == os_mode


def test_failed_atomic_replace_preserves_the_previous_snapshot(
    monkeypatch: Any,
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = invoke(["release", "reconcile", "--version", "2.6.0"], root)
        assert first.exit_code == 0, first.output
        state_path = next(root.rglob("last-reconciliation.json"))
        previous = state_path.read_bytes()

        def fail_replace(_staged_path: Path, _state_path: Path) -> None:
            raise OSError("simulated replace failure")

        monkeypatch.setattr(cli_module, "_replace_state", fail_replace)
        failed = invoke(["release", "reconcile", "--version", "2.7.0"], root)

        assert failed.exit_code == 1
        assert "previous snapshot was left unchanged" in failed.output
        assert state_path.read_bytes() == previous
        assert not list(state_path.parent.glob(f".{state_path.name}.*.tmp"))


def test_serialization_failure_preserves_the_previous_snapshot(monkeypatch: Any) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = invoke(["release", "reconcile"], root)
        assert first.exit_code == 0, first.output
        state_path = next(root.rglob("last-reconciliation.json"))
        previous = state_path.read_bytes()

        def fail_serialization(_record: Any) -> str:
            raise TypeError("simulated serialization failure")

        monkeypatch.setattr(cli_module, "_serialize_reconciliation", fail_serialization)
        failed = invoke(["release", "reconcile", "--version", "2.7.0"], root)

        assert failed.exit_code == 1
        assert state_path.read_bytes() == previous


def test_concurrent_public_reconciliations_leave_a_complete_snapshot() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        initial = invoke(["release", "reconcile"], root)
        assert initial.exit_code == 0, initial.output
        state_path = next(root.rglob("last-reconciliation.json"))
        stop_reader = threading.Event()
        reader_errors: list[BaseException] = []

        def read_while_writing() -> None:
            while not stop_reader.is_set():
                try:
                    json.loads(state_path.read_text(encoding="utf-8"))
                except BaseException as exc:  # captured for assertion in the test thread
                    reader_errors.append(exc)
                    stop_reader.set()

        with ThreadPoolExecutor(max_workers=5) as pool:
            reader = pool.submit(read_while_writing)
            futures = [
                pool.submit(
                    invoke,
                    ["release", "reconcile", "--version", f"2.{minor}.0"],
                    root,
                )
                for minor in range(8, 12)
            ]
            results = [future.result() for future in futures]
            stop_reader.set()
            reader.result()

        assert not reader_errors
        assert all(result.exit_code == 0 for result in results)
        final = json.loads(state_path.read_text(encoding="utf-8"))
        assert final["action"] == "reconciled"
        assert final["target_version"] in {f"2.{minor}.0" for minor in range(8, 12)}


def test_json_error_envelope_preserves_nonzero_exit_status() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            ["--json", "--environment", "unknown", "status"],
            Path(directory),
        )

    assert result.exit_code != 0
    payload = json.loads(result.stdout)
    assert payload["schema"] == "base-cli.error"
    assert payload["type"] == "error"
    assert payload["details"]["exit_code"] == result.exit_code


def test_debug_log_file_redacts_sensitive_adapter_argument() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        log_path = root / "northstar.log"
        secret = "demo-secret"
        result = base_cli.testing.invoke(
            command,
            [
                "--debug",
                "--log-file",
                str(log_path),
                "release",
                "reconcile",
                "--approval-token",
                secret,
            ],
            home=root / "home",
        )

        assert result.exit_code == 0, result.output
        log_text = log_path.read_text(encoding="utf-8")

    assert secret not in log_text
    assert "[REDACTED]" in log_text


def test_json_lifecycle_envelope_is_available_to_consumers() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            ["--environment", "dev", "--json", "status", "--format", "json"],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["schema"] == "base-cli.output"
    assert payload["code"] == "ok"
    assert '"orders-api"' in payload["details"]["stdout"]


def test_default_consumer_config_reports_its_own_provenance() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(["config", "show", "--format", "json"], Path(directory))

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {
            "setting": "service_owner",
            "value": None,
            "source": "consumer-default",
        },
        {
            "setting": "release_version",
            "value": "2.5.0",
            "source": "consumer-default",
        },
    ]


def test_explicit_consumer_config_filters_and_sets_release_default() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        config_path = root / "northstar.json"
        config_path.write_text(
            '{"service_owner": "commerce", "release_version": "2.6.0"}',
            encoding="utf-8",
        )
        result = invoke(
            [
                "--config",
                str(config_path),
                "release",
                "plan",
                "--format",
                "json",
            ],
            root / "home",
        )

    assert result.exit_code == 0, result.output
    records = json.loads(result.stdout)
    assert [record["service"] for record in records] == ["orders-api", "web"]
    assert {record["target_version"] for record in records} == {"2.6.0"}


def test_release_version_override_uses_the_config_non_empty_string_policy() -> None:
    for command_name in ("plan", "reconcile"):
        with tempfile.TemporaryDirectory() as directory:
            result = invoke(
                ["release", command_name, "--version", "   "], Path(directory)
            )

        assert result.exit_code == 2
        assert "non-empty string" in result.output
        assert "Traceback" not in result.output


def test_release_version_override_preserves_arbitrary_non_empty_strings() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = invoke(
            ["release", "plan", "--version", "  release candidate  ", "--format", "json"],
            Path(directory),
        )

    assert result.exit_code == 0, result.output
    assert {row["target_version"] for row in json.loads(result.stdout)} == {
        "release candidate"
    }


def test_invalid_utf8_config_is_a_safe_configuration_error() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        config_path = root / "invalid-encoding.json"
        config_path.write_bytes(b'{"release_version":"\xff"}')
        result = invoke(["--config", str(config_path), "status"], root / "home")

    assert result.exit_code == 2
    assert "as UTF-8" in result.output
    assert "Traceback" not in result.output


def test_config_release_version_uses_the_same_non_empty_string_policy() -> None:
    for invalid in ("", "   "):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "invalid-version.json"
            config_path.write_text(
                json.dumps({"release_version": invalid}), encoding="utf-8"
            )
            result = invoke(
                ["--config", str(config_path), "release", "plan"], root / "home"
            )

        assert result.exit_code == 2
        assert "non-empty string" in result.output
        assert "Traceback" not in result.output


def test_invalid_consumer_config_is_a_safe_configuration_error() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        config_path = root / "invalid.json"
        config_path.write_text('{"service_owner": 42}', encoding="utf-8")
        result = invoke(
            ["--config", str(config_path), "status"],
            root / "home",
        )

    assert result.exit_code == 2
    assert "service_owner" in result.output
    assert "Traceback" not in result.output

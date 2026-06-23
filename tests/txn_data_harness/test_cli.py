"""Tests for the composable Transaction Data Harness CLI."""

from __future__ import annotations

import json

from scripts.txn_data_harness import cli
from scripts.txn_data_harness.manifests import write_manifest
from scripts.txn_data_harness.models import Manifest


def test_plan_delegates_to_generate_with_dry_run(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr("scripts.txn_data_harness.cli.generate.main", lambda argv: calls.append(argv) or 0)

    exit_code = cli.main(["plan", "--org", "sf-alias", "--config", "config.yaml", "-vv"])

    assert exit_code == 0
    assert calls == [[
        "--org", "sf-alias",
        "--config", "config.yaml",
        "--api-version", "67.0",
        "--transport", "requests",
        "--concurrency", "4",
        "--poll-timeout", "180",
        "--max-retries", "2",
        "--dry-run",
        "-vv",
    ]]


def test_run_delegates_to_generate_without_dry_run(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr("scripts.txn_data_harness.cli.generate.main", lambda argv: calls.append(argv) or 0)

    exit_code = cli.main(["run", "--org", "sf-alias", "--count", "2", "--with-opportunity"])

    assert exit_code == 0
    assert "--dry-run" not in calls[0]
    assert "--with-opportunity" in calls[0]
    assert calls[0][0:2] == ["--org", "sf-alias"]


def test_inspect_manifest_path_prints_summary(tmp_path, capsys) -> None:
    path = write_manifest(
        Manifest(run_id="DEMO-1", account_name="Infinitech", reached_stage="quote"),
        manifest_dir=tmp_path,
    )

    exit_code = cli.main(["inspect", "--manifest", str(path)])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["run_id"] == "DEMO-1"
    assert payload["account"] == "Infinitech"
    assert payload["reached_stage"] == "quote"


def test_inspect_latest_uses_newest_manifest(tmp_path, monkeypatch, capsys) -> None:
    old = write_manifest(Manifest(run_id="DEMO-OLD"), manifest_dir=tmp_path)
    new = write_manifest(Manifest(run_id="DEMO-NEW"), manifest_dir=tmp_path)
    monkeypatch.setattr("scripts.txn_data_harness.cli.list_manifests", lambda: [new, old])

    exit_code = cli.main(["inspect", "--latest"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["run_id"] == "DEMO-NEW"


def test_step_reports_missing_account_without_org_calls(tmp_path, monkeypatch, capsys) -> None:
    path = write_manifest(Manifest(run_id="DEMO-1", reached_stage="quote"), manifest_dir=tmp_path)
    monkeypatch.setattr(
        "scripts.txn_data_harness.cli.SfRestClient.from_alias",
        lambda *_args, **_kwargs: object(),
    )

    exit_code = cli.main([
        "step",
        "--org", "sf-alias",
        "--manifest", str(path),
        "--to-stage", "order",
    ])

    assert exit_code == 1
    assert "requires --account" in capsys.readouterr().err

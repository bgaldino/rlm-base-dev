"""`cli quote-to-cash`: run to payment_applied, then verify; and its CCI wrapper."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from scripts.txn_data_harness import cli
from scripts.txn_data_harness.config import load_scenarios
from scripts.txn_data_harness.models import Manifest

REPO = Path(__file__).resolve().parents[2]
INV = "3ttWt0000000001"
PAY = "0a8Wt0000000001"
# What the verifier reads them as: 18 characters with the case suffix.
EXPECTED = (cli.billing_verify._check_ids([INV], "invoice"),
            cli.billing_verify._check_ids([PAY], "payment"))


def _manifest(run_id="DEMO-1", stage="payment_applied", error=None) -> Manifest:
    return Manifest(run_id=run_id, reached_stage=stage, error=error)


@pytest.fixture
def harness(monkeypatch, tmp_path):
    """Fake generator, manifest files and verify; record what was called."""
    state = {"argv": None, "batch": [_manifest()], "code": 0, "fetched": None,
             "report": {"ok": True, "checked": 2, "skipped": 0, "results": []}}

    def fake_main(argv, on_batch=None):
        state["argv"] = argv
        if state["batch"] is not None and on_batch is not None:
            on_batch(object(), list(state["batch"]))
        return state["code"]

    def fake_path(run_id):
        path = tmp_path / f"{run_id}.json"
        if not path.exists():
            path.write_text(json.dumps({"run_id": run_id, "invoice_id": INV,
                                        "payment_ids": [PAY]}))
        return path

    def fake_fetch(client, invoice_ids, payment_ids):
        state["fetched"] = (invoice_ids, payment_ids)
        return {}

    monkeypatch.setattr(cli.generate, "main", fake_main)
    monkeypatch.setattr(cli, "manifest_path", fake_path)
    monkeypatch.setattr(cli.SfRestClient, "from_alias", classmethod(lambda c, *a, **k: object()))
    monkeypatch.setattr(cli.billing_verify, "fetch_records", fake_fetch)
    monkeypatch.setattr(cli.billing_verify, "run_checks", lambda records, level="auto": state["report"])
    monkeypatch.setattr(cli.billing_verify, "render_text", lambda report: "RESULT: stub")
    return state


def test_pass_runs_serially_and_verifies_the_recorded_ids(harness, capsys):
    assert cli.main(["quote-to-cash", "--org", "x"]) == 0
    argv = harness["argv"]
    assert argv[argv.index("--concurrency") + 1] == "1"
    assert argv[argv.index("--config") + 1] == str(cli.QUOTE_TO_CASH_CONFIG)
    assert harness["fetched"] == EXPECTED
    assert "QUOTE-TO-CASH: pass (1 scenario(s) at payment_applied: DEMO-1)" in capsys.readouterr().out


def test_a_short_stage_fails_without_verifying(harness, capsys):
    harness["batch"] = [_manifest(stage="invoice_posted")]
    assert cli.main(["quote-to-cash", "--org", "x"]) == 1
    out = capsys.readouterr().out
    assert "FAIL: DEMO-1 reached invoice_posted, not payment_applied" in out
    assert harness["fetched"] is None


def test_a_failed_scenario_fails_with_its_error(harness, capsys):
    harness["batch"] = [_manifest(stage="invoice_posted", error="boom")]
    harness["code"] = 1
    assert cli.main(["quote-to-cash", "--org", "x"]) == 1
    assert "FAIL: DEMO-1 reached invoice_posted, not payment_applied: boom" in capsys.readouterr().out


def test_a_nonzero_run_fails_even_when_every_stage_was_reached(harness):
    harness["code"] = 1
    assert cli.main(["quote-to-cash", "--org", "x"]) == 1
    assert harness["fetched"] is None


def test_a_run_that_never_started_returns_its_code(harness, capsys):
    harness["batch"] = None
    harness["code"] = 3
    assert cli.main(["quote-to-cash", "--org", "x"]) == 3
    assert "the run did not start (exit 3)" in capsys.readouterr().err


def test_a_failed_check_fails(harness, capsys):
    harness["report"] = {"ok": False, "checked": 2, "skipped": 0, "results": []}
    assert cli.main(["quote-to-cash", "--org", "x"]) == 1
    assert "a balance check failed" in capsys.readouterr().out


def test_nothing_checked_is_a_failure(harness, capsys):
    harness["report"] = {"ok": True, "checked": 0, "skipped": 3, "results": []}
    assert cli.main(["quote-to-cash", "--org", "x"]) == 1
    assert "no balance was checked" in capsys.readouterr().out


def test_a_verify_error_is_exit_2(harness, monkeypatch, capsys):
    def refused(*_a, **_k):
        raise cli.SfApiError(401, '[{"errorCode": "INVALID_SESSION_ID"}]', "GET", "/query")
    monkeypatch.setattr(cli.billing_verify, "fetch_records", refused)
    assert cli.main(["quote-to-cash", "--org", "x"]) == 2
    assert "quote-to-cash verify: Salesforce request failed" in capsys.readouterr().err


def test_ids_are_deduplicated_across_scenarios(harness):
    harness["batch"] = [_manifest("DEMO-1-001"), _manifest("DEMO-1-002")]
    assert cli.main(["quote-to-cash", "--org", "x"]) == 0
    assert harness["fetched"] == EXPECTED


def test_shipped_config_targets_payment_applied_with_settlement():
    specs = load_scenarios(cli.generate.parse_args(
        ["--org", "x", "--config", str(cli.QUOTE_TO_CASH_CONFIG)]))
    assert specs and all(s.target_stage == "payment_applied" for s in specs)
    assert all(s.settlement is not None for s in specs)


def _task_module():
    spec = importlib.util.spec_from_file_location(
        "rlm_quote_to_cash", REPO / "tasks" / "rlm_quote_to_cash.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_task_runs_the_harness_command_with_the_username():
    task = _task_module()
    assert task.harness_command("py", "u@example.com") == [
        "py", "-m", "scripts.txn_data_harness.cli", "quote-to-cash", "--org", "u@example.com"]
    assert task.harness_command("py", "u@example.com", "a.yaml")[-2:] == ["--config", "a.yaml"]


def test_task_command_parses_as_the_cli_subcommand():
    task = _task_module()
    cmd = task.harness_command(sys.executable, "u@example.com", "a.yaml")
    args = cli.parse_args(cmd[3:])
    assert args.func is cli._cmd_quote_to_cash
    assert args.org == "u@example.com" and str(args.config) == "a.yaml"

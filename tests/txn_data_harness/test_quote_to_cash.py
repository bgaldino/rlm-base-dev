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
    err = capsys.readouterr().err
    assert "quote-to-cash verify: Salesforce request failed" in err
    # The run completed: the error names its runs and the verify, not a new run.
    assert "The batch ran (DEMO-1)" in err and "cli verify --manifest" in err


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


def test_an_error_in_the_run_is_exit_2_not_a_verdict(harness, monkeypatch, capsys):
    def no_sf(argv, on_batch=None):
        raise FileNotFoundError(2, "No such file or directory", "sf")
    monkeypatch.setattr(cli.generate, "main", no_sf)
    assert cli.main(["quote-to-cash", "--org", "x"]) == 2
    captured = capsys.readouterr()
    assert "quote-to-cash run: the sf CLI was not found on PATH" in captured.err
    assert "QUOTE-TO-CASH" not in captured.out


def test_a_config_not_targeting_payment_applied_is_refused_before_any_write(
        harness, tmp_path, capsys):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("defaults: {kind: sales_txn_quote}\n"
                   "scenarios:\n  - {account: Infinitech, target_stage: invoice_posted}\n")
    assert cli.main(["quote-to-cash", "--org", "x", "--config", str(cfg)]) == 4
    assert harness["argv"] is None  # the generator never ran
    assert "must target payment_applied, not invoice_posted" in capsys.readouterr().err


def test_an_unreadable_config_is_exit_4(harness, tmp_path, capsys):
    assert cli.main(["quote-to-cash", "--org", "x", "--config", str(tmp_path / "none.yaml")]) == 4
    assert harness["argv"] is None
    assert "bad config" in capsys.readouterr().err


def test_generate_hands_the_batch_manifests_to_on_batch(monkeypatch, tmp_path) -> None:
    """The real generate.main calls on_batch with every scenario's manifest."""
    from types import SimpleNamespace

    from scripts.txn_data_harness import generate
    from scripts.txn_data_harness.runner import BatchResult

    spec = SimpleNamespace(count=1, kind="sales_txn_quote", target_stage="payment_applied")
    resolved = SimpleNamespace(account=SimpleNamespace(id="001A", name="Infinitech"),
                               spec=spec, effective_stage="payment_applied")
    manifest = _manifest()
    result = BatchResult(base_run_id="DEMO-1", total=1, failures=0, manifest_dir=tmp_path)

    def fake_run_batch(client, ctx, specs, *, on_start, on_complete, **_kw):
        on_start("DEMO-1", 1, 1)
        on_complete(1, 1, manifest, tmp_path / "DEMO-1.json")
        return result

    monkeypatch.setattr(generate.SfRestClient, "from_alias", lambda *a, **kw: object())
    monkeypatch.setattr(generate, "discover", lambda *a, **kw: object())
    monkeypatch.setattr(generate, "load_scenarios", lambda args: [spec])
    monkeypatch.setattr(generate, "SCENARIO_HANDLERS",
                        {"sales_txn_quote": SimpleNamespace(resolve=lambda c, x, s: resolved)})
    monkeypatch.setattr(generate, "run_batch", fake_run_batch)
    monkeypatch.setattr(generate, "write_batch_report",
                        lambda report, d: (d / "r.json", d / "r.md"))
    seen = []
    assert generate.main(["--org", "o", "--concurrency", "1"],
                         on_batch=lambda r, ms: seen.append((r, ms))) == 0
    assert seen == [(result, [manifest])]


def test_a_malformed_config_value_is_exit_4_not_a_traceback(harness, tmp_path, capsys):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("defaults: {kind: sales_txn_quote, target_stage: [payment_applied]}\n"
                   "scenarios:\n  - {account: Infinitech}\n")
    assert cli.main(["quote-to-cash", "--org", "x", "--config", str(cfg)]) == 4
    assert harness["argv"] is None
    assert "bad config" in capsys.readouterr().err


@pytest.mark.parametrize("returncode", [0, 1, 2])
def test_task_raises_on_a_nonzero_exit(monkeypatch, returncode):
    from types import SimpleNamespace

    task_module = _task_module()
    calls = []

    def fake_run(cmd, cwd):
        calls.append((cmd, cwd))
        return SimpleNamespace(returncode=returncode)

    monkeypatch.setattr(task_module.subprocess, "run", fake_run)
    task = task_module.VerifyQuoteToCash.__new__(task_module.VerifyQuoteToCash)
    task.org_config = SimpleNamespace(username="u@example.com")
    task.project_config = SimpleNamespace(repo_root="/repo")
    task.options = {}
    task.logger = SimpleNamespace(info=lambda *a, **k: None)
    if returncode:
        with pytest.raises(task_module.CommandException, match=f"exit {returncode}"):
            task._run_task()
    else:
        task._run_task()
    cmd, cwd = calls[0]
    assert cwd == "/repo" and cmd[-2:] == ["--org", "u@example.com"]


def test_settlement_warnings_are_printed(harness, capsys):
    m = _manifest()
    m.settlement_warnings = ["invoice already had applications before settlement"]
    harness["batch"] = [m]
    assert cli.main(["quote-to-cash", "--org", "x"]) == 0
    assert "WARNING: DEMO-1: invoice already had applications" in capsys.readouterr().out


def test_connection_options_reach_the_run(harness):
    assert cli.main(["quote-to-cash", "--org", "x", "--api-version", "67.0",
                     "--transport", "cli", "--poll-timeout", "30", "-vv"]) == 0
    argv = harness["argv"]
    for flag, value in (("--api-version", "67.0"), ("--transport", "cli"),
                        ("--poll-timeout", "30")):
        assert argv[argv.index(flag) + 1] == value
    assert "-vv" in argv


@pytest.mark.parametrize("stage, credit_later, payment_later", [
    ("payment_applied", False, False),
    ("credit_applied", False, True),
    ("invoice_posted", True, True),
])
def test_plan_marks_settlement_parts_the_run_does_not_reach(
        capsys, stage, credit_later, payment_later):
    from scripts.txn_data_harness import generate
    from scripts.txn_data_harness.config import CreditSpec, PaymentSpec, SettlementSpec

    generate._print_settlement(
        SettlementSpec(application_level="auto", credit=CreditSpec(amount=5.0),
                       payment=PaymentSpec()), stage)
    out = capsys.readouterr().out.splitlines()
    credit = next(line for line in out if "credit   :" in line)
    payment = next(line for line in out if "payment  :" in line)
    assert ("not reached" in credit) is credit_later
    assert ("not reached" in payment) is payment_later


@pytest.mark.parametrize("ids, missing", [
    ({}, "credit memo or payment"),
    ({"credit_memo_ids": ["50g1"]}, "payment"),
    ({"payment_ids": ["0a8P"]}, "credit memo"),
])
def test_a_run_that_wrote_no_credit_or_payment_fails(harness, capsys, ids, missing):
    """Posting can settle the invoice with an earlier payment; the stages then
    advance without writing, which proves nothing about this run."""
    m = _manifest()
    m.settlement = {"application_level": "auto", "credit": {"percent": 10.0},
                    "payment": {"amount": "exact"}}
    m.credit_memo_ids = ids.get("credit_memo_ids", [])
    m.payment_ids = ids.get("payment_ids", [])
    m.settlement_warnings = ["payment skipped: no open balance"]
    harness["batch"] = [m]
    assert cli.main(["quote-to-cash", "--org", "x"]) == 1
    out = capsys.readouterr().out
    assert f"FAIL: DEMO-1 created no {missing}" in out
    assert harness["fetched"] is None


def test_a_run_with_its_own_credit_and_payment_passes(harness):
    m = _manifest()
    m.settlement = {"application_level": "auto", "credit": {"percent": 10.0},
                    "payment": {"amount": "exact"}}
    m.credit_memo_ids, m.payment_ids = ["50g1"], ["0a8P"]
    harness["batch"] = [m]
    assert cli.main(["quote-to-cash", "--org", "x"]) == 0


def test_a_payment_only_block_needs_only_its_payment(harness):
    m = _manifest()
    m.settlement = {"application_level": "auto", "payment": {"amount": "exact"}}
    m.payment_ids = ["0a8P"]
    harness["batch"] = [m]
    assert cli.main(["quote-to-cash", "--org", "x"]) == 0


def test_an_error_after_the_batch_names_its_runs(harness, monkeypatch, capsys):
    def report_write_fails(argv, on_batch=None):
        on_batch(object(), [_manifest()])
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(cli.generate, "main", report_write_fails)
    assert cli.main(["quote-to-cash", "--org", "x"]) == 2
    err = capsys.readouterr().err
    assert "quote-to-cash run: could not run a command or read a file" in err
    assert "The batch ran (DEMO-1)" in err


@pytest.mark.parametrize("stage, warned", [("payment_applied", True), ("credit_applied", False)])
def test_plan_warns_of_an_over_payment_only_when_the_run_pays(capsys, stage, warned):
    from scripts.txn_data_harness import generate
    from scripts.txn_data_harness.config import CreditSpec, PaymentSpec, SettlementSpec

    generate._print_settlement(
        SettlementSpec(application_level="auto", credit=CreditSpec(amount=5.0),
                       payment=PaymentSpec(percent=150.0)), stage)
    assert ("over-payment" in capsys.readouterr().out) is warned

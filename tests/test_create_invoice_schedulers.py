"""Offline tests for create_invoice_schedulers (tasks.rlm_billing.CreateInvoiceSchedulers, todo 379)."""
import importlib
import json
import logging
import sys
import types
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import repo `tasks.*` modules before cumulusci: its project_config empties tasks.__path__.
import tasks.soql_utils  # noqa: E402,F401

PLAN_JSON = REPO / "datasets/sfdmu/qb/en-US/qb-billing/InvoiceSchedulers.json"
OPTION_KEYS = {
    "shouldCatchUpBillRun",
    "targetDayOfMonth",
    "targetMonthOffset",
    "billingCycleCount",
    "shouldGenerateInvoiceDocuments",
}


def _module():
    sys.modules["tasks"].__path__ = [str(REPO / "tasks")]
    return importlib.import_module("tasks.rlm_billing")


def _task(plan_dir, existing=()):
    mod = _module()
    task = mod.CreateInvoiceSchedulers.__new__(mod.CreateInvoiceSchedulers)
    task.options = {"plan_dir": str(plan_dir)}
    task.org_config = types.SimpleNamespace(access_token="t", instance_url="https://x.my.salesforce.com")
    task.project_config = types.SimpleNamespace(project__package__api_version="68.0")
    task.logger = logging.getLogger("test_create_invoice_schedulers")
    task.sf = types.SimpleNamespace(
        query_all=lambda soql: {"records": [{"BillingSchedulerName": n} for n in existing]}
    )
    return task


class _Resp:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


def _capture_posts(monkeypatch, status_code=201):
    import requests

    posts = []

    def fake_post(url, headers=None, json=None, timeout=None):
        posts.append((url, json))
        return _Resp(status_code, '{"billingBatchScheduler":{"id":"5BS"}}')

    monkeypatch.setattr(requests, "post", fake_post)
    return posts


def test_body_is_always_inactive_and_never_starts_a_run():
    mod = _module()
    entry = {
        "schedulerName": "S",
        "status": "Active",
        "frequencyCadence": "Monthly",
        "frequencyCadenceOptions": {"shouldStartRunImmediately": True, "recursOnDate": "1"},
    }
    body = mod.build_invoice_scheduler_body(entry, "2026-12-01")
    assert body["status"] == "Inactive"
    assert body["startDate"] == "2026-12-01"
    assert body["frequencyCadenceOptions"] == {"recursOnDate": "1"}
    assert "targetDate" not in body
    # the entry itself is not changed
    assert entry["status"] == "Active"
    assert entry["frequencyCadenceOptions"]["shouldStartRunImmediately"] is True


def test_once_scheduler_gets_the_start_date_as_target_date_only_when_it_has_none():
    mod = _module()
    once = {"schedulerName": "S", "frequencyCadence": "Once", "frequencyCadenceOptions": {}}
    assert mod.build_invoice_scheduler_body(once, "2026-12-01")["targetDate"] == "2026-12-01"
    dated = dict(once, targetDate="2026-10-31")
    assert mod.build_invoice_scheduler_body(dated, "2026-12-01")["targetDate"] == "2026-10-31"


def test_start_date_is_the_next_utc_day():
    mod = _module()
    assert mod.scheduler_start_date(date(2026, 12, 31)) == "2027-01-01"


def test_shipped_samples_cover_each_264_option_once():
    entries = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    names = [e["schedulerName"] for e in entries]
    assert len(names) == len(set(names)) == 4
    for e in entries:
        # status and start date come from the task, never the file
        assert "status" not in e and "startDate" not in e, e["schedulerName"]
    used = {k: [e["schedulerName"] for e in entries if k in e] for k in OPTION_KEYS}
    assert all(len(v) == 1 for v in used.values()), used
    # target day of month and month offset are one sample
    assert used["targetDayOfMonth"] == used["targetMonthOffset"]
    catch_up = next(e for e in entries if e.get("shouldCatchUpBillRun"))
    # the API refuses these on a catch-up scheduler and requires Once
    assert "invoiceStatus" not in catch_up and "invoiceDate" not in catch_up
    assert catch_up["frequencyCadence"] == "Once"


def test_run_creates_missing_samples_and_skips_existing(monkeypatch, tmp_path):
    entries = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    (tmp_path / "InvoiceSchedulers.json").write_text(json.dumps(entries))
    posts = _capture_posts(monkeypatch)
    _task(tmp_path, existing=[entries[0]["schedulerName"]])._run_task()
    assert [b["schedulerName"] for _, b in posts] == [e["schedulerName"] for e in entries[1:]]
    for url, body in posts:
        assert url == "https://x.my.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-schedulers"
        assert body["status"] == "Inactive"


def test_rerun_creates_nothing(monkeypatch, tmp_path):
    entries = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    (tmp_path / "InvoiceSchedulers.json").write_text(json.dumps(entries))
    posts = _capture_posts(monkeypatch)
    _task(tmp_path, existing=[e["schedulerName"] for e in entries])._run_task()
    assert posts == []


def test_a_refused_create_fails_the_task(monkeypatch, tmp_path):
    (tmp_path / "InvoiceSchedulers.json").write_text(json.dumps([{"schedulerName": "S"}]))
    _capture_posts(monkeypatch, status_code=403)
    with pytest.raises(Exception, match="1 scheduler creation"):
        _task(tmp_path)._run_task()


def test_missing_data_file_fails_the_task(tmp_path):
    with pytest.raises(Exception, match="InvoiceSchedulers.json not found"):
        _task(tmp_path)._run_task()


def test_wired_into_prepare_billing_behind_the_billing_flag():
    data = yaml.safe_load((REPO / "cumulusci.yml").read_text(encoding="utf-8"))
    assert data["tasks"]["create_invoice_schedulers"]["class_path"] == "tasks.rlm_billing.CreateInvoiceSchedulers"
    steps = [s for s in data["flows"]["prepare_billing"]["steps"].values()
             if s.get("task") == "create_invoice_schedulers"]
    assert len(steps) == 1
    assert "project_config.project__custom__billing" in steps[0]["when"]

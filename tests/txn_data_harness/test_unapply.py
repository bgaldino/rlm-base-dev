"""`cli unapply` and the unapply lifecycle calls (todo 490), offline.

The fake org answers the reads `cli unapply` sends and the two unapply actions,
with the shapes measured live on 264 (Line Level): the original row keeps Type
Applied and turns UnappliedStatus Yes; a new Type Unapplied row points at it; a
second unapply of the same row is refused with HTTP 400.
"""

from __future__ import annotations

import json
import re

import pytest

from scripts.txn_data_harness import cli, lifecycle
from scripts.txn_data_harness.auth import SfApiError
from scripts.txn_data_harness.models import Manifest

PAY_ROW, CREDIT_ROW, PAYMENT = "1AlROW0000000001AA", "4sGROW0000000001AA", "0aQPAY0000000001AA"


class UnapplyOrg:
    api_version = "68.0"

    def __init__(self):
        self.rows = {
            PAY_ROW: {"Id": PAY_ROW, "Amount": 445.5, "Type": "Applied",
                      "UnappliedStatus": "No", "PaymentId": PAYMENT, "_obj": "payment"},
            CREDIT_ROW: {"Id": CREDIT_ROW, "Amount": 49.5, "Type": "Applied",
                         "UnappliedStatus": "No", "CreditMemoLineId": "9yxLINE",
                         "_obj": "credit"},
        }
        self.posts: list[tuple[str, dict]] = []
        self.fail_post: dict[str, Exception] = {}
        self.fail_reads = False
        self._n = 0

    def query(self, soql: str) -> list[dict]:
        if self.fail_reads:
            raise SfApiError(401, '[{"errorCode": "INVALID_SESSION_ID"}]', "GET", "/query")
        kind = "payment" if "PaymentLineInvoiceLine" in soql else "credit"
        m = re.search(r"WHERE Id IN \(([^)]*)\)", soql)
        if m:
            ids = {i.strip().strip("'") for i in m.group(1).split(",")}
            return [self._public(r) for r in self.rows.values()
                    if r["Id"] in ids and r["_obj"] == kind]
        related = re.search(r"Related\w+ = '([^']+)'", soql).group(1)
        return [{"Id": r["Id"]} for r in self.rows.values()
                if r.get("_related") == related and r["Type"] == "Unapplied"]

    @staticmethod
    def _public(row: dict) -> dict:
        return {k: v for k, v in row.items() if not k.startswith("_")}

    def post(self, path: str, body: dict, *, retry: bool = True) -> dict:
        assert retry is False, "an unapply must never be resent by the transport"
        self.posts.append((path, body))
        row_id = path.split("/")[-3]
        if row_id in self.fail_post:
            raise self.fail_post[row_id]
        original = self.rows[row_id]
        if original["UnappliedStatus"] == "Yes":
            raise SfApiError(400, '[{"errorCode": "INVALID_FIELD_FOR_INSERT_UPDATE"}]',
                             "POST", path)
        original["UnappliedStatus"] = "Yes"
        self._n += 1
        new_id = f"{row_id[:3]}NEW{self._n:012d}"
        self.rows[new_id] = {"Id": new_id, "Amount": original["Amount"], "Type": "Unapplied",
                             "UnappliedStatus": "NA", "_obj": original["_obj"],
                             "_related": row_id}
        if "/paymentlines/" in path:
            return {"id": new_id, "unappliedDate": "2026-11-26T03:47:15.401Z"}
        return {"creditMemoLineInvoiceLineId": new_id, "errors": [], "success": True}


@pytest.fixture
def run(monkeypatch, tmp_path):
    """A settled line-level manifest on disk and the fake org behind `--org x`."""
    org = UnapplyOrg()
    manifest = Manifest(run_id="DEMO-U", reached_stage="payment_applied",
                        application_level="line", payment_ids=[PAYMENT],
                        payment_application_ids=[PAY_ROW], credit_memo_ids=["50gMEMO"],
                        credit_application_ids=[CREDIT_ROW])
    path = tmp_path / "DEMO-U.json"

    def load(_ref):
        return Manifest.from_dict(json.loads(path.read_text()))

    def write(m):
        path.write_text(json.dumps(m.to_dict()))
        return path

    write(manifest)
    monkeypatch.setattr(cli, "load_manifest", load)
    monkeypatch.setattr(cli, "write_manifest", write)
    monkeypatch.setattr(cli.SfRestClient, "from_alias", classmethod(lambda c, *a, **k: org))
    return org, path


def _unapply(*extra: str) -> int:
    return cli.main(["unapply", "--org", "x", "--manifest", "DEMO-U", *extra])


def _recorded(path) -> list[str]:
    return json.loads(path.read_text())["unapplied_row_ids"]


def test_unapplies_the_payment_then_the_credit_and_records_the_new_rows(run, capsys):
    org, path = run
    assert _unapply() == 0
    assert [p for p, _ in org.posts] == [
        f"/services/data/v68.0/commerce/billing/payments/{PAYMENT}/paymentlines/{PAY_ROW}"
        "/actions/unapply",
        f"/services/data/v68.0/commerce/invoicing/credit-memo-line-invoice-line/{CREDIT_ROW}"
        "/actions/unapply",
    ]
    assert _recorded(path) == ["1AlNEW000000000001", "4sGNEW000000000002"]
    out = capsys.readouterr().out
    assert "UNAPPLIED: payment 1AlROW0000000001AA (445.5)" in out
    assert "NOTE: 2 application(s) unapplied" in out
    assert out.rstrip().endswith("UNAPPLY: done (DEMO-U)")


def test_a_second_run_sends_nothing_and_records_the_existing_rows(run, capsys):
    org, path = run
    assert _unapply() == 0
    path.write_text(json.dumps({**json.loads(path.read_text()), "unapplied_row_ids": []}))
    org.posts.clear()
    assert _unapply() == 0
    assert org.posts == []  # the platform refuses a second unapply; it is never sent
    assert _recorded(path) == ["1AlNEW000000000001", "4sGNEW000000000002"]
    assert capsys.readouterr().out.count("ALREADY UNAPPLIED") == 2


def test_only_limits_the_kind(run):
    org, path = run
    assert _unapply("--only", "credit") == 0
    assert [p.split("/")[5] for p, _ in org.posts] == ["invoicing"]
    assert _recorded(path) == ["4sGNEW000000000001"]


def test_one_failed_row_fails_the_run_but_the_other_is_still_unapplied(run, capsys):
    org, path = run
    org.fail_post[PAY_ROW] = SfApiError(400, '[{"errorCode": "INVALID_FIELD"}]', "POST", "/x")
    assert _unapply() == 1
    assert _recorded(path) == ["4sGNEW000000000001"]
    out = capsys.readouterr().out
    assert f"FAIL: payment {PAY_ROW}:" in out and "UNAPPLY: fail (DEMO-U)" in out


def test_a_row_the_org_does_not_return_fails(run, capsys):
    org, _path = run
    del org.rows[CREDIT_ROW]
    assert _unapply() == 1
    assert f"credit application {CREDIT_ROW} is not a line-level Applied row" in (
        capsys.readouterr().out)


def test_header_level_is_refused_before_any_read(run, capsys):
    org, path = run
    path.write_text(json.dumps({**json.loads(path.read_text()), "application_level": "header"}))
    org.fail_reads = True  # a read would raise; the refusal comes first
    assert _unapply() == 2
    assert org.posts == []
    assert "measured at Line Level only" in capsys.readouterr().err


def test_a_refused_read_is_exit_2_and_writes_nothing(run, capsys):
    org, _path = run
    org.fail_reads = True
    assert _unapply() == 2
    assert org.posts == []
    assert "Salesforce request failed" in capsys.readouterr().err


def test_an_unreadable_manifest_is_exit_2(monkeypatch, capsys):
    def missing(_ref):
        raise FileNotFoundError(2, "No such file or directory", "out/NOPE.json")
    monkeypatch.setattr(cli, "load_manifest", missing)
    assert cli.main(["unapply", "--org", "x", "--manifest", "NOPE"]) == 2
    assert "ERROR: unapply:" in capsys.readouterr().err


def test_unapply_calls_fail_on_a_response_without_a_new_row():
    class Org:
        api_version = "68.0"

        def __init__(self, result):
            self.result = result

        def post(self, path, body, *, retry=True):
            return self.result

    with pytest.raises(lifecycle.SettlementError, match="no row id"):
        lifecycle.unapply_payment_line(Org({}), PAYMENT, PAY_ROW)
    with pytest.raises(lifecycle.SettlementError, match="credit memo line unapply failed"):
        lifecycle.unapply_credit_line(
            Org({"creditMemoLineInvoiceLineId": None, "errors": ["x"], "success": False}),
            CREDIT_ROW)


def _set(path, **fields):
    path.write_text(json.dumps({**json.loads(path.read_text()), **fields}))


def test_a_credit_only_run_with_no_recorded_level_is_unapplied(run):
    # The credit stage records no application level; the rows decide.
    org, path = run
    _set(path, application_level=None, reached_stage="credit_applied", payment_ids=[],
         payment_application_ids=[],
         settlement={"application_level": "auto", "credit": {"percent": 10.0}})
    assert _unapply() == 0
    assert _recorded(path) == ["4sGNEW000000000001"]


def test_a_flagged_row_with_no_unapplied_row_fails(run, capsys):
    org, path = run
    org.rows[PAY_ROW]["UnappliedStatus"] = "Yes"  # reversed some unmeasured way
    assert _unapply("--only", "payment") == 1
    assert org.posts == []
    out = capsys.readouterr().out
    assert "no Unapplied row names it" in out and "NOTE" not in out


def test_nothing_recorded_to_unapply_fails_without_reading(run, capsys):
    org, path = run
    _set(path, payment_application_ids=[])
    org.fail_reads = True
    assert _unapply("--only", "payment") == 1
    assert "recorded no payment application to unapply" in capsys.readouterr().out


def test_a_failed_manifest_write_fails_the_row_and_goes_on(run, monkeypatch, capsys):
    org, path = run
    real = cli.write_manifest
    calls = []

    def flaky(m):
        calls.append(1)
        if len(calls) == 1:
            raise OSError(28, "No space left on device")
        return real(m)

    monkeypatch.setattr(cli, "write_manifest", flaky)
    assert _unapply() == 1
    out = capsys.readouterr().out
    assert f"FAIL: payment {PAY_ROW}:" in out
    assert "unapplied in the org (Unapplied row 1AlNEW000000000001), but the manifest " \
        "write failed (OSError:" in out and "rerun to record it" in out
    assert "UNAPPLIED: credit" in out
    # The failed row is not recorded by the next row's write either.
    assert _recorded(path) == ["4sGNEW000000000002"]
    # A rerun looks the payment's Unapplied row up instead of sending again.
    org.posts.clear()
    monkeypatch.setattr(cli, "write_manifest", real)
    assert _unapply() == 0
    assert org.posts == []
    assert sorted(_recorded(path)) == ["1AlNEW000000000001", "4sGNEW000000000002"]



@pytest.mark.parametrize("fields, why", [
    ({"error": "[payment] apply returned 503"}, "records an error"),
    ({"reached_stage": "credit_applied",
      "settlement": {"application_level": "auto", "credit": {"percent": 10.0},
                     "payment": {"amount": "exact"}}},
     "reached credit_applied, not the end of its settlement"),
])
def test_an_unfinished_settlement_is_refused_before_any_read(run, capsys, fields, why):
    # An unfinished run may hold applications it never recorded, and a later
    # `cli step` could settle it again: only a finished one is reversed.
    org, path = run
    _set(path, **fields)
    org.fail_reads = True  # a read would raise; the refusal comes first
    assert _unapply() == 2
    assert org.posts == []
    assert why in capsys.readouterr().err


def test_harness_refusals_are_not_labelled_unexpected(run, capsys):
    org, _path = run
    del org.rows[CREDIT_ROW]
    assert _unapply() == 1
    out = capsys.readouterr().out
    assert "unexpected" not in out and "[unapply] credit application" in out



def test_inspect_shows_the_unapplied_rows_of_a_reversed_run(run, capsys):
    from scripts.txn_data_harness.handlers import SCENARIO_HANDLERS

    org, path = run
    assert _unapply() == 0
    manifest = Manifest.from_dict(json.loads(path.read_text()))
    summary = SCENARIO_HANDLERS[manifest.kind].summarize(manifest)
    assert summary["settlement"]["unapplied_row_ids"] == manifest.unapplied_row_ids
    assert "Unapplied rows recorded by cli unapply: 2" in cli._format_inspect_text(summary)


def test_a_recorded_row_that_reads_back_as_unapplied_is_not_sent(run, capsys):
    org, _path = run
    org.rows[CREDIT_ROW]["Type"] = "Unapplied"
    assert _unapply("--only", "credit") == 1
    assert org.posts == []
    assert "is not a line-level Applied row" in capsys.readouterr().out

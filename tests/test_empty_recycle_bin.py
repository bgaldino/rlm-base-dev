#!/usr/bin/env python3
"""Offline checks for scripts/recycle_bin/empty_recycle_bin.py.

    python tests/test_empty_recycle_bin.py

No org needed: the Org client is replaced by a fake, and the SOAP parser is fed
the response shape the partner API returns (success, per-Id error, and fault).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "recycle_bin"))

import empty_recycle_bin as erb  # noqa: E402

NS = 'xmlns="urn:partner.soap.sforce.com"'


def raises_recycle_error(fn, *args, match=""):
    try:
        fn(*args)
    except erb.RecycleBinError as exc:
        assert re.search(match, str(exc)), str(exc)
        return
    raise AssertionError("expected RecycleBinError")


def soap(body):
    return (
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">'
        f"<soapenv:Body>{body}</soapenv:Body></soapenv:Envelope>"
    )


class FakeOrg:
    api_version = "68.0"

    def __init__(self, deleted, sobjects=None, reject=(), gone=()):
        self.deleted = deleted  # {object: [ids]}
        self.sobjects = sobjects or []
        self.reject = set(reject)  # Ids the purge refuses
        self.gone = set(gone)  # Ids already purged (still visible to queryAll)
        self.purge_calls = []

    def describe_global(self):
        return self.sobjects

    def composite_batch(self, urls):
        out = []
        for u in urls:
            name = u.split("FROM%20")[1].split("%20")[0]
            if name == "NoIsDeleted":
                out.append({"statusCode": 400, "result": []})
            else:
                out.append({"statusCode": 200, "result": {"totalSize": len(self.deleted.get(name, []))}})
        return out

    def query_all(self, soql):
        name = soql.split("FROM ")[1].split(" ")[0]
        return [{"Id": i} for i in self.deleted[name]]

    def empty_recycle_bin(self, ids):
        self.purge_calls.append(list(ids))
        out = []
        for i in ids:
            if i in self.gone:
                out.append({"id": i, "success": False,
                            "errors": ["invalid record id; no recycle bin entry found"]})
            elif i in self.reject:
                out.append({"id": i, "success": False, "errors": ["INSUFFICIENT_ACCESS"]})
            else:
                out.append({"id": i, "success": True, "errors": []})
        return out


def test_candidates_need_queryable_and_undeletable():
    sobjects = [
        {"name": "Account", "queryable": True, "undeletable": True},
        {"name": "Setup", "queryable": True, "undeletable": False},
        {"name": "Hidden", "queryable": False, "undeletable": True},
    ]
    assert erb.candidate_objects(sobjects) == ["Account"]


def test_count_batches_and_skips_zero_and_rejected():
    names = [f"Obj{i}" for i in range(30)] + ["NoIsDeleted"]
    org = FakeOrg({"Obj3": ["a"] * 4})
    logs = []
    assert erb.count_deleted(org, names, logs.append) == {"Obj3": 4}
    assert any("NoIsDeleted" in line for line in logs)


def test_explicit_objects_fail_when_their_count_query_fails():
    org = FakeOrg({"Obj3": ["a"]})
    raises_recycle_error(erb.run, org, ["Obj3", "NoIsDeleted"], [], False, lambda *_: None,
                         match="NoIsDeleted")


def test_purge_chunks_at_200_and_reports_failures():
    ids = [f"001{i:012d}" for i in range(450)]
    org = FakeOrg({}, reject={ids[7]})
    failures, already = erb.purge(org, ids)
    assert [len(c) for c in org.purge_calls] == [200, 200, 50]
    assert failures == [{"id": ids[7], "errors": ["INSUFFICIENT_ACCESS"]}]
    assert already == 0


def test_already_purged_rows_are_not_failures():
    org = FakeOrg({"Account": ["001A", "001B"]}, gone={"001A", "001B"})
    assert erb.purge(org, ["001A", "001B"]) == ([], 2)
    assert erb.run(org, ["Account"], [], execute=True, log=lambda *_: None) == 0


def test_dry_run_purges_nothing():
    org = FakeOrg({"Account": ["001A", "001B"]})
    assert erb.run(org, ["Account"], [], execute=False, log=lambda *_: None) == 0
    assert org.purge_calls == []


def test_execute_purges_across_objects_and_honours_exclude():
    org = FakeOrg({"Account": ["001A"], "Quote": ["0Q0A", "0Q0B"], "Skip": ["xx"]})
    rc = erb.run(org, ["Account", "Quote", "Skip"], ["skip"], execute=True, log=lambda *_: None)
    assert rc == 0
    assert sorted(i for c in org.purge_calls for i in c) == ["001A", "0Q0A", "0Q0B"]


def test_execute_exit_code_1_on_partial_failure():
    org = FakeOrg({"Account": ["001A", "001B"]}, reject={"001B"})
    assert erb.run(org, ["Account"], [], execute=True, log=lambda *_: None) == 1


def test_empty_bin_is_a_clean_no_op():
    org = FakeOrg({"Account": []})
    assert erb.run(org, ["Account"], [], execute=True, log=lambda *_: None) == 0
    assert org.purge_calls == []


def test_parse_success_and_error_results():
    text = soap(
        f"<emptyRecycleBinResponse {NS}>"
        "<result><id>001A</id><success>true</success></result>"
        "<result><id>001B</id><success>false</success>"
        "<errors><message>insufficient access</message><statusCode>INSUFFICIENT_ACCESS</statusCode></errors></result>"
        "</emptyRecycleBinResponse>"
    )
    assert erb.parse_empty_response(200, text) == [
        {"id": "001A", "success": True, "errors": []},
        {"id": "001B", "success": False, "errors": ["insufficient access"]},
    ]


def test_parse_fault_raises():
    text = soap("<soapenv:Fault><faultcode>sf:INVALID_SESSION_ID</faultcode>"
                "<faultstring>INVALID_SESSION_ID: expired</faultstring></soapenv:Fault>")
    raises_recycle_error(erb.parse_empty_response, 500, text, match="INVALID_SESSION_ID")


def test_parse_non_xml_and_empty_raise():
    raises_recycle_error(erb.parse_empty_response, 502, "<html>bad gateway")
    raises_recycle_error(erb.parse_empty_response, 200, soap(f"<emptyRecycleBinResponse {NS}/>"))


def test_task_wrapper_declares_org():
    from tasks.rlm_empty_recycle_bin import EmptyRecycleBin
    assert EmptyRecycleBin.salesforce_task is True


def _run_wrapper(options, run_rc=0, run_error=None):
    """Run EmptyRecycleBin._run_task with erb.Org and erb.run stubbed; return (error, calls, warnings)."""
    import types
    from unittest import mock

    from tasks import rlm_empty_recycle_bin as wrapper

    calls, warnings = [], []

    def fake_run(org, objects, exclude, execute, log):
        calls.append((objects, exclude, execute))
        if run_error:
            raise run_error
        return run_rc

    task = wrapper.EmptyRecycleBin.__new__(wrapper.EmptyRecycleBin)
    task.options = options
    task.org_config = types.SimpleNamespace(instance_url="https://x", access_token="t")
    task.logger = types.SimpleNamespace(info=lambda *a: None, warning=warnings.append)
    with mock.patch.object(wrapper.erb, "Org", lambda *a: calls.append("org") or "ORG"), \
            mock.patch.object(wrapper.erb, "run", fake_run):
        try:
            task._run_task()
            return None, calls, warnings
        except Exception as exc:
            return str(exc), calls, warnings


def test_task_wrapper_options_blank_padded_and_lists():
    # todo 488: a list was stringified ("['A', 'B']" split into "['A'" and "'B']"), a padded
    # " true " read as false, and blank execute turned a purge into a dry run.
    for options, expected in (
        ({}, ([], [], True)),
        ({"objects": "", "exclude": "  ", "execute": "", "fatal": "  "}, ([], [], True)),
        ({"objects": None, "exclude": None, "execute": None}, ([], [], True)),
        ({"objects": ["Account", "Contact"], "exclude": ["Case"]}, (["Account", "Contact"], ["Case"], True)),
        ({"objects": " Account ,, Contact ", "execute": " false "}, (["Account", "Contact"], [], False)),
        ({"execute": "off"}, ([], [], False)),
        ({"execute": 0}, ([], [], False)),
        ({"execute": " TRUE "}, ([], [], True)),
    ):
        err, calls, _ = _run_wrapper(options)
        # Each case expects the purge call: no call fails it.
        assert err is None and calls == ["org", expected], (options, err, calls)


def test_task_wrapper_fatal_padded_and_blank():
    err, _, warnings = _run_wrapper({"fatal": " true "}, run_rc=1)
    assert err and "could not be purged" in err, err
    for blank in ("", "  ", None, "false"):
        err, calls, warnings = _run_wrapper({"fatal": blank}, run_rc=1)
        assert err is None and calls and warnings, (blank, err, calls, warnings)


def test_task_wrapper_refuses_bad_options_by_name_before_any_request():
    # Read outside the try, so a refusal fails the task instead of becoming a non-fatal warning.
    for options, needle in (
        ({"execute": ["true"]}, "execute must be a single value"),
        ({"execute": "maybe"}, "execute must be true or false"),
        ({"fatal": ["true"]}, "fatal must be a single value"),
        ({"fatal": "maybe"}, "fatal must be true or false"),
        ({"objects": 0}, "objects must be a comma-separated string"),
        ({"objects": ["Account", None]}, "objects items must be names"),
        ({"exclude": [" ", ""]}, "exclude contains no names"),
    ):
        err, calls, warnings = _run_wrapper(options)
        assert err and needle in err, (options, err)
        assert calls == [] and warnings == [], (options, calls, warnings)


def main():
    tests =[(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as exc:  # a check that blows up is a failure, not a crash
            failed += 1
            print(f"  FAIL  {name}  {type(exc).__name__}: {exc}")
    print(f"{len(tests) - failed}/{len(tests)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

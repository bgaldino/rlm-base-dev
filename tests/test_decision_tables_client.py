#!/usr/bin/env python3
"""Small offline contract suite for the Decision Table sf-CLI transport.

Run: ``python tests/test_decision_tables_client.py``.
No org is contacted: the subprocess/request boundary is replaced with fakes.
"""

import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.decision_tables import _client  # noqa: E402

_PASS = 0
_FAIL = 0


def check(label, condition, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL: {label}" + (f"  ({detail})" if detail else ""))


def _completed(*, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(["sf"], returncode, stdout=stdout, stderr=stderr)


def test_request_shape_and_empty_response():
    print("test_request_shape_and_empty_response")
    calls = []
    original = _client._run_sf

    def fake_run(args, *, input_text=None, timeout=None):
        calls.append((args, input_text, timeout))
        return _completed(stdout="")

    _client._run_sf = fake_run
    try:
        result = _client.connect_request(
            "post", "connect/example", {"name": "café"},
            target_org="rlm-base__test", api_version="67.0",
        )
        _client.connect_request("DELETE", "tooling/sobjects/DecisionTable/0lDxx",
                                target_org="rlm-base__test")
    finally:
        _client._run_sf = original

    post_args, post_stdin, post_timeout = calls[0]
    check("request prepends the versioned REST path",
          "/services/data/v67.0/connect/example" in post_args, post_args)
    check("request carries verb, target org, and stdin body flags",
          "POST" in post_args and "rlm-base__test" in post_args
          and post_args[-2:] == ["-b", "-"], post_args)
    check("request serializes its body on stdin",
          json.loads(post_stdin) == {"name": "café"}, post_stdin)
    check("mutation uses the mutation timeout", post_timeout == 600, post_timeout)
    check("empty/204-style stdout normalizes to an empty object", result == {}, result)
    check("bodiless DELETE still sends empty stdin", calls[1][1] == "", calls[1])


def test_dry_run_skips_writes_but_executes_reads():
    print("test_dry_run_skips_writes_but_executes_reads")
    calls = []
    logs = []
    original = _client._run_sf

    def fake_run(args, *, input_text=None, timeout=None):
        calls.append(args)
        return _completed(stdout='{"ok": true}')

    _client._run_sf = fake_run
    try:
        skipped = _client.connect_request(
            "PATCH", "tooling/sobjects/DecisionTable/0lDxx", {"Metadata": {}},
            target_org="x", dry_run=True, logger=logs.append,
        )
        read = _client.connect_request("GET", "tooling/query?q=SELECT%20Id",
                                       target_org="x", dry_run=True)
    finally:
        _client._run_sf = original

    check("dry-run mutation is skipped", skipped == {} and len(calls) == 1, calls)
    check("dry-run logs the skipped method and path",
          logs and "PATCH" in logs[0] and "DecisionTable" in logs[0], logs)
    check("dry-run read still executes and parses JSON", read == {"ok": True}, read)


def test_errors_preserve_salesforce_details():
    print("test_errors_preserve_salesforce_details")
    responses = [
        _completed(returncode=1,
                   stdout='[{"message":"bad field","errorCode":"INVALID_FIELD"}]'),
        _completed(stdout="not-json"),
    ]
    original = _client._run_sf
    _client._run_sf = lambda *a, **k: responses.pop(0)
    try:
        try:
            _client.connect_request("GET", "query?q=bad", target_org="x")
            check("non-zero response raises", False, "no exception")
        except _client.DecisionTableClientError as exc:
            check("Salesforce error code is retained", exc.has_error_code("INVALID_FIELD"), exc)
            check("return code and response body are retained",
                  exc.returncode == 1 and "bad field" in exc.body, exc.body)
        try:
            _client.connect_request("GET", "query?q=bad-json", target_org="x")
            check("invalid JSON raises", False, "no exception")
        except _client.DecisionTableClientError as exc:
            check("invalid JSON error includes a bounded raw response",
                  "Could not parse JSON" in str(exc) and "not-json" in str(exc), exc)
    finally:
        _client._run_sf = original


def test_query_pagination_preserves_tooling_path():
    print("test_query_pagination_preserves_tooling_path")
    paths = []
    responses = [
        {"records": [{"Id": "one"}], "done": False,
         "nextRecordsUrl": "/services/data/v67.0/tooling/query/01gNEXT"},
        {"records": [{"Id": "two"}], "done": True},
    ]
    original = _client.connect_request

    def fake_request(method, path, body, **kwargs):
        paths.append(path)
        return responses.pop(0)

    _client.connect_request = fake_request
    try:
        rows = _client.tooling_query("SELECT Id FROM DecisionTable", target_org="x")
    finally:
        _client.connect_request = original

    check("pagination returns records from every page",
          [row["Id"] for row in rows] == ["one", "two"], rows)
    check("nextRecordsUrl retains the tooling segment",
          paths[1] == "tooling/query/01gNEXT", paths)


def test_csv_transport_shapes_and_timeout():
    print("test_csv_transport_shapes_and_timeout")
    captured = []
    original_sobject = _client.sobjects_request
    original_connect = _client.connect_request
    original_run = _client.subprocess.run

    def fake_sobject(method, sobject, record_id=None, body=None, **kwargs):
        captured.append((method, sobject, body))
        return {"id": "068xx"}

    def fake_connect(method, path, body=None, **kwargs):
        captured.append((method, path, body))
        return {}

    _client.sobjects_request = fake_sobject
    _client.connect_request = fake_connect
    try:
        _client.content_version_insert("Rows", "Region\nNorth\n", target_org="x")
        _client.upload_decision_table_csv(
            "0lDxx", "068xx", delete_all_rows=True, version_number=2, target_org="x"
        )
        _client.get_decision_table_data(
            "0lDxx", version_number=2, row_filter="Region:North West", limit=5,
            target_org="x",
        )
    finally:
        _client.sobjects_request = original_sobject
        _client.connect_request = original_connect

    cv_body = captured[0][2]
    check("ContentVersion body contains the exact base64 CSV",
          base64.b64decode(cv_body["VersionData"]).decode("utf-8") == "Region\nNorth\n",
          cv_body)
    check("CSV upload carries version and destructive flag explicitly",
          captured[1][1].endswith("/file?versionNumber=2")
          and captured[1][2] == {"fileId": "068xx", "deleteAllRows": True}, captured[1])
    check("CSV data GET URL-encodes the filter and keeps version/limit",
          "versionNumber=2" in captured[2][1]
          and "filter=Region%3ANorth%20West" in captured[2][1]
          and "limit=5" in captured[2][1], captured[2])

    _client.subprocess.run = lambda *a, **k: (_ for _ in ()).throw(
        subprocess.TimeoutExpired(a[0] if a else ["sf"], k.get("timeout", 9))
    )
    try:
        try:
            _client._run_sf(["api", "request"], timeout=9)
            check("sf timeout raises", False, "no exception")
        except _client.DecisionTableClientError as exc:
            check("sf timeout is actionable", "timed out after 9s" in str(exc), exc)
    finally:
        _client.subprocess.run = original_run


def main():
    for test in (
        test_request_shape_and_empty_response,
        test_dry_run_skips_writes_but_executes_reads,
        test_errors_preserve_salesforce_details,
        test_query_pagination_preserves_tooling_path,
        test_csv_transport_shapes_and_timeout,
    ):
        test()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

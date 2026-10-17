#!/usr/bin/env python3
"""
Offline tests for tasks/rlm_mcp.py reconcile and binding-scope logic.

    .venv/bin/python tests/test_rlm_mcp_configure.py

No org needed: the Tooling API is faked by stubbing the task's query/create/update
methods. Covers (1) an existing-but-inactive McpServerAccess is reactivated, not
skipped, (2) a binding on another tool with the same (ApiSource, Operation) does
not make this tool look bound, (3) an access record linked to the wrong server
fails, (4) a missing invocable fails before any write, and (5) a tool whose
binding cannot be created is deleted, because one unbound tool makes the gateway
fail the whole server, (6) an identifier the org does not resolve warns and skips
the tools that depend on it, (7) a binding to a legacy identifier is rebound, and
(8) the real create/delete/report paths, run against a stubbed requests.
"""
import logging
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tasks import rlm_mcp  # noqa: E402
from tasks.rlm_mcp import ConfigureMcpServers  # noqa: E402

SERVER_ID = "SRV1"


class FakeTask(ConfigureMcpServers):
    def __init__(self, access=None, tools=None, bindings=None):
        self.logger = logging.getLogger("fake")
        self.dry_run = False
        self.created, self.skipped, self.failed, self.warnings = [], [], [], []
        self.access = access or []
        self.tools = tools or []
        self.bindings = bindings or []
        self.creates = []  # (sobject, body)
        self.updates = []  # (sobject, id, body)
        self.deletes = []  # (sobject, id)
        self.fail_creates = set()  # sobjects whose create fails
        self.unresolved_creates = False  # binding creates fail as an unknown CONNECT id
        self._last_soft_error = False
        self.project_config = None

    def _tooling_query(self, soql):
        if "FROM McpServerAccess" in soql:
            return self.access
        if "FROM McpServerToolDefinition" in soql:
            return self.tools
        if "FROM McpServerToolApiDefinition" in soql:
            # honor the ToolId IN (...) scope like the real API would
            return [b for b in self.bindings if f"'{b['ToolId']}'" in soql]
        raise AssertionError(soql)

    def _tooling_create(self, sobject, body, label, soft_error=None):
        self._last_soft_error = False
        if self.unresolved_creates and soft_error and sobject == "McpServerToolApiDefinition":
            self._last_soft_error = True
            self._warn(label)
            return None
        if sobject in self.fail_creates:
            self.failed.append(label)
            return None
        self.creates.append((sobject, body))
        self.created.append(label)
        return f"NEW{len(self.creates)}"

    def _tooling_update(self, sobject, record_id, body, label):
        self.updates.append((sobject, record_id, body))
        self.created.append(label)
        return True

    fail_deletes = False

    def _tooling_delete(self, sobject, record_id, label, on_failure):
        if self.fail_deletes:
            self.failed.append(on_failure)
            return False
        self.deletes.append((sobject, record_id))
        return True


def test_inactive_hosted_access_is_reactivated():
    t = FakeTask(access=[{"Id": "A1", "DeveloperName": "industries_revenue_cloud", "Active": False}])
    t._ensure_hosted([("industries_revenue_cloud", "revenue-cloud")])
    assert t.updates == [("McpServerAccess", "A1", {"Active": True})], t.updates
    assert t.creates == []


def test_active_hosted_access_is_skipped_and_missing_is_created():
    t = FakeTask(access=[{"Id": "A1", "DeveloperName": "industries_revenue_cloud", "Active": True}])
    t._ensure_hosted(
        [("industries_revenue_cloud", "revenue-cloud"), ("industries_revenue_cloud_billing", "rcb")]
    )
    assert t.updates == []
    assert [c[1]["DeveloperName"] for c in t.creates] == ["industries_revenue_cloud_billing"]
    assert "revenue-cloud" in t.skipped


def test_inactive_custom_access_is_reactivated():
    t = FakeTask(
        access=[{"Id": "A9", "DeveloperName": rlm_mcp.CUSTOM_SERVER_DEVELOPER_NAME,
                 "McpServerId": SERVER_ID, "Active": False}]
    )
    t._ensure_custom_access(SERVER_ID)
    assert t.updates == [("McpServerAccess", "A9", {"Active": True})]
    assert t.creates == []


def _tools():
    return [{"Id": "T1", "ToolName": "placeSalesTransaction"}, {"Id": "T2", "ToolName": "cloneSalesTransaction"}]


def test_binding_on_other_tool_does_not_count():
    # Another server's tool already binds CONNECT/placeSalesTransaction.
    other = {
        "Id": "B0", "ToolId": "OTHER", "ApiSource": "CONNECT",
        "ApiIdentifier": "revenue-transactionmanagement", "Operation": "placeSalesTransaction",
    }
    t = FakeTask(tools=_tools(), bindings=[other])
    t._ensure_tools(SERVER_ID)
    created = [b for s, b in t.creates if s == "McpServerToolApiDefinition"]
    assert {b["ToolId"] for b in created} == {"T1", "T2"}, created
    assert t.failed == []


def test_correct_binding_on_this_tool_is_skipped():
    mine = {
        "Id": "B1", "ToolId": "T1", "ApiSource": "CONNECT",
        "ApiIdentifier": "revenue-transactionmanagement", "Operation": "placeSalesTransaction",
    }
    t = FakeTask(tools=_tools(), bindings=[mine])
    t._ensure_tools(SERVER_ID)
    created = [b for s, b in t.creates if s == "McpServerToolApiDefinition"]
    assert [b["ToolId"] for b in created] == ["T2"], created
    assert "binding placeSalesTransaction" in t.skipped


def test_wrong_binding_on_this_tool_fails_rather_than_duplicating():
    wrong = {
        "Id": "B1", "ToolId": "T1", "ApiSource": "CONNECT",
        "ApiIdentifier": "something-else", "Operation": "placeSalesTransaction",
    }
    t = FakeTask(tools=_tools(), bindings=[wrong])
    t._ensure_tools(SERVER_ID)
    assert len(t.failed) == 1 and "placeSalesTransaction" in t.failed[0]
    created = [b for s, b in t.creates if s == "McpServerToolApiDefinition"]
    assert [b["ToolId"] for b in created] == ["T2"]


def test_failed_binding_removes_the_unbound_tool():
    # Existing unbound tools (an earlier run) and new ones take the same path.
    t = FakeTask(tools=_tools())
    t.fail_creates = {"McpServerToolApiDefinition"}
    t._ensure_tools(SERVER_ID)
    assert t.deletes == [("McpServerToolDefinition", "T1"),
                         ("McpServerToolDefinition", "T2")], t.deletes
    assert len(t.failed) == 2, t.failed


def test_unresolved_connect_identifier_warns_and_skips_the_tool():
    t = FakeTask(tools=_tools()[1:])  # clone exists; place is new
    t.warnings = []
    t.unresolved_creates = True
    t._ensure_tools(SERVER_ID)
    assert t.failed == [], t.failed
    assert any("placeSalesTransaction" in w for w in t.warnings), t.warnings
    # the place tool was created, its binding was unresolvable, so it was removed
    assert [d[0] for d in t.deletes] == ["McpServerToolDefinition"], t.deletes
    clone = [b for s, b in t.creates if s == "McpServerToolApiDefinition"]
    assert [b["ToolId"] for b in clone] == ["T2"], clone


def test_unresolved_mark_matches_only_the_unknown_identifier_error():
    unknown = 'No \\"industries-revenue\\" identifier found for source \\"CONNECT\\"'
    bad_op = 'No operation \\"x\\" found for identifier \\"revenue-price\\" from source \\"CONNECT\\"'
    assert rlm_mcp.UNRESOLVED_IDENTIFIER_MARK in unknown
    assert rlm_mcp.UNRESOLVED_IDENTIFIER_MARK not in bad_op


def test_failed_delete_says_the_server_stays_broken():
    t = FakeTask(tools=_tools()[:1])
    t.fail_creates = {"McpServerToolApiDefinition"}
    t.fail_deletes = True
    t._ensure_tools(SERVER_ID)
    assert any("returns 500 for the whole server" in f and "T1" in f for f in t.failed), t.failed


def test_dry_run_deletes_nothing():
    t = FakeTask(tools=_tools())
    t.dry_run = True
    t.fail_creates = {"McpServerToolApiDefinition"}
    t._ensure_tools(SERVER_ID)
    assert t.deletes == []


def test_legacy_binding_is_rebound_not_failed():
    legacy = {
        "Id": "B1", "ToolId": "T1", "ApiSource": "CONNECT",
        "ApiIdentifier": "industries-revenue", "Operation": "placeSalesTransaction",
    }
    t = FakeTask(tools=_tools(), bindings=[legacy])
    t._ensure_tools(SERVER_ID)
    assert t.failed == [], t.failed
    assert ("McpServerToolApiDefinition", "B1") in t.deletes, t.deletes
    rebound = [b for s, b in t.creates if s == "McpServerToolApiDefinition" and b["ToolId"] == "T1"]
    assert [b["ApiIdentifier"] for b in rebound] == ["revenue-transactionmanagement"], rebound


def test_legacy_binding_dry_run_changes_nothing():
    legacy = {
        "Id": "B1", "ToolId": "T1", "ApiSource": "CONNECT",
        "ApiIdentifier": "industries-revenue", "Operation": "placeSalesTransaction",
    }
    t = FakeTask(tools=_tools(), bindings=[legacy])
    t.dry_run = True
    t._ensure_tools(SERVER_ID)
    assert t.deletes == [] and t.failed == [], (t.deletes, t.failed)
    assert any("would rebind" in s for s in t.skipped), t.skipped


def _legacy():
    return {"Id": "B1", "ToolId": "T1", "ApiSource": "CONNECT",
            "ApiIdentifier": "industries-revenue", "Operation": "placeSalesTransaction"}


def test_legacy_rebind_whose_create_fails_removes_the_tool():
    t = FakeTask(tools=_tools(), bindings=[_legacy()])
    t.fail_creates = {"McpServerToolApiDefinition"}
    t._ensure_tools(SERVER_ID)
    assert ("McpServerToolApiDefinition", "B1") in t.deletes
    assert ("McpServerToolDefinition", "T1") in t.deletes, t.deletes  # not left unbound


def test_legacy_delete_failure_fails_and_creates_nothing():
    t = FakeTask(tools=_tools()[:1], bindings=[_legacy()])
    t.fail_deletes = True
    t._ensure_tools(SERVER_ID)
    assert len(t.failed) == 1 and "legacy binding" in t.failed[0], t.failed
    assert "unserved" in t.failed[0], t.failed
    assert not [b for s, b in t.creates if b.get("ToolId") == "T1"], t.creates


def test_tools_sharing_an_unresolved_identifier_are_skipped():
    saved = rlm_mcp.CUSTOM_TOOLS
    rlm_mcp.CUSTOM_TOOLS = (
        ("toolA", "CONNECT", "gone-id", "opA"),
        ("toolB", "CONNECT", "gone-id", "opB"),
    )
    try:
        t = FakeTask()
        t.unresolved_creates = True
        t._ensure_tools(SERVER_ID)
    finally:
        rlm_mcp.CUSTOM_TOOLS = saved
    tools_created = [b["ToolName"] for s, b in t.creates if s == "McpServerToolDefinition"]
    assert tools_created == ["toolA"], tools_created
    assert any("toolB skipped" in w for w in t.warnings), t.warnings
    assert t.failed == [], t.failed


class _Resp:
    def __init__(self, status, text):
        self.status_code, self.text = status, text

    def json(self):
        import json
        return json.loads(self.text)


class HttpTask(FakeTask):
    """Runs the REAL _tooling_create/_tooling_delete/_report against a stubbed requests."""
    _tooling_create = ConfigureMcpServers._tooling_create
    _tooling_delete = ConfigureMcpServers._tooling_delete

    def __init__(self, post_response, **kw):
        super().__init__(**kw)
        self.instance_url, self.api_version, self.access_token = "https://x", "68.0", "tok"
        self.post_response = post_response


def _with_requests(task, fn):
    real_post, real_delete = rlm_mcp.requests.post, rlm_mcp.requests.delete
    rlm_mcp.requests.post = lambda url, headers=None, json=None: task.post_response
    rlm_mcp.requests.delete = lambda url, headers=None: _Resp(204, "")
    try:
        return fn()
    finally:
        rlm_mcp.requests.post, rlm_mcp.requests.delete = real_post, real_delete


def test_real_create_unknown_identifier_is_a_warning():
    t = HttpTask(_Resp(400, '[{"message":"No \\"industries-revenue\\" identifier found for '
                            'source \\"CONNECT\\"","errorCode":"FIELD_INTEGRITY_EXCEPTION"}]'))
    out = _with_requests(t, lambda: t._tooling_create(
        "McpServerToolApiDefinition", {}, "binding x", soft_error=rlm_mcp.UNRESOLVED_IDENTIFIER_MARK))
    assert out is None and t._last_soft_error and t.failed == [] and len(t.warnings) == 1
    t._report()  # warnings only: must not raise


def test_real_create_other_rejection_is_a_failure():
    t = HttpTask(_Resp(400, '[{"message":"No operation \\"x\\" found for identifier '
                            '\\"revenue-price\\" from source \\"CONNECT\\""}]'))
    out = _with_requests(t, lambda: t._tooling_create(
        "McpServerToolApiDefinition", {}, "binding x", soft_error=rlm_mcp.UNRESOLVED_IDENTIFIER_MARK))
    assert out is None and not t._last_soft_error and len(t.failed) == 1 and t.warnings == []
    try:
        t._report()
    except Exception:
        pass
    else:
        raise AssertionError("a failure must make _report raise")


def test_real_create_success_resets_the_soft_flag():
    t = HttpTask(_Resp(201, '{"id": "NEW"}'))
    t._last_soft_error = True
    out = _with_requests(t, lambda: t._tooling_create(
        "McpServerToolApiDefinition", {}, "binding x", soft_error=rlm_mcp.UNRESOLVED_IDENTIFIER_MARK))
    assert out == "NEW" and not t._last_soft_error


def test_real_delete_success_and_failure():
    t = HttpTask(None)
    real_delete = rlm_mcp.requests.delete
    try:
        rlm_mcp.requests.delete = lambda url, headers=None: _Resp(204, "")
        assert t._tooling_delete("X", "1", "x", on_failure="boom") is True and t.failed == []
        rlm_mcp.requests.delete = lambda url, headers=None: _Resp(400, "[{\"message\":\"no\"}]")
        assert t._tooling_delete("X", "1", "x", on_failure="boom") is False
        assert len(t.failed) == 1 and t.failed[0].startswith("boom"), t.failed
    finally:
        rlm_mcp.requests.delete = real_delete


def test_real_dry_run_create_and_delete_touch_nothing():
    t = HttpTask(None)
    t.dry_run = True
    t._last_soft_error = True
    assert t._tooling_create("X", {}, "x", soft_error="m") is None and not t._last_soft_error
    assert t._tooling_delete("X", "1", "x", on_failure="f") is False  # requests not stubbed: would raise


def test_hosted_access_linked_to_a_custom_server_fails():
    t = FakeTask(access=[{"Id": "A1", "DeveloperName": "industries_revenue_cloud",
                          "McpServerId": "SRV9", "Active": True}])
    t._ensure_hosted([("industries_revenue_cloud", "revenue-cloud")])
    assert len(t.failed) == 1 and "SRV9" in t.failed[0], t.failed
    assert t.creates == [] and t.updates == []


def test_custom_access_linked_to_another_definition_fails():
    t = FakeTask(access=[{"Id": "A9", "DeveloperName": rlm_mcp.CUSTOM_SERVER_DEVELOPER_NAME,
                          "McpServerId": "OLD", "Active": False}])
    t._ensure_custom_access(SERVER_ID)
    assert len(t.failed) == 1 and "OLD" in t.failed[0], t.failed
    assert t.updates == []


def test_custom_access_linked_correctly_is_skipped():
    t = FakeTask(access=[{"Id": "A9", "DeveloperName": rlm_mcp.CUSTOM_SERVER_DEVELOPER_NAME,
                          "MasterLabel": rlm_mcp.CUSTOM_SERVER_LABEL,
                          "McpServerId": SERVER_ID, "Active": True}])
    t._ensure_custom_access(SERVER_ID)
    assert t.failed == [] and t.updates == [] and t.creates == []


def test_missing_invocable_fails_before_any_write():
    class NoApex(FakeTask):
        def _tooling_query(self, soql):
            if "FROM ApexClass" in soql:
                return []
            return super()._tooling_query(soql)

    t = NoApex()
    try:
        t._preflight_custom()
    except Exception as exc:  # CommandException, or Exception offline
        assert "No records were modified" in str(exc)
    else:
        raise AssertionError("expected the preflight to fail")
    assert t.creates == [] and t.updates == []


def test_run_task_preflights_before_any_hosted_write():
    class Org:
        access_token, instance_url, api_version = "tok", "https://x", "68.0"

    class NoApex(FakeTask):
        def _tooling_query(self, soql):
            if "FROM ApexClass" in soql:
                return []
            return super()._tooling_query(soql)

        def _preflight(self):
            pass

    t = NoApex()  # no access rows, so a hosted write would happen if it ran first
    t.options, t.org_config = {}, Org()
    try:
        t._run_task()
    except Exception as exc:
        assert "No records were modified" in str(exc), exc
    else:
        raise AssertionError("expected the preflight to fail")
    assert t.creates == [] and t.updates == [], (t.creates, t.updates)


def _run_ensure(options, flag):
    """Run _run_task with every phase stubbed, and report whether the custom server ran."""
    class Org:
        access_token, instance_url, api_version = "tok", "https://x", "68.0"

    class Project:
        project__custom__mcp_custom_server = flag

    calls = []

    class T(FakeTask):
        def _preflight(self):
            pass

        def _preflight_custom(self):
            calls.append("preflight_custom")

        def _ensure_hosted(self, wanted):
            calls.append("hosted")

        def _ensure_custom_server(self):
            calls.append("custom")

    t = T()
    t.options, t.org_config, t.project_config = options, Org(), Project()
    t._run_task()
    return calls


def test_custom_server_follows_the_flag_and_the_option_overrides_it():
    assert _run_ensure({}, None) == ["preflight_custom", "hosted", "custom"]  # flag absent: on
    assert _run_ensure({}, True) == ["preflight_custom", "hosted", "custom"]
    assert _run_ensure({}, False) == ["hosted"]
    assert _run_ensure({}, "False") == ["hosted"]  # a -o flag override arrives as a string
    assert _run_ensure({"custom_server": "True"}, False) == ["preflight_custom", "hosted", "custom"]
    assert _run_ensure({"custom_server": "False"}, True) == ["hosted"]


def test_list_labels_a_leftover_custom_server_when_custom_is_off():
    class T(FakeTask):
        def _tooling_query(self, soql):
            if "FROM McpServerAccess" in soql:
                return [{"DeveloperName": rlm_mcp.CUSTOM_SERVER_DEVELOPER_NAME,
                         "MasterLabel": rlm_mcp.CUSTOM_SERVER_LABEL, "Active": True}]
            return []

    t = T()
    lines = []
    t.logger = type("L", (), {"info": lambda self, m: lines.append(m),
                              "warning": lambda self, m: lines.append(m)})()
    t._list_surface([], want_custom=False)
    row = [m for m in lines if rlm_mcp.CUSTOM_SERVER_LABEL in m]
    assert row and "not removed" in row[0] and "UNMANAGED" not in row[0], lines


def test_no_overlay_class_remains():
    assert not hasattr(rlm_mcp, "DeployMcpOverlay")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)

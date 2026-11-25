#!/usr/bin/env python3
"""
Invariant: task options that reach SOQL are escaped or whitelisted, and an accepted option is used.

    python tests/test_soql_option_hardening.py

Needs `requests` (rlm_cml imports it) and a real CumulusCI install (the stdctx task subclasses its base classes); run it with the repo .venv interpreter.

Covers the pack 457 class sweep of tasks no flow calls: tasks/soql_utils.py, manage_decision_tables
(sort_by / sort_order / limit), export_cml (developer_name, version), manage_transaction_processing_types
(key value), extend_standard_context (the activate option was accepted and ignored), and the API version
of manage_transaction_processing_types and manage_fulfillment_scope_cnfg (read from project config).
"""
import re
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


def raises(fn, text=""):
    try:
        fn()
    except Exception as exc:
        return text in str(exc)
    return False


import importlib  # noqa: E402
import tasks as _tasks_pkg  # noqa: E402

_TASKS_PATH = [str(REPO / "tasks")]


def load(name):
    """Import tasks.<name>. Importing cumulusci setdefaults a synthetic `tasks` and sets its __path__ to [], so restore both first."""
    sys.modules["tasks"] = _tasks_pkg
    _tasks_pkg.__path__ = list(_TASKS_PATH)
    return importlib.import_module(f"tasks.{name}")


from tasks.soql_utils import positive_int, require_identifier, soql_quote, split_names  # noqa: E402

print("soql_utils")
check("soql_quote escapes quote and backslash", soql_quote("a'b\\c") == "'a\\'b\\\\c'", soql_quote("a'b\\c"))
check("soql_quote escapes newlines", "\n" not in soql_quote("a\nb"))
check("split_names splits, trims and de-duplicates", split_names(" a, b ,a,,c ", "x") == ["a", "b", "c"])
check("split_names flattens a list that holds commas", split_names(["a,b", "c"], "x") == ["a", "b", "c"])
check("split_names rejects an empty value", raises(lambda: split_names(" , ", "x"), "no names"))
check("split_names rejects a non-string", raises(lambda: split_names(5, "x"), "comma-separated"))
check("require_identifier accepts a field path", require_identifier("LastSyncDate", "s") == "LastSyncDate"
      and require_identifier("A.B_c", "s") == "A.B_c")
check("require_identifier rejects SOQL fragments", raises(lambda: require_identifier("Id; DROP", "s"), "field name"))
check("positive_int rejects 0, text and fragments",
      all(raises(lambda v=v: positive_int(v, "limit"), "positive integer") for v in ("0", "x", "5 OFFSET 1", "-1")))
check("positive_int accepts a number", positive_int(" 7 ", "limit") == 7)

print("manage_decision_tables: sort_by, sort_order and limit are validated")
ManageDecisionTables = load("rlm_manage_decision_tables").ManageDecisionTables


def dt_soql(options):
    task = ManageDecisionTables.__new__(ManageDecisionTables)
    task.options = options
    return task._build_soql_query()


soql = dt_soql({"sort_by": "DeveloperName", "sort_order": "asc", "limit": "3"})
check("valid values pass through", soql.endswith("ORDER BY DeveloperName Asc LIMIT 3"), soql)
check("sort_by fragment rejected", raises(lambda: dt_soql({"sort_by": "Id; x"}), "sort_by"))
check("sort_order fragment rejected", raises(lambda: dt_soql({"sort_order": "Desc; x"}), "sort_order"))
check("limit fragment rejected", raises(lambda: dt_soql({"limit": "1 OFFSET 2"}), "limit"))

print("export_cml: developer_name is escaped and version must be a whole number")
ExportCML = load("rlm_cml").ExportCML

queries = []
task = ExportCML.__new__(ExportCML)
task.options = {"developer_name": "Bad'Name", "version": "1", "output_dir": "/nonexistent-457"}
task.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None,
                                    error=lambda *a, **k: None, debug=lambda *a, **k: None)
blobs = []
# False for the ConstraintModel query, so both ExpressionSetDefinitionVersion queries are built.
task._export_query = lambda soql, fields, dest: queries.append((soql, fields)) or "ConstraintModel" not in fields
task._export_referenced_objects = lambda out: None
task._download_blob = lambda api, out: blobs.append(api)
import os  # noqa: E402
_makedirs = os.makedirs
os.makedirs = lambda *a, **k: None
try:
    task._run_task()
finally:
    os.makedirs = _makedirs
sent = " ".join(q for q, _ in queries)
esdv = [q for q, _ in queries if "FROM ExpressionSetDefinitionVersion" in q]
check("both ExpressionSetDefinitionVersion queries are built", len(esdv) == 2, repr(esdv))
check("developer_name quote escaped in every query", "'Bad\\'Name'" in sent and "'Bad'Name'" not in sent, sent)
check("developer_name escaped in each ESDV query", all("'Bad\\'Name'" in q for q in esdv), repr(esdv))
queries.clear()
blobs.clear()
task.options["version"] = " 007 "
os.makedirs = lambda *a, **k: None
try:
    task._run_task()
finally:
    os.makedirs = _makedirs
esdv = [q for q, _ in queries if "FROM ExpressionSetDefinitionVersion" in q]
check("version reaches SOQL only as a plain integer ('007' becomes 7)",
      len(esdv) == 2 and all(re.search(r"VersionNumber = 7\s*$", q) for q in esdv), repr(esdv))
check("the blob lookup uses the same normalised version (_V7, not _V007)", blobs == ["Bad'Name_V7"], repr(blobs))
task.options["version"] = "1 OR 1=1"
check("version fragment rejected", raises(task._run_task, "version must be a whole number"))
for bad in ("\u0661", "\uff11", "0"):
    task.options["version"] = bad
    check(f"version {bad!r} (non-ASCII digit or zero) rejected", raises(task._run_task, "version must be a whole number"))

print("export_cml: _build_id_query runs with a non-empty id list")
q = ExportCML._build_id_query("Product2", ["Id", "Name"], ["01t000000000001", "01t'x"])
check("ids quoted and escaped", q.endswith("WHERE Id IN ('01t000000000001','01t\\'x')"), q)
check("empty list still falls back", "WHERE Id = '000000000000000AAA'" in ExportCML._build_id_query("Product2", ["Id"], []))

print("manage_transaction_processing_types: the upsert key value is escaped")
ManageTransactionProcessingTypes = load("rlm_manage_transaction_processing_types").ManageTransactionProcessingTypes
import json  # noqa: E402
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "in.json"
    path.write_text(json.dumps([{"DeveloperName": "O'Brien"}]))
    seen = []
    t = ManageTransactionProcessingTypes.__new__(ManageTransactionProcessingTypes)
    t.options = {"input_file": str(path), "dry_run": "true"}
    t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None)
    t._get_api_context = lambda: ("tok", "https://x", "68.0")
    t._describe = lambda *a: {"fields": [{"name": "DeveloperName"}]}
    t._query = lambda tok, url, ver, soql: seen.append(soql) or []
    t._upsert_records()
check("key value escaped", seen and seen[0].endswith("DeveloperName = 'O\\'Brien'"), repr(seen))

print("api version: read from project config, never org_config.api_version")


class StrictOrgConfig(types.SimpleNamespace):
    def __getattr__(self, name):
        raise AssertionError(f"org_config.{name} is not an OrgConfig attribute")


for module, cls in (("rlm_manage_transaction_processing_types", "ManageTransactionProcessingTypes"),
                    ("rlm_manage_fulfillment_scope_cnfg", "ManageFulfillmentScopeCnfg")):
    klass = getattr(load(module), cls)
    t = klass.__new__(klass)
    t.options = {}
    t.org_config = StrictOrgConfig(access_token="tok", instance_url="https://x")
    t.project_config = types.SimpleNamespace(project__package__api_version="v68.0")
    try:
        version = t._get_api_context()[2]
    except Exception as exc:  # noqa: BLE001
        version = exc
    check(f"{cls} takes the project version ('v' stripped)", version == "68.0", repr(version))
    t.project_config = types.SimpleNamespace(project__package__api_version=None)
    check(f"{cls} refuses a missing project version", raises(t._get_api_context, "No API version"))

print("extend_standard_context: activate is honoured")
ExtendStandardContext = load("rlm_extend_stdctx").ExtendStandardContext


def activate_requested(value):
    t = ExtendStandardContext.__new__(ExtendStandardContext)
    t.options = {} if value is None else {"activate": value}
    return t._activate_requested()


check("true, 'true' and unset activate", activate_requested(True) and activate_requested("True") and activate_requested(None))
check("false and 'false' leave it inactive", not activate_requested(False) and not activate_requested("false"))
check("a null or blank activate takes the default (true)", activate_requested("") and activate_requested("  "))
check("a non-boolean string is rejected", raises(lambda: activate_requested("maybe"), "activate must be"))
check("a non-bool, non-string value is rejected", raises(lambda: activate_requested(1), "activate must be"))

t = ExtendStandardContext.__new__(ExtendStandardContext)
t.instance_url, t.access_token = "https://x", "tok"
t.project_config = types.SimpleNamespace(project__package__api_version="v68.0")
url, _ = t._build_url_and_headers("connect/context-definitions")
check("extend_standard_context strips a 'v' from the project version", "/services/data/v68.0/" in url, url)
t.project_config = types.SimpleNamespace(project__package__api_version=None)
check("extend_standard_context refuses a missing project version",
      raises(lambda: t._build_url_and_headers("x"), "No API version"))

print("extend_standard_context: _init_options rejects bad options before any change")
from unittest import mock  # noqa: E402
from cumulusci.tasks.sfdx import SFDXBaseTask  # noqa: E402


def init_options(options):
    t = ExtendStandardContext.__new__(ExtendStandardContext)
    t.options = options
    t._get_env = lambda: {}
    with mock.patch.object(SFDXBaseTask, "_init_options", create=True, new=lambda self, kwargs: None):
        t._init_options({})
    return t


GOOD = {"name": "N", "developerName": "D", "baseReference": "B", "activate": "false"}
check("a complete option set is accepted", init_options(dict(GOOD)) is not None)
check("a missing name, developerName and baseReference are all named",
      raises(lambda: init_options({"activate": True}), "name, developerName, baseReference"))
check("a bad activate value is rejected at init", raises(lambda: init_options(dict(GOOD, activate="maybe")), "activate must be"))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")

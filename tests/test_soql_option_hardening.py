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


from tasks.soql_utils import positive_int, require_identifier, soql_like_prefix, soql_quote, split_names  # noqa: E402

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
soql = dt_soql({"sort_by": " ", "sort_order": " "})
check("blank sort_by and sort_order mean the defaults", soql.endswith("ORDER BY LastSyncDate Desc"), soql)
soql = dt_soql({"sort_by": " DeveloperName "})
check("padded sort_by is trimmed", "ORDER BY DeveloperName Desc" in soql, soql)

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
import atexit  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
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


# --- pack 467: tasks and scripts outside the 457 sweep escape SOQL values with soql_quote -------------------
from unittest.mock import MagicMock  # noqa: E402
from urllib.parse import unquote  # noqa: E402

NASTY = "a'b\\c\nd"            # a quote, a backslash and a newline in one value
LIT = "'a\\'b\\\\c\\nd'"       # soql_quote(NASTY): one line, every special character escaped
EMPTY = {"records": [], "totalSize": 0, "done": True}


class FakeResponse:
    status_code = 200
    returncode = 0
    text = "{}"
    stderr = ""
    stdout = '{"result": {"records": [], "totalSize": 0}}'
    ok = True

    def json(self):
        return dict(EMPTY)

    def raise_for_status(self):
        pass


def _strings(value, out):
    if isinstance(value, str):
        # Only a URL or query path carries an encoded query string; a LIKE literal's `%` must stay as sent.
        out.append(unquote(value.replace("+", " ")) if re.search(r"(^https?:|[?&]q=)", value) and "%" in value else value)
    elif isinstance(value, dict):
        for item in value.values():
            _strings(item, out)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _strings(item, out)


def grab(task, fn, *args, **kwargs):
    """Run fn(*args) with every query transport stubbed; return the SOQL strings it sent. Errors after the query are ignored."""
    sent = []

    def record(*a, **k):
        found = []
        _strings(list(a) + list(k.values()), found)
        sent.extend(f for f in found if "SELECT" in f)
        return FakeResponse()

    def query(soql, *a, **k):
        record(soql)
        return dict(EMPTY)

    task.sf = MagicMock()
    task.sf.query.side_effect = query
    task.sf.query_all.side_effect = query
    for name in ("_query", "_query_all", "_soql_query", "_query_tooling", "_tooling_query", "_tooling_request", "_make_request",
                 "_run_cli"):
        if name not in getattr(task, "_real", ()):
            setattr(task, name, lambda *a, _n=name, **k: (record(*a, **k), [] if _n in ("_query", "_soql_query", "_query_tooling") else FakeResponse())[1])
    with mock.patch.object(type(task), "_sf", create=True, new=property(lambda self: self.sf)), \
            mock.patch("requests.get", record), mock.patch("requests.post", record), \
            mock.patch("subprocess.run", record), mock.patch("time.sleep", lambda *a: None):
        try:
            fn(*args, **kwargs)
        except Exception:  # noqa: BLE001 -- the stubs return empty rows; only the query text matters
            pass
    return sent


def grab_rows(task, fn, rows, *args):
    """Run fn(*args) where a query containing a key of `rows` returns that list; returns every SOQL string sent."""
    sent = []

    def answer(soql, *a, **k):
        sent.append(soql)
        return next((value for key, value in rows.items() if key in soql), [])

    def network(*a, **k):
        raise AssertionError("grab_rows: unexpected network call")

    for name in ("_query", "_soql_query", "_query_tooling", "_tooling_query"):
        setattr(task, name, answer)
    with mock.patch("requests.get", network), mock.patch("requests.post", network), \
            mock.patch("requests.request", network), mock.patch("time.sleep", lambda *a: None):
        try:
            fn(*args)
        except Exception:  # noqa: BLE001 -- only the query text matters
            pass
    return sent


def new_task(module, cls, **attrs):
    klass = getattr(load(module), cls)
    task = klass.__new__(klass)
    task.options = {}
    task.logger = MagicMock()
    task.org_config = types.SimpleNamespace(username="u@x.org", instance_url="https://x", access_token="tok")
    task.project_config = types.SimpleNamespace(project__package__api_version="68.0", repo_root="/nonexistent-467")
    for key, value in (("_base_url", "https://x/services/data/v68.0"), ("_headers", {})):
        try:
            setattr(task, key, value)
        except AttributeError:  # a read-only property derived from org_config
            pass
    for key, value in attrs.items():
        setattr(task, key, value)
    return task


def expect(label, sent, needle):
    """A query was sent, carries the escaped literal, and no query holds the raw value or a raw newline."""
    ok = bool(sent) and any(needle in q for q in sent) and not any("\n" in q for q in sent) \
        and not any(("a'b" in q) for q in sent)
    check(label, ok, repr(sent))


print("pack 467: values are escaped by soql_quote (quote, backslash and newline) in every changed query builder")

T = new_task("rlm_apply_procedure_plan_overlay", "ApplyProcedurePlanOverlay", options={"max_wait_seconds": 0})
expect("overlay _get_version", grab(T, T._get_version, NASTY), f"DeveloperName = {LIT} ")
expect("overlay _wait_for_active_state", grab(T, T._wait_for_active_state, NASTY, True), f"WHERE Id = {LIT}")
expect("overlay _get_section_records", grab(T, T._get_section_records, NASTY, NASTY),
       f"ProcedurePlanVersionId = {LIT} AND SubSectionType = {LIT}")
expect("overlay _get_all_section_records", grab(T, T._get_all_section_records, NASTY), f"ProcedurePlanVersionId = {LIT} ")
expect("overlay _get_expression_set_id", grab(T, T._get_expression_set_id, NASTY), f"DeveloperName = {LIT}")
expect("overlay _get_option_records", grab(T, T._get_option_records, NASTY, 1), f"ProcedurePlanSectionId = {LIT} ")
expect("overlay _get_criterion_records", grab(T, T._get_criterion_records, NASTY, 1), f"ProcedurePlanOptionId = {LIT} ")

T = new_task("rlm_billing", "CreateSequencePolicies")
policies = [{"selectionConditions": [{"filterFieldType": "Reference", "filterField": "LegalEntityId", "filterValue": NASTY}]}]
expect("billing _build_ref_id_cache", grab(T, T._build_ref_id_cache, policies), f"Name IN ({LIT})")
bad = [{"selectionConditions": [{"filterFieldType": "Reference", "filterField": "A Name FROM X--Id", "filterValue": "v"}]}]
check("billing rejects a filterField that is not an identifier", raises(lambda: T._build_ref_id_cache(bad), "filterField"))

T = new_task("rlm_community", "PatchNetworkEmailForDeploy", options={"network_name": NASTY})
expect("community _run_task", grab(T, T._run_task), f"Name = {LIT} LIMIT 1")

T = new_task("rlm_configure_pricing_recipe_table_mappings", "ConfigurePricingRecipeTableMappings")
rows = [{"pricingRecipeDeveloperName": NASTY, "decisionTableDeveloperName": NASTY}]
expect("recipe mappings _get_recipe_ids", grab(T, T._get_recipe_ids, "t", "https://x", "68.0", rows), f"DeveloperName IN ({LIT})")
expect("recipe mappings _get_table_ids", grab(T, T._get_table_ids, "t", "https://x", "68.0", rows), f"DeveloperName IN ({LIT})")
expect("recipe mappings _get_existing_mappings", grab(T, T._get_existing_mappings, "t", "https://x", "68.0", [NASTY]),
       f"PricingRecipeId IN ({LIT})")

T = new_task("rlm_create_approval_email_templates", "CreateApprovalEmailTemplates", _TIMEOUT=5)
session = MagicMock()
seen = []
session.get.side_effect = lambda url, params=None, **k: (seen.append(params["q"]), FakeResponse())[1]
try:
    T._create_templates("https://x", session, [{"Name": NASTY}], "f")
except Exception:  # noqa: BLE001
    pass
expect("approval templates _create_templates", seen, f"Name IN ({LIT})")
seen.clear()
try:
    T._link_alerts("https://x", session, [{"Name": NASTY, "EmailTemplate.Name": "T"}], {"T": "t"})
except Exception:  # noqa: BLE001
    pass
expect("approval templates _link_alerts", seen, f"Name IN ({LIT})")

T = new_task("rlm_create_persona_user", "CreatePersonaUser")
expect("persona _resolve_profile_id", grab(T, T._resolve_profile_id, NASTY), f"Name = {LIT} LIMIT 1")
sent = grab(T, T._find_existing_user, {"Username": NASTY, "Email": NASTY, "Alias": NASTY})
expect("persona _find_existing_user", sent, f"Username = {LIT} OR Username LIKE 'a\\'b\\\\c\\nd.%' OR (Email = {LIT} AND Alias = {LIT})")

for cls, label in (("CreateProcedurePlanDefinition", "plan def"),):
    T = new_task("rlm_create_procedure_plan_def", cls)
    expect(f"{label} _definition_exists", grab(T, T._definition_exists, NASTY), f"DeveloperName = {LIT}")
    expect(f"{label} _get_context_definition_id_by_label", grab(T, T._get_context_definition_id_by_label, NASTY),
           f"MasterLabel = {LIT}")
for cls in ("ActivateProcedurePlanVersion", "DeactivateProcedurePlanVersion"):
    T = new_task("rlm_create_procedure_plan_def", cls, options={"developerName": NASTY, "max_wait_seconds": 0,
                                                                 "poll_interval_seconds": 1})
    expect(f"{cls} _run_task", grab(T, T._run_task), f"DeveloperName = {LIT} ")

T = new_task("rlm_deactivate_changed_decision_tables", "DeactivateChangedDecisionTables")
expect("deactivate _active_tables", grab(T, T._active_tables, [NASTY, "b"]), f"DeveloperName IN ({LIT}, 'b') AND Status")

T = new_task("rlm_deploy_expression_sets", "DeployExpressionSets")
sent = []
T._query_all = lambda soql: (sent.append(soql), {"records": [{"Id": NASTY, "ExpressionSetDefinition": {"DeveloperName": "d"}}]})[1]
T._org_versions([NASTY])
check("deploy_expression_sets definition names escaped", len(sent) == 2 and f"DeveloperName IN ({LIT})" in sent[0], repr(sent))
check("deploy_expression_sets ids escaped", len(sent) == 2 and f"ExpressionSetId IN ({LIT})" in sent[1], repr(sent))

T = new_task("rlm_docgen", "FixDocumentTemplateBinaries", options={"library_developer_name": NASTY})
expect("docgen _run_task library", grab(T, T._run_task), f"DeveloperName = {LIT} LIMIT 1")
expect("docgen _find_latest_content_doc", grab(T, T._find_latest_content_doc, "058000000000001", NASTY), f"Title = {LIT} ")

T = new_task("rlm_expression_set_connect", "ExpressionSetConnectBase")
expect("es_connect _get_expression_set_definition_id", grab(T, T._get_expression_set_definition_id, NASTY), f"DeveloperName = {LIT}")
expect("es_connect _get_expression_set_id", grab(T, T._get_expression_set_id, NASTY), f"DeveloperName = {LIT}")
expect("es_connect _resolve_version_by_es_id", grab(T, T._resolve_version_by_es_id, NASTY), f"ExpressionSetId = {LIT} ")
expect("es_connect _definition_name", grab(T, T._definition_name, NASTY), f"WHERE Id = {LIT}")
expect("es_connect _list_versions", grab(T, T._list_versions, NASTY), f"ExpressionSetId = {LIT} ")
expect("es_connect _resolve_esdv_id", grab(T, T._resolve_esdv_id, NASTY, 1), f"ExpressionSetDefinitionId = {LIT} AND")

T = new_task("rlm_mcp", "ConfigureMcpServers")
expect("mcp _bindings_by_tool", grab(T, T._bindings_by_tool, [NASTY]), f"ToolId IN ({LIT})")
expect("mcp _ensure_tools: server Id", grab_rows(T, T._ensure_tools, {}, NASTY), f"WHERE McpServerId = {LIT}")
T.logger = MagicMock()
T._custom_server_id = lambda: NASTY
expect("mcp _list_surface: custom server Id", grab_rows(T, T._list_surface, {}, [], True), f"WHERE McpServerId = {LIT}")

T = new_task("rlm_recalculate_permission_set_groups", "RecalculatePermissionSetGroups")
expect("recalc _aggregate_fields", grab(T, T._aggregate_fields, NASTY, [NASTY]),
       f"Field IN ({LIT})")
expect("recalc _aggregate_fields group", grab(T, T._aggregate_fields, NASTY, [NASTY]), f"DeveloperName = {LIT})")
expect("recalc _query_groups", grab(T, T._query_groups, [NASTY]), f"DeveloperName IN ({LIT})")
expect("recalc _touch_group_description", grab(T, T._touch_group_description, NASTY), f"DeveloperName = {LIT} LIMIT 1")
T.PROBE_PERMISSION_SET = "Probe"
expect("recalc _force_recalc", grab(T, T._force_recalc, NASTY, 0, 1), f"DeveloperName = {LIT} LIMIT 1")

T = new_task("rlm_reconfigure_expression_set", "ReconfigureExpressionSet")
expect("reconfigure _get_expression_set_version (exact)", grab(T, T._get_expression_set_version, NASTY),
       "ApiName = 'a\\'b\\\\c\\nd_V1'")
expect("reconfigure _get_expression_set_version (LIKE)", grab(T, T._get_expression_set_version, NASTY),
       "ApiName LIKE 'a\\'b\\\\c\\nd%' ")
expect("reconfigure _update_context_definition", grab(T, T._update_context_definition, NASTY, NASTY),
       f"DeveloperName = {LIT}")

print("pack 467: Ids returned by the org are quoted too")
T = new_task("rlm_reconfigure_expression_set", "ReconfigureExpressionSet")
expect("reconfigure _update_context_definition: ExpressionSetDefinition Id",
       grab_rows(T, T._update_context_definition, {"FROM ExpressionSetDefinition ": [{"Id": NASTY}],
                                                   "FROM ContextDefinition": [{"Id": "x"}]}, "es", "cd"),
       f"ExpressionSetDefinitionId = {LIT}")
T = new_task("rlm_recalculate_permission_set_groups", "RecalculatePermissionSetGroups")
T._probe_permission_set_id = lambda base: NASTY
T._query_groups = lambda names: [{"Status": "Idle"}]
expect("recalc _force_recalc: group and probe Ids",
       grab_rows(T, T._force_recalc, {"FROM PermissionSetGroup ": [{"Id": NASTY}]}, "G", 0, 1),
       f"PermissionSetGroupId = {LIT} AND PermissionSetId = {LIT}")
T = new_task("rlm_docgen", "FixDocumentTemplateBinaries")
expect("docgen _find_latest_content_doc: library Id", grab(T, T._find_latest_content_doc, NASTY, "Template"), f"ContentWorkspaceId = {LIT}")
T = new_task("rlm_bre", "ExportBRE", options={"output_dir": "/nonexistent-467"})
sent = []
T._export_query = lambda soql, fields, dest: (sent.append(soql), [{"Id": NASTY, "RuleLibraryDefinitionId": NASTY}])[1]
os.makedirs = lambda *a, **k: None
def _no_network(*a, **k):
    raise AssertionError("bre: unexpected network call")


try:
    with mock.patch("requests.get", _no_network), mock.patch("requests.post", _no_network):
        try:
            T._run_task()
        except Exception:  # noqa: BLE001 -- only the queries built from the first rows matter
            pass
finally:
    os.makedirs = _makedirs
expect("bre RuleLibraryDefinition and RuleLibraryVersion Id filters", sent, f"FROM RuleLibraryDefinition WHERE Id IN ({LIT})")
check("bre RuleLibraryVersion filter quotes the RuleLibrary Id", any(f"RuleLibraryId IN ({LIT})" in q for q in sent), repr(sent))

T = new_task("rlm_refresh_decision_table", "RefreshDecisionTable", instance_url="https://x", access_token="tok")
expect("refresh _query_decision_table_statuses", grab(T, T._query_decision_table_statuses, [NASTY]), f"DeveloperName IN ({LIT})")

T = new_task("rlm_repair_pricing_schedules", "EnsurePricingSchedules")
expect("repair _get_missing_schedules", grab(T, T._get_missing_schedules, [NASTY]), f"Name IN ({LIT})")
expect("repair _get_missing_decision_tables", grab(T, T._get_missing_decision_tables, [NASTY]), f"DeveloperName IN ({LIT})")

klass = load("rlm_sharing").SetOrgWideDefaultsSharingOnly
T = klass.__new__(klass)
T.owds = {NASTY: "Private"}
T.api_names = set()
T.logger = MagicMock()
expect("sharing _prune_to_existing_objects", grab(T, T._prune_to_existing_objects), f"QualifiedApiName IN ({LIT})")

T = new_task("rlm_context_service", "ManageContextDefinition", instance_url="https://x", access_token="tok",
             api_version="68.0")
rule = {"contextAttribute": NASTY, "mappingName": "m", "contextNode": "n", "sObject": "Quote", "sObjectField": "Account",
        "childSObject": "Account", "childSObjectField": "Name"}
sent = grab(T, T._apply_traversal_hydration, [rule], {"contextDefinitionVersionList": [{"contextMappings": []}]}, False)
expect("context_service _apply_traversal_hydration", sent, f"ContextInputAttributeName={LIT} ORDER")
rule = dict(rule, contextAttribute="Attr")
T._make_request = lambda method, url, params=None, **k: (sent.append(params["q"]) if params else None,
                                                         {"records": [{"Id": NASTY}] if params and "FROM ContextAttributeMapping" in params["q"] else []})[1]
sent = []
try:
    T._apply_traversal_hydration([rule], {"contextDefinitionVersionList": [{"contextMappings": []}]}, False)
except Exception:  # noqa: BLE001 -- only the query text matters
    pass
expect("context_service _apply_traversal_hydration: the mapping Id from the org", sent, f"ContextAttributeMappingId={LIT}")

T = new_task("rlm_bre", "ExportBRE", options={"api_name": NASTY, "output_dir": "/nonexistent-467"})
os.makedirs = lambda *a, **k: None
try:
    expect("bre _run_task RuleLibrary filter", grab(T, T._run_task), f"WHERE ApiName = {LIT} ")
finally:
    os.makedirs = _makedirs

sfdmu = load("rlm_sfdmu")
sent = grab(type("Bare", (), {})(), sfdmu.target_org_user_name, NASTY + "@x")
expect("sfdmu target_org_user_name", sent, "Username = 'a\\'b\\\\c\\nd@x'")

print("pack 467: object and field names from plan files are validated as identifiers")
Exc = sfdmu.CommandException
BAD = "Account; DELETE"
T = new_task("rlm_sfdmu", "DeleteSFDMUData")
sent = grab(T, T._delete_all_records, BAD)
plan = tempfile.mkdtemp()
atexit.register(shutil.rmtree, plan, True)
with open(os.path.join(plan, "export.json"), "w") as handle:
    json.dump({"objects": [{"query": "SELECT Id FROM Bad", "operation": "Insert"},
                           {"query": "SELECT Id FROM Account", "operation": "Insert"}]}, handle)
T.options = {"pathtoexportjson": plan}
T.logger = MagicMock()
deleted = []
T._delete_all_records = lambda name: deleted.append(name) or 0
with mock.patch.object(sfdmu.sfdmu_export, "extract_object_name", lambda q: BAD if "Bad" in q else "Account"):
    check("sfdmu delete validates every object name before the first delete",
          raises(T._run_task, "sobject") and not deleted, repr(deleted))
del T._delete_all_records
check("sfdmu delete refuses an sobject name that is not an identifier before querying",
      raises(lambda: T._delete_all_records(BAD), "sobject") and not sent, repr(sent))
T = new_task("rlm_sfdmu", "TestSFDMUIdempotency")
T._get_org_for_cli = lambda: "u@x.org"
check("sfdmu idempotency counts refuse an sobject name that is not an identifier",
      raises(lambda: T._get_record_counts([BAD]), "sobject"))

tmp = Path(tempfile.mkdtemp())
atexit.register(shutil.rmtree, tmp, True)
(tmp / "export.json").write_text(json.dumps({"objects": [{"query": "SELECT Id FROM Account", "externalId": "Product2.$$Name$Code"}]}))
(tmp / "Account.csv").write_text("Id,Product2.$$Name$Code\n1,#N/A\n")
T = new_task("rlm_sfdmu", "ExtractSFDMUData")
sent = []
T._sf_query_records = lambda soql: sent.append(soql) or []
check("sfdmu code backfill skips a lookup that is not an identifier instead of aborting the extraction",
      T._build_code_backfill_map(str(tmp), str(tmp)) == {} and not sent, repr(sent))
(tmp / "export.json").write_text(json.dumps({"objects": [{"query": "SELECT Id FROM Account", "externalId": "Product2.Code"}]}))
(tmp / "Account.csv").write_text("Id,Product2.Code\n1,#N/A\n")
T._build_code_backfill_map(str(tmp), str(tmp))
check("sfdmu code backfill still queries a valid lookup", any("SELECT Product2.Name, Product2.Code FROM Account" in q for q in sent), repr(sent))
check("sfdmu accepts a namespaced custom object name", require_identifier("ns__Thing__c", "sobject") == "ns__Thing__c")
VK = load("rlm_validate_keys").ValidateSourceDataKeys
T = VK.__new__(VK)
T.options = {}
T.logger = MagicMock()
sent = grab(T, T._validate_object, "Product2", ["StockKeepingUnit"], False)
check("validate_keys queries a valid object and key", any("FROM Product2" in q for q in sent), repr(sent))
check("validate_keys rejects an object that is not an identifier",
      raises(lambda: T._validate_object("Product2 WHERE x", ["Name"], False), "object"))
check("validate_keys rejects a key field that is not an identifier",
      raises(lambda: T._validate_object("Product2", ["Name, (SELECT Id FROM X)"], False), "externalId field"))

T = new_task("rlm_repair_pricing_schedules", "EnsurePricingSchedules")
sent = grab(T, T._get_missing_schedules, [])
check("repair_pricing_schedules: no schedule names means no query", not sent and T._get_missing_schedules([]) == [], repr(sent))
# The settings paths are required options (CumulusCI always supplies them); grab stubs the deploys.
REPAIR_PATHS = {"disable_settings_path": "disable", "enable_settings_path": "enable"}
T.options = {"schedule_names": "A,B", "validate_decision_table_lookups": "false", **REPAIR_PATHS}
sent = grab(T, T._run_task)
check("repair_pricing_schedules: a comma-separated schedule_names option is read as names",
      any(f"Name IN ({soql_quote('A')}, {soql_quote('B')})" in q for q in sent), repr(sent))
for blank in (None, "", "  ", []):
    T.options = {"schedule_names": blank, "validate_decision_table_lookups": "false", **REPAIR_PATHS}
    sent = grab(T, T._run_task)
    check(f"repair_pricing_schedules: schedule_names={blank!r} checks the default schedules",
          any(soql_quote("Standard Price Adjustment Tier") in q for q in sent), repr(sent))
sys.path.insert(0, str(REPO / "scripts" / "docgen"))
import _soql as docgen_soql  # noqa: E402
check("docgen soql_escape escapes line breaks like soql_quote", docgen_soql.soql_escape(NASTY) == soql_quote(NASTY)[1:-1])
check("docgen soql_like_prefix matches tasks.soql_utils.soql_like_prefix",
      all(docgen_soql.soql_like_prefix(v) == soql_like_prefix(v) for v in (NASTY, "a_b%c", "o'x\\y")))
import docgen_template_manage as docgen_manage  # noqa: E402
sent = []
with mock.patch.object(docgen_manage, "_sf_query", lambda soql, org: sent.append(soql) or []):
    try:
        docgen_manage._find_content_doc("Quote_Doc%", NASTY, "org")
    except SystemExit:  # no document found: the script exits after both queries
        pass
check("docgen _find_content_doc: the LIKE fallback escapes _ and %, the library Id is escaped",
      any("Title LIKE 'Quote\\_Doc\\%%'" in q for q in sent) and all(f"ContentWorkspaceId = {LIT})" in q for q in sent)
      and len(sent) == 2, repr(sent))
docgen_network = []


def _docgen_no_network(*a, **k):
    docgen_network.append(a[:1])  # recorded: the calls below swallow exceptions
    raise AssertionError("docgen: unexpected network call")


sent = []
with mock.patch.object(docgen_manage, "_sf_query", lambda soql, org: sent.append(soql) or []), \
        mock.patch.object(docgen_manage, "_find_library", lambda org: "058"), \
        mock.patch.object(docgen_manage, "_resolve_template", lambda *a, **k: {"Id": "2dt", "Name": "T", "VersionNumber": 1,
                                                                                "Status": "Active", "IsActive": True, "Type": "t",
                                                                                "TokenList": ""}), \
        mock.patch("requests.get", _docgen_no_network), \
        mock.patch.object(docgen_manage, "_find_content_doc", lambda *a, **k: NASTY), \
        mock.patch.object(docgen_manage, "_get_rest_auth", lambda org: ("https://x", "t")):
    try:
        docgen_manage.cmd_status(types.SimpleNamespace(org="org", name="T", json_output=False))
    except (SystemExit, Exception):  # noqa: BLE001 -- only the query text matters
        pass
    for given in ({"version_id": "068" + NASTY}, {"version_id": "068x' OR Title != '"}, {"template": "T"}):
        try:
            docgen_manage.cmd_download(types.SimpleNamespace(**{"org": "org", "version_id": None, "template": None,
                                                                "output": None, **given}))
        except (SystemExit, Exception):  # noqa: BLE001 -- only the query text matters
            pass
check("docgen cmd_status and cmd_download: a --version-id that is not an Id is refused, the content document Id is escaped",
      not any("FROM ContentVersion WHERE Id" in q for q in sent) and sum(f"ContentDocumentId = {LIT} " in q for q in sent) == 2
      and not any("a'b" in q for q in sent) and not docgen_network, repr((sent, docgen_network)))
sys.path.insert(0, str(REPO / "scripts"))
import sync_appmenu_from_user as appmenu  # noqa: E402
sent = []
display = types.SimpleNamespace(returncode=0, stdout=json.dumps({"result": {"username": NASTY}}), stderr="")
with mock.patch.object(appmenu.subprocess, "run", lambda *a, **k: display), \
        mock.patch.object(appmenu, "_run_sf_query", lambda soql: sent.append(soql) or ""):
    try:
        appmenu._get_running_user_id()
    except Exception:  # noqa: BLE001 -- no rows: only the query text matters
        pass
check("sync_appmenu: the running username is escaped like soql_quote", sent == [f"SELECT Id FROM User WHERE Username = {LIT} LIMIT 1"], repr(sent))
sent = []
with mock.patch.object(appmenu, "_get_running_user_id", lambda: NASTY), \
        mock.patch.object(appmenu, "_run_sf_query", lambda soql: sent.append(soql) or ""):
    appmenu.main()  # no customization rows: returns before writing the snapshot
check("sync_appmenu: the running user Id from the org is escaped", len(sent) == 1 and f"WHERE UserId = {LIT} ORDER" in sent[0], repr(sent))

check("soql_like_prefix: _ and % in the prefix match themselves (a single backslash in the literal, measured live)", soql_like_prefix("a_b%c") == "'a\\_b\\%c%'", soql_like_prefix("a_b%c"))
check("soql_like_prefix: a backslash and a quote take the ordinary literal escape (measured live)",
      soql_like_prefix("o'x\\y") == "'o\\'x\\\\y%'", soql_like_prefix("o'x\\y"))
T = new_task("rlm_reconfigure_expression_set", "ReconfigureExpressionSet")
expect("reconfigure LIKE fallback escapes underscores", grab(T, T._get_expression_set_version, "Pricing_Proc"), "ApiName LIKE 'Pricing\\_Proc%'")

print("pack 467: scripts that cannot import tasks escape locally")
sys.path.insert(0, str(REPO / "scripts"))
import sfdmu_conditional_steps as scs  # noqa: E402

queries_sent = []
met = scs.requirement_met({"namedCredential": NASTY}, lambda q: queries_sent.append(q) or [])
check("conditional steps: namedCredential value escaped", queries_sent and f"DeveloperName = 'a\\'b\\\\c\\nd' " in queries_sent[0],
      repr(queries_sent))
check("conditional steps: _soql_text matches soql_quote", f"'{scs._soql_text(NASTY)}'" == LIT)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")

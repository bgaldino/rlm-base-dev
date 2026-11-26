#!/usr/bin/env python3
"""
Invariant: task options that reach SOQL are escaped or whitelisted, and an accepted option is used.

    python tests/test_soql_option_hardening.py

Needs `requests` (rlm_cml imports it) and a real CumulusCI install (the stdctx task subclasses its base classes); run it with the repo .venv interpreter.

Covers the pack 457 class sweep of tasks no flow calls: tasks/soql_utils.py, manage_decision_tables
(sort_by / sort_order / limit), export_cml (developer_name, version), manage_transaction_processing_types
(key value), extend_standard_context (the activate option was accepted and ignored), and the API version
of manage_transaction_processing_types and manage_fulfillment_scope_cnfg (read from project config).
Todo 488 adds option_flag (checked against the installed CumulusCI process_bool_arg) and the refusal
of a list item that is not a string in split_names / requested_names.
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

print("soql_utils: option_flag and non-string list items (todo 488)")
from tasks.soql_utils import FALSE_WORDS, TRUE_WORDS, option_flag, requested_names  # noqa: E402
from scripts.ux._flags import to_bool as _ux_to_bool  # noqa: E402

check("option_flag: None, blank and whitespace are the default",
      [option_flag(v, "f") for v in (None, "", "  ")] == [False] * 3
      and [option_flag(v, "f", default=True) for v in (None, "", "  ")] == [True] * 3)
check("option_flag: padded text, bools and int 0/1 are values",
      option_flag(" true ", "f") is True and option_flag(" FALSE ", "f", default=True) is False
      and option_flag(True, "f") is True and option_flag(False, "f", default=True) is False
      and option_flag(0, "f", default=True) is False and option_flag(1, "f") is True)
check("option_flag: 'on' and 'y' are True, 'off' and 'n' are False (CumulusCI's vocabulary)",
      option_flag("on", "f") is True and option_flag("Y", "f") is True
      and option_flag("off", "f", default=True) is False and option_flag("n", "f", default=True) is False)
check("option_flag: 'maybe' and the text '2' are refused, naming the option",
      raises(lambda: option_flag("maybe", "dry_run"), "dry_run must be true or false")
      and raises(lambda: option_flag("2", "dry_run"), "dry_run must be true or false"))
check("option_flag: any int is its truth value, as in CumulusCI (2 and -1 True, 0 False)",
      option_flag(2, "f") is True and option_flag(-1, "f") is True and option_flag(0, "f", default=True) is False)
check("option_flag: a list, even of one valid word, is refused, naming the option",
      raises(lambda: option_flag(["true"], "dry_run"), "dry_run must be a single value")
      and raises(lambda: option_flag([], "dry_run"), "dry_run must be a single value"))
from cumulusci.core.utils import process_bool_arg as _cci_bool  # noqa: E402


def _cci(value):
    try:
        return _cci_bool(value)
    except TypeError:
        return "refused"


def _ours(value):
    try:
        return option_flag(value, "f")
    except ValueError:
        return "refused"


_words = list(TRUE_WORDS) + list(FALSE_WORDS) + [w.upper() for w in TRUE_WORDS + FALSE_WORDS] + [
    "maybe", "2", "-1", "t", "f", "enabled", "truee", "nope", True, False, 0, 1, 2, -1]
_drift = [(w, _cci(w), _ours(w)) for w in _words if _cci(w) != _ours(w)]
check("option_flag agrees with the installed CumulusCI process_bool_arg on every unpadded value, ints included",
      not _drift, repr(_drift))


def _ux(value):
    try:
        return _ux_to_bool(value, "f")
    except Exception:  # UxOptionError
        return "refused"


_ux_drift = [(w, _ours(w), _ux(w)) for w in _words + ["", "  ", " true ", " OFF ", None, ["true"]]
             if _ours(w) != _ux(w)]
check("option_flag and scripts/ux/_flags.to_bool agree, blank and padded included", not _ux_drift, repr(_ux_drift))
check("requested_names refuses a null list item, naming the option",
      raises(lambda: requested_names(["A", None], "developer_names"), "developer_names items must be names"))
check("requested_names refuses a nested list item and an int item",
      raises(lambda: requested_names([["A", "B"]], "developer_names"), "developer_names items must be names")
      and raises(lambda: requested_names(["A", 5], "developer_names"), "developer_names items must be names"))
check("split_names refuses a null item too (it is the shared path)",
      raises(lambda: split_names([None], "x"), "x items must be names"))
check("requested_names still splits a list of strings that hold commas, and None/blank/[] are none",
      requested_names(["A,B", " C "], "x") == ["A", "B", "C"]
      and [requested_names(v, "x") for v in (None, "", "  ", [])] == [[], [], [], []])

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
check("an int is its truth value, as in CumulusCI (todo 488: it was refused)",
      activate_requested(1) is True and activate_requested(2) is True and activate_requested(0) is False)
check("a list or a dict is rejected, naming the option",
      raises(lambda: activate_requested(["true"]), "activate must be a single value")
      and raises(lambda: activate_requested({"a": 1}), "activate must be a single value"))

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

# max_wait_seconds is a positive integer (todo 488 refuses 0); grab stubs time.sleep, so 1 does not wait.
T = new_task("rlm_apply_procedure_plan_overlay", "ApplyProcedurePlanOverlay", options={"max_wait_seconds": 1})
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
    T = new_task("rlm_create_procedure_plan_def", cls, options={"developerName": NASTY, "max_wait_seconds": 1,
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
# They must exist, checked before any query (todo 488), so they are real (empty) directories.
REPAIR_PATHS = {"disable_settings_path": tempfile.mkdtemp(), "enable_settings_path": tempfile.mkdtemp()}
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

print("todo 488: currency, test_agents and import_cml read options through the shared helpers")
_currency = load("rlm_currency")


def currency_run(cls, options, csv_text=None):
    """Run an UpdateCurrencyRates* task with the rates fetch and the org stubbed to record.

    Returns (error text or None, calls, csv text after the run)."""
    calls = []
    task = cls.__new__(cls)
    task.options = dict(options)
    task.logger = types.SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
    tmp = None
    if csv_text is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        tmp.write(csv_text)
        tmp.close()
        task.options.setdefault("csv_path", tmp.name)
    task.sf = types.SimpleNamespace(
        query=lambda soql: calls.append(("query", soql)) or {"records": [
            {"Id": "1", "IsoCode": "EUR", "ConversionRate": 1.0}, {"Id": "2", "IsoCode": "GBP", "ConversionRate": 1.0}]},
        CurrencyType=types.SimpleNamespace(update=lambda rid, body: calls.append(("update", rid, body))),
    )
    with mock.patch.object(_currency, "_fetch_rates", lambda logger: calls.append("fetch") or {"EUR": 0.9, "GBP": 0.8}):
        try:
            cls._run_task(task)
            err = None
        except Exception as exc:
            err = str(exc)
    text = None
    if tmp is not None:
        text = Path(tmp.name).read_text(encoding="utf-8")
        os.unlink(tmp.name)
    return err, calls, text


CSV = "IsoCode,ConversionRate,IsCorporate\nUSD,1,true\nEUR,1,false\nGBP,1,false\n"
for value in (" true ", "on", "Y", True, 1):
    err, calls, text = currency_run(_currency.UpdateCurrencyRatesCsv, {"dry_run": value}, CSV)
    check(f"currency csv: dry_run {value!r} writes nothing (a padded ' true ' used to write)",
          err is None and "fetch" in calls and text == CSV, repr((err, calls)))
for value in (None, "", "  ", " false ", 0):
    err, calls, text = currency_run(_currency.UpdateCurrencyRatesCsv, {"dry_run": value}, CSV)
    check(f"currency csv: dry_run {value!r} is not a dry run",
          err is None and "fetch" in calls and "EUR,0.9" in text and "GBP,0.8" in text, repr((err, calls, text)))
for value, expected in ((["eur"], "EUR,0.9"), (" eur ,, ", "EUR,0.9")):
    err, calls, text = currency_run(_currency.UpdateCurrencyRatesCsv, {"iso_codes": value}, CSV)
    check(f"currency csv: iso_codes {value!r} filters to EUR (a list was a raw AttributeError)",
          err is None and expected in text and "GBP,1," in text, repr((err, text)))
for value in ("  ", "", []):
    err, calls, text = currency_run(_currency.UpdateCurrencyRatesCsv, {"iso_codes": value}, CSV)
    check(f"currency csv: blank iso_codes {value!r} is no filter (whitespace used to match nothing)",
          err is None and "EUR,0.9" in text and "GBP,0.8" in text, repr((err, text)))
for cls in (_currency.UpdateCurrencyRatesCsv, _currency.UpdateCurrencyRates):
    for options, needle in (({"dry_run": ["true"]}, "dry_run must be a single value"),
                            ({"dry_run": "maybe"}, "dry_run must be true or false"),
                            ({"iso_codes": 0}, "iso_codes must be a comma-separated string"),
                            ({"iso_codes": ["EUR", None]}, "iso_codes items must be names")):
        err, calls, _ = currency_run(cls, options, CSV if cls is _currency.UpdateCurrencyRatesCsv else None)
        check(f"currency {cls.__name__}: {options!r} refused by name before any request",
              err is not None and needle in err and calls == [], repr((err, calls)))
err, calls, _ = currency_run(_currency.UpdateCurrencyRates, {"dry_run": " true "})
check("currency org: a padded ' true ' dry run queries but updates nothing",
      err is None and "fetch" in calls and any(c[0] == "query" for c in calls if isinstance(c, tuple))
      and not [c for c in calls if isinstance(c, tuple) and c[0] == "update"], repr((err, calls)))
err, calls, _ = currency_run(_currency.UpdateCurrencyRates, {"iso_codes": ["gbp"]})
check("currency org: a list iso_codes updates only that currency",
      err is None and [c[1] for c in calls if isinstance(c, tuple) and c[0] == "update"] == ["2"], repr((err, calls)))

_agents = load("rlm_test_agents")


def agents_run(options):
    """Run TestAgents._run_task over a temp suite with the sf CLI steps stubbed; return (error, specs run)."""
    ran = []
    with tempfile.TemporaryDirectory() as d:
        for name in ("alpha.yaml", "beta.yaml"):
            Path(d, name).write_text("name: x\n", encoding="utf-8")
        task = _agents.TestAgents.__new__(_agents.TestAgents)
        task.options = {"tests_path": d, **options}
        task.org_config = types.SimpleNamespace(username="u@x")
        task.logger = types.SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
        task._create = lambda spec, api_name, target: ran.append(spec.name)
        task._run_and_evaluate = lambda spec, api_name, target: []
        try:
            task._run_task()
            return None, ran
        except Exception as exc:
            return str(exc), ran


for value, expected in ((None, ["alpha.yaml", "beta.yaml"]), ("", ["alpha.yaml", "beta.yaml"]),
                        ("  ", ["alpha.yaml", "beta.yaml"]), ([], ["alpha.yaml", "beta.yaml"]),
                        (["alpha", "beta.yaml"], ["alpha.yaml", "beta.yaml"]), (" beta , ", ["beta.yaml"]),
                        (["beta"], ["beta.yaml"])):
    err, ran = agents_run({"test_files": value})
    check(f"test_agents: test_files {value!r} runs {expected} (a list was stringified and matched nothing)",
          err is None and ran == expected, repr((err, ran)))
for options, needle in (({"test_files": 0}, "test_files must be a comma-separated string"),
                        ({"test_files": ["alpha", None]}, "test_files items must be names"),
                        ({"test_files": [" "]}, "test_files contains no names"),
                        ({"tests_path": ["x"]}, "tests_path must be a single value"),
                        ({"api_name_prefix": ["P"]}, "api_name_prefix must be a single value")):
    err, ran = agents_run(options)
    check(f"test_agents: {options!r} refused by name before any sf call",
          err is not None and needle in err and ran == [], repr((err, ran)))
err, ran = agents_run({"tests_path": "  ", "agent": ["quote"]})
check("test_agents: a blank tests_path falls back to agent, and a list agent is refused by name",
      err is not None and "agent must be a single value" in err and ran == [], repr((err, ran)))

_cml = load("rlm_cml")


def cml_options(options):
    """ImportCML._run_task up to its first file read; return (error, dataset_dirs, dry_run) seen there."""
    seen = {}
    task = _cml.ImportCML.__new__(_cml.ImportCML)
    task.options = {"data_dir": "/nonexistent", **options}
    task.logger = types.SimpleNamespace(info=lambda msg, *a: seen.setdefault("log", msg), warning=lambda *a: None)

    def read_csv(path):
        raise RuntimeError("stop: options read")
    task.read_csv = read_csv
    try:
        task._run_task()
    except RuntimeError as exc:
        if "stop: options read" not in str(exc):
            return str(exc), seen
        return None, seen
    except Exception as exc:
        return str(exc), seen
    return "ran past the first read", seen


for value, dry in ((None, "False"), ("", "False"), ("  ", "False"), (" true ", "True"), ("on", "True"), (0, "False")):
    err, seen = cml_options({"dry_run": value})
    check(f"import_cml: dry_run {value!r} is dry_run={dry} (a padded ' true ' imported for real)",
          err is None and f"(dry_run={dry})" in seen.get("log", ""), repr((err, seen)))
for options, needle in (({"dry_run": ["true"]}, "dry_run must be a single value"),
                        ({"dry_run": "maybe"}, "dry_run must be true or false"),
                        ({"dataset_dirs": 5}, "dataset_dirs must be a comma-separated string"),
                        ({"dataset_dirs": ["a", None]}, "dataset_dirs items must be names")):
    err, seen = cml_options(options)
    check(f"import_cml: {options!r} refused by name before any read or request",
          err is not None and needle in err and "log" not in seen, repr((err, seen)))


print("todo 488: recalculate_permission_set_groups and create_procedure_plan_definition booleans")
_psg = load("rlm_recalculate_permission_set_groups")


def psg_run(options):
    """Run _run_task with an Outdated group; return (error, queries, wait kwargs, force args)."""
    seen = {"queries": [], "wait": None, "force": None}
    task = _psg.RecalculatePermissionSetGroups.__new__(_psg.RecalculatePermissionSetGroups)
    task.options = {"api_names": "G1", "initial_delay_seconds": 0, **options}
    task.logger = types.SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
    task._query_groups = lambda names: seen["queries"].append(list(names)) or [
        {"DeveloperName": n, "Status": "Outdated"} for n in names]
    task._wait_until_updated = lambda **kw: seen.__setitem__("wait", kw)
    task._run_force = lambda names, timeout, poll, verify=None: seen.__setitem__("force", (names, verify))
    try:
        task._run_task()
        err = None
    except Exception as exc:
        err = str(exc)
    return err, seen


for value, want in ((None, True), ("", True), ("   ", True), (" true ", True), ("on", True),
                    ("false", False), (" off ", False), (0, False)):
    err, seen = psg_run({"trigger_recalc": value})
    check(f"psg: trigger_recalc {value!r} is {want} (blank read false, against its default true)",
          err is None and seen["queries"] and seen["wait"] and seen["wait"]["trigger_recalc"] is want,
          repr((err, seen)))
for value, want in ((" true ", True), ("on", True), ("", False), ("false", False)):
    err, seen = psg_run({"use_tooling_api": value})
    check(f"psg: use_tooling_api {value!r} is {want}",
          err is None and seen["wait"] and seen["wait"]["use_tooling_api"] is want, repr((err, seen)))
err, seen = psg_run({"force_recalc": " true ", "verify_fields": " Quote.A , Quote.B "})
check("psg: a padded force_recalc runs the force path with the parsed verify_fields",
      err is None and seen["force"] == (["G1"], ["Quote.A", "Quote.B"]), repr((err, seen)))
err, seen = psg_run({"force_recalc": "  ", "verify_fields": "  "})
check("psg: blank force_recalc is false (the normal wait runs) and blank verify_fields is none",
      err is None and seen["wait"] and seen["force"] is None, repr((err, seen)))
err, seen = psg_run({"api_names": [" G1 ", "G2,G3"]})
check("psg: api_names list items are trimmed and split",
      err is None and seen["queries"][0] == ["G1", "G2", "G3"], repr((err, seen)))
for options, needle in (({"trigger_recalc": ["true"]}, "trigger_recalc must be a single value"),
                        ({"trigger_recalc": "maybe"}, "trigger_recalc must be true or false"),
                        ({"use_tooling_api": "maybe"}, "use_tooling_api must be true or false"),
                        ({"force_recalc": ["true"]}, "force_recalc must be a single value"),
                        ({"verify_fields": ["Quote.A", None]}, "verify_fields items must be names"),
                        ({"api_names": ["G1", None]}, "api_names items must be names"),
                        ({"api_names": 0}, "api_names must be a comma-separated string"),
                        ({"api_names": "  "}, "api_names cannot be empty"),
                        ({"api_names": []}, "api_names cannot be empty")):
    err, seen = psg_run(options)
    check(f"psg: {options!r} refused by name before any query",
          err is not None and needle in err and not seen["queries"] and not seen["wait"] and not seen["force"],
          repr((err, seen)))

# The int options were raw int(): blank raised ValueError, "abc" an opaque one, 0 a silent no-wait.
for options, field, want in (({"timeout_seconds": "  "}, "timeout_seconds", 300), ({"timeout_seconds": " 60 "}, "timeout_seconds", 60),
                             ({"poll_seconds": ""}, "poll_seconds", 10), ({"post_trigger_delay_seconds": None}, "post_trigger_delay_seconds", 90),
                             ({"post_trigger_delay_seconds": "5"}, "post_trigger_delay_seconds", 5)):
    err, seen = psg_run(options)
    check(f"psg: {options!r} gives {field}={want} and the wait runs",
          err is None and seen["wait"] and seen["wait"][field] == want, repr((err, seen)))
_slept = []
with mock.patch.object(_psg.time, "sleep", lambda s: _slept.append(s)):
    for value, want in (("  ", None), ("0", None), (" 3 ", 3)):
        del _slept[:]
        err, seen = psg_run({"initial_delay_seconds": value})
        check(f"psg: initial_delay_seconds {value!r} is accepted (0 or more; blank is 0)",
              err is None and seen["wait"] and _slept == ([] if want is None else [want]), repr((err, _slept)))
for value in ("", "0", " 4 "):
    err, seen = psg_run({"retry_count": value})
    check(f"psg: retry_count {value!r} is accepted (0 or more; blank is 2)", err is None and seen["wait"], repr((err, seen)))
for options, needle in (({"timeout_seconds": "abc"}, "timeout_seconds must be a positive integer"),
                        ({"poll_seconds": 0}, "poll_seconds must be a positive integer"),
                        ({"retry_delay_seconds": ["5"]}, "retry_delay_seconds must be a single value"),
                        ({"post_trigger_delay_seconds": "-1"}, "post_trigger_delay_seconds must be a whole number, 0 or more"),
                        ({"retry_delay_seconds": "abc"}, "retry_delay_seconds must be a whole number, 0 or more"),
                        ({"initial_delay_seconds": "abc"}, "initial_delay_seconds must be a whole number, 0 or more"),
                        ({"retry_count": "-1"}, "retry_count must be a whole number, 0 or more")):
    err, seen = psg_run(options)
    check(f"psg: {options!r} refused by name before any query",
          err is not None and needle in err and not seen["queries"] and not seen["wait"], repr((err, seen)))

# 0 means "no wait" for the two delays, as before.
for name in ("post_trigger_delay_seconds", "retry_delay_seconds"):
    err, seen = psg_run({name: "0"})
    check(f"psg: {name} '0' is accepted (no wait)", err is None and seen["wait"] is not None, repr((err, seen)))
err, seen = psg_run({"post_trigger_delay_seconds": 0})
check("psg: post_trigger_delay_seconds int 0 reaches the wait as 0",
      err is None and seen["wait"]["post_trigger_delay_seconds"] == 0, repr((err, seen)))


def psg_retry_run(options):
    """_run_task where every wait times out; return (error, waits attempted, sleeps)."""
    attempts, sleeps = [], []
    task = _psg.RecalculatePermissionSetGroups.__new__(_psg.RecalculatePermissionSetGroups)
    task.options = {"api_names": "G1", **options}
    task.logger = types.SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
    task._query_groups = lambda names: [{"DeveloperName": n, "Status": "Outdated"} for n in names]

    def time_out(**kw):
        attempts.append(kw)
        raise _psg.TaskOptionsError("Timed out")
    task._wait_until_updated = time_out
    with mock.patch.object(_psg.time, "sleep", lambda secs: sleeps.append(secs)):
        try:
            task._run_task()
            return None, attempts, sleeps
        except Exception as exc:
            return str(exc), attempts, sleeps


# Default-value mutants: retry_count 2 (three attempts) and retry_delay_seconds 120.
err, attempts, sleeps = psg_retry_run({})
check("psg: unset retry_count and retry_delay_seconds: three attempts, two 120s retry sleeps, then the timeout",
      err == "Timed out" and len(attempts) == 3 and sleeps == [120, 120], repr((err, len(attempts), sleeps)))
err, attempts, sleeps = psg_retry_run({"retry_count": "  ", "retry_delay_seconds": "0"})
check("psg: blank retry_count is 2; retry_delay_seconds 0 retries at once",
      err == "Timed out" and len(attempts) == 3 and sleeps == [0, 0], repr((err, len(attempts), sleeps)))
err, attempts, sleeps = psg_retry_run({"retry_count": "0", "initial_delay_seconds": " 5 "})
check("psg: retry_count 0 makes one attempt; initial_delay_seconds ' 5 ' sleeps 5 first",
      err == "Timed out" and len(attempts) == 1 and sleeps == [5], repr((err, len(attempts), sleeps)))

_eps = load("rlm_repair_pricing_schedules")
_eps_dirs = tempfile.mkdtemp()
EPS_DISABLE, EPS_ENABLE, EPS_META = (os.path.join(_eps_dirs, n) for n in ("disable", "enable", "esd"))
for _d in (EPS_DISABLE, EPS_ENABLE, EPS_META):
    os.makedirs(_d)


def eps_run(options, still_missing=0):
    """EnsurePricingSchedules._run_task with one schedule missing at first; return (error, calls, sleeps).

    still_missing: how many polls still report it missing (more than poll_attempts fails the task)."""
    calls, sleeps = [], []
    polls = {"n": 0}
    t = _eps.EnsurePricingSchedules.__new__(_eps.EnsurePricingSchedules)
    t.options = {"disable_settings_path": EPS_DISABLE, "enable_settings_path": EPS_ENABLE,
                 "expression_sets_metadata_path": EPS_META, **options}
    t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None)
    t._discover_lookup_decision_tables = lambda path=None: calls.append(("discover", path)) or []

    def missing(names):
        calls.append(("schedules", list(names)))
        polls["n"] += 1
        return [names[0]] if polls["n"] <= 1 + still_missing else []
    t._get_missing_schedules = missing
    t._get_missing_decision_tables = lambda names: []
    t._deploy_settings = lambda path: calls.append(("deploy", path))
    with mock.patch.object(_eps.time, "sleep", lambda secs: sleeps.append(secs)):
        try:
            t._run_task()
            return None, calls, sleeps
        except Exception as exc:
            return str(exc), calls, sleeps


err, calls, sleeps = eps_run({})
check("ensure_pricing_schedules: defaults (blank or unset) poll every 10s, discover lookups, check the three schedules",
      err is None and ("discover", EPS_META) in calls
      and calls[1] == ("schedules", list(_eps.EnsurePricingSchedules.DEFAULT_SCHEDULE_NAMES))
      and calls[2:4] == [("deploy", EPS_DISABLE), ("deploy", EPS_ENABLE)] and sleeps == [10], repr((err, calls, sleeps)))
err, calls, sleeps = eps_run({"poll_attempts": "  ", "poll_interval_seconds": " 3 ",
                              "validate_decision_table_lookups": " off ", "schedule_names": "A, B"})
check("ensure_pricing_schedules: padded interval, blank attempts, ' off ' skips discovery, a comma string is two names",
      err is None and not any(c[0] == "discover" for c in calls) and calls[0] == ("schedules", ["A", "B"]) and sleeps == [3],
      repr((err, calls, sleeps)))
err, calls, sleeps = eps_run({"poll_attempts": " 2 ", "poll_interval_seconds": 1}, still_missing=5)
check("ensure_pricing_schedules: poll_attempts ' 2 ' polls twice, then fails naming what is missing",
      err is not None and "PriceAdjustmentSchedule" in err and sleeps == [1, 1], repr((err, sleeps)))
for options, needle in (({"poll_attempts": "abc"}, "poll_attempts must be a positive integer"),
                        ({"poll_attempts": 0}, "poll_attempts must be a positive integer"),
                        ({"poll_interval_seconds": ["5"]}, "poll_interval_seconds must be a single value"),
                        ({"validate_decision_table_lookups": "maybe"}, "validate_decision_table_lookups must be true or false"),
                        ({"schedule_names": ["A", None]}, "schedule_names items must be names"),
                        # The two settings paths: a bad enable path used to fail after the disable deploy.
                        ({"enable_settings_path": "  "}, "enable_settings_path is required"),
                        ({"enable_settings_path": None}, "enable_settings_path is required"),
                        ({"enable_settings_path": os.path.join(_eps_dirs, "typo")}, "enable_settings_path must be an existing directory or file"),
                        ({"disable_settings_path": ""}, "disable_settings_path is required"),
                        ({"disable_settings_path": [EPS_DISABLE]}, "disable_settings_path must be a single value"),
                        ({"expression_sets_metadata_path": os.path.join(_eps_dirs, "nope")},
                         "expression_sets_metadata_path must be a directory")):
    err, calls, sleeps = eps_run(options)
    check(f"ensure_pricing_schedules: {options!r} refused by name before any query or deploy (the polls were read "
          "after the two deploys)", err is not None and needle in err and calls == [] and sleeps == [],
          repr((err, calls, sleeps)))

# Padded settings paths pass the stripped directory check, so the deploys must get the stripped value
# too; the raw option would reach sf padded and fail after pricing had been disabled.
err, calls, sleeps = eps_run({"disable_settings_path": f" {EPS_DISABLE} ", "enable_settings_path": f" {EPS_ENABLE} "})
check("ensure_pricing_schedules: padded settings paths are deployed stripped",
      err is None and calls[2:4] == [("deploy", EPS_DISABLE), ("deploy", EPS_ENABLE)], repr((err, calls)))
# Default-value mutants: poll_attempts 6 and poll_interval_seconds 10 when nothing is set.
err, calls, sleeps = eps_run({}, still_missing=99)
check("ensure_pricing_schedules: unset poll_attempts polls six times, 10s apart, then fails",
      err is not None and "PriceAdjustmentSchedule" in err and sleeps == [10] * 6, repr((err, sleeps)))
# A blank expression_sets_metadata_path is the documented default (it was Path(""), the working
# directory, which found 0 expression sets); resolved from the working directory, as sf deploy is.
_cwd = os.getcwd()
os.chdir(REPO)
try:
    err, calls, sleeps = eps_run({"expression_sets_metadata_path": "  "})
finally:
    os.chdir(_cwd)
check("ensure_pricing_schedules: a blank expression_sets_metadata_path is the default directory",
      err is None and ("discover", "force-app/main/default/expressionSetDefinition") in calls, repr((err, calls)))
err, calls, sleeps = eps_run({"expression_sets_metadata_path": os.path.join(_eps_dirs, "nope"),
                              "validate_decision_table_lookups": "false"})
check("ensure_pricing_schedules: with lookups not validated, the metadata path is not needed",
      err is None and not any(c[0] == "discover" for c in calls), repr((err, calls)))

_ppd = load("rlm_create_procedure_plan_def")


def ppd_run(options):
    """Run CreateProcedurePlanDefinition._run_task; return (error, existence queries, POST bodies)."""
    queries, posts = [], []
    task = _ppd.CreateProcedurePlanDefinition.__new__(_ppd.CreateProcedurePlanDefinition)
    task.options = {"developerName": "D", "name": "N", "processType": "P", "versionRank": 1, **options}
    task.logger = types.SimpleNamespace(info=lambda *a: None, warning=lambda *a: None, error=lambda *a: None)
    task._definition_exists = lambda name: queries.append(name) or False
    task._resolve_context_definition_id = lambda: "CTX"
    resp = types.SimpleNamespace(ok=True, content=b"{}", json=lambda: {"id": "X"})
    with mock.patch.object(_ppd.CreateProcedurePlanDefinition, "_base_url", "https://x", create=True), \
            mock.patch.object(_ppd.CreateProcedurePlanDefinition, "_headers", {}, create=True), \
            mock.patch.object(_ppd.requests, "post", lambda url, headers=None, json=None, timeout=None:
                              posts.append(json) or resp):
        try:
            task._run_task()
            err = None
        except Exception as exc:
            err = str(exc)
    return err, queries, posts


for value, want in ((True, True), (" true ", True), ("on", True), (None, False), ("", False),
                    ("  ", False), ("false", False), (0, False)):
    err, queries, posts = ppd_run({"versionActive": value})
    check(f"procedure plan: versionActive {value!r} posts active={want}",
          err is None and queries == ["D"] and len(posts) == 1
          and posts[0]["procedurePlanDefinitionVersions"][0]["active"] is want
          if posts and "procedurePlanDefinitionVersions" in posts[0] else False, repr((err, queries, posts)))
for value, want in ((" 3 ", 3), (1, 1), (0, 0), ("0", 0)):
    err, queries, posts = ppd_run({"versionRank": value})
    check(f"procedure plan: versionRank {value!r} posts rank={want}",
          err is None and len(posts) == 1 and posts[0]["procedurePlanDefinitionVersions"][0]["rank"] == want,
          repr((err, queries, posts)))
for value, needle in ((None, "versionRank is required"), ("", "versionRank is required"),
                      ("  ", "versionRank is required"), ("abc", "versionRank must be a whole number"),
                      (-1, "versionRank must be a whole number"), (["1"], "versionRank must be a single value")):
    err, queries, posts = ppd_run({"versionRank": value})
    check(f"procedure plan: versionRank {value!r} refused by name before any query (not posted as rank 0)",
          err is not None and needle in err and queries == [] and posts == [], repr((err, queries, posts)))


def deactivate_run(options):
    calls = []
    t = _ppd.DeactivateProcedurePlanVersion.__new__(_ppd.DeactivateProcedurePlanVersion)
    t.options = {"developerName": "D", **options}
    t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None)

    def get(*a, **k):
        calls.append("get")
        raise RuntimeError("stop: first request")
    with mock.patch.object(_ppd.DeactivateProcedurePlanVersion, "_base_url", "https://x", create=True), \
            mock.patch.object(_ppd.DeactivateProcedurePlanVersion, "_headers", {}, create=True), \
            mock.patch.object(_ppd.requests, "get", get), \
            mock.patch.object(_ppd.requests, "patch", lambda *a, **k: calls.append("patch")):
        try:
            t._run_task()
            return "no error", calls
        except RuntimeError:
            return "reached", calls
        except Exception as exc:
            return str(exc), calls


for name in ("max_wait_seconds", "poll_interval_seconds"):
    for value, needle in (("abc", "must be a positive integer"), (0, "must be a positive integer"),
                          (["5"], "must be a single value")):
        err, calls = deactivate_run({name: value})
        check(f"deactivate procedure plan version: {name} {value!r} refused by name before any request",
              f"{name} {needle}" in err and calls == [], repr((err, calls)))
    for value in (None, "", "  ", " 5 "):
        err, calls = deactivate_run({name: value})
        check(f"deactivate procedure plan version: {name} {value!r} is accepted and the query is sent",
              err == "reached" and calls == ["get"], repr((err, calls)))
for value, needle in ((["false"], "versionActive must be a single value"),
                      ("maybe", "versionActive must be true or false")):
    err, queries, posts = ppd_run({"versionActive": value})
    check(f"procedure plan: versionActive {value!r} refused by name before any query (a list read True)",
          err is not None and needle in err and queries == [] and posts == [], repr((err, queries, posts)))


print("todo 488 round 2: context_service, procedure plan overlay, TPT, FSC, recipe mappings, validate_setup")
_ctx = load("rlm_context_service")


def ctx_run(options, plan, resolve_id="CTX"):
    """ManageContextDefinition._run_task on `plan` with every request stubbed; return (error, calls)."""
    calls = []
    with tempfile.TemporaryDirectory() as tmp:
        plan_path = Path(tmp) / "plan.json"
        plan_path.write_text(json.dumps(plan))
        t = _ctx.ManageContextDefinition.__new__(_ctx.ManageContextDefinition)
        t.options = {"plan_file": str(plan_path), **options}
        t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None)
        t._prep_runtime = lambda: calls.append("prep")
        t._resolve_context_definition_id = lambda name: calls.append("resolve") or resolve_id
        t._create_context_definition_record = lambda p, dry_run: calls.append(("create", dry_run)) or "NEW"
        t._validate_plan = lambda cid, p: calls.append("validate")
        t._is_context_active = lambda cid: calls.append("is_active") or True
        t._set_context_active = lambda cid, active, dry_run: calls.append(("deactivate", dry_run))
        t._fetch_context_definition = lambda cid: calls.append("fetch") or {}
        t._post_context_tags = lambda cid, payload, dry_run: calls.append(("tags", dry_run))
        t._log_verification = lambda detail, p: calls.append("verify")
        t._activate_context_definition = lambda cid, dry_run: calls.append(("activate", dry_run))
        t._translate_mapping_rules = lambda rules, detail, developer_name=None: calls.append("translate") or None
        try:
            t._run_task()
            return None, calls
        except Exception as exc:
            return str(exc), calls


PLAN = {"developerName": "D", "contextTags": [{"name": "T"}]}
err, calls = ctx_run({"dry_run": " true ", "verify": "on", "activate": "Y", "deactivate_before": " yes "}, PLAN)
check("context: padded and CumulusCI words read true (they read false under `in {1, true, yes}`)",
      err is None and ("deactivate", True) in calls and ("tags", True) in calls and "verify" in calls
      and ("activate", True) in calls, repr((err, calls)))
err, calls = ctx_run({"dry_run": "", "verify": "  ", "activate": False}, {**PLAN, "activate": True})
check("context: blank options are false, and a set activate (False) beats the plan's activate",
      err is None and ("tags", False) in calls and "verify" not in calls
      and not any(isinstance(c, tuple) and c[0] == "activate" for c in calls), repr((err, calls)))
err, calls = ctx_run({"activate": "  "}, {**PLAN, "activate": True, "deactivateBefore": True})
check("context: a blank activate / deactivate_before falls back to the plan's own fields",
      err is None and ("activate", False) in calls and ("deactivate", False) in calls, repr((err, calls)))
err, calls = ctx_run({"validate_only": " true "}, PLAN)
check("context: a padded validate_only validates and stops", err is None and calls[-1] == "validate", repr((err, calls)))
RULES_PLAN = {**PLAN, "mappingRules": [{"mappingType": "SOBJECT", "contextNode": "N"}]}
for options in ({}, {"translate_plan": "  "}, {"translate_plan": None}, {"translate_plan": " on "}):
    err, calls = ctx_run(options, RULES_PLAN)
    check(f"context: translate_plan {options.get('translate_plan', '<unset>')!r} is true (its default): "
          "mappingRules are translated", err is None and "translate" in calls, repr((err, calls)))
# The create path (_run_create_flow) reads translate_plan too, with the same default.
CREATE_PLAN = {**RULES_PLAN, "create": True}
for options in ({}, {"translate_plan": "  "}, {"translate_plan": None}):
    err, calls = ctx_run(options, CREATE_PLAN, resolve_id=None)
    check(f"context create: translate_plan {options.get('translate_plan', '<unset>')!r} is true (its default): "
          "mappingRules are translated", err is None and ("create", False) in calls and "translate" in calls,
          repr((err, calls)))
err, calls = ctx_run({"translate_plan": "false"}, CREATE_PLAN, resolve_id=None)
check("context create: translate_plan 'false' skips translating mappingRules",
      err is None and ("create", False) in calls and "translate" not in calls, repr((err, calls)))
for value in ("false", " off ", 0):
    err, calls = ctx_run({"translate_plan": value}, RULES_PLAN)
    check(f"context: translate_plan {value!r} skips translating mappingRules",
          err is None and "fetch" in calls and "translate" not in calls, repr((err, calls)))
for options, needle in (({"dry_run": ["true"]}, "dry_run must be a single value"),
                        ({"verify": "maybe"}, "verify must be true or false"),
                        ({"translate_plan": "maybe"}, "translate_plan must be true or false"),
                        ({"activate": ["true"]}, "activate must be a single value"),
                        ({"deactivate_before": "maybe"}, "deactivate_before must be true or false"),
                        ({"validate_only": "maybe"}, "validate_only must be true or false")):
    err, calls = ctx_run(options, PLAN)
    check(f"context: {options!r} refused by name before the plan or any request",
          err is not None and needle in err and calls == [], repr((err, calls)))

_ppo = load("rlm_apply_procedure_plan_overlay")


def ppo_run(options):
    calls = []
    t = _ppo.ApplyProcedurePlanOverlay.__new__(_ppo.ApplyProcedurePlanOverlay)
    t.options = {"developerName": "D", **options}
    t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None)
    t._load_overlay = lambda: calls.append("overlay") or {}

    def get_version(name):
        calls.append("get_version")
        raise RuntimeError("stop: first request")
    t._get_version = get_version
    try:
        t._run_task()
        return "no error", calls
    except RuntimeError:
        return "reached", calls
    except Exception as exc:
        return str(exc), calls


check("procedure plan overlay: padded and blank booleans reach the first request",
      ppo_run({"dry_run": " on ", "verify": "", "activate_after_apply": "  "}) == ("reached", ["overlay", "get_version"]))
check("procedure plan overlay: _bool_option reads CumulusCI's words (\"on\" was false) and blank is the default",
      _ppo.ApplyProcedurePlanOverlay._bool_option(" on ", False, "dry_run") is True
      and _ppo.ApplyProcedurePlanOverlay._bool_option("  ", True, "verify") is True
      and _ppo.ApplyProcedurePlanOverlay._bool_option(0, True, "verify") is False)
for name in ("dry_run", "verify", "activate_after_apply"):
    for value, needle in ((["true"], "must be a single value"), ("maybe", "must be true or false")):
        err, calls = ppo_run({name: value})
        check(f"procedure plan overlay: {name} {value!r} refused by name before the overlay or any request",
              f"{name} {needle}" in err and calls == [], repr((err, calls)))

# max_wait_seconds / poll_interval_seconds were int() after the deactivation and the writes.
for name in ("max_wait_seconds", "poll_interval_seconds"):
    for value, needle in (("abc", "must be a positive integer"), (0, "must be a positive integer"),
                          (["5"], "must be a single value")):
        err, calls = ppo_run({name: value})
        check(f"procedure plan overlay: {name} {value!r} refused by name before the overlay or any request",
              f"{name} {needle}" in err and calls == [], repr((err, calls)))
    for value in (None, "", "  ", " 7 "):
        err, calls = ppo_run({name: value})
        check(f"procedure plan overlay: {name} {value!r} is accepted (blank is the default) and the run reaches the org",
              err == "reached" and calls == ["overlay", "get_version"], repr((err, calls)))
_po = _ppo.ApplyProcedurePlanOverlay.__new__(_ppo.ApplyProcedurePlanOverlay)
_po.options = {"max_wait_seconds": "  ", "poll_interval_seconds": " 4 "}
check("procedure plan overlay: _wait_options gives the default for blank and reads padded text",
      _po._wait_options() == (45, 4), repr(_po._wait_options()))
# The late reads themselves: with raw int() back in either method, the blank wait raises here.
_po = _ppo.ApplyProcedurePlanOverlay.__new__(_ppo.ApplyProcedurePlanOverlay)
_po.options = {"max_wait_seconds": "  ", "poll_interval_seconds": " 1 "}
_po.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None)
_po._query = lambda soql: [{"Id": "V1", "IsActive": True}]
_po._all_counts_valid = lambda version_id, overlay: True
for _label, _call in (("_wait_for_active_state", lambda: _po._wait_for_active_state("V1", True)),
                      ("_verify_overlay", lambda: _po._verify_overlay("V1", {}))):
    try:
        _call()
        _ok, _detail = True, ""
    except Exception as exc:
        _ok, _detail = False, f"{type(exc).__name__}: {exc}"
    check(f"procedure plan overlay: {_label} runs with a blank max_wait and a padded poll", _ok, _detail)

_tpt = load("rlm_manage_transaction_processing_types")
_fsc = load("rlm_manage_fulfillment_scope_cnfg")


def upsert_run(module, cls, options, records):
    """`operation: upsert` over `records` with the org stubbed; return (error, calls)."""
    calls = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "in.json"
        path.write_text(json.dumps(records))
        klass = getattr(module, cls)
        t = klass.__new__(klass)
        t.options = {"operation": "upsert", "input_file": str(path), **options}
        t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None,
                                         error=lambda *a, **k: None)
        t._get_api_context = lambda: calls.append("context") or ("tok", "https://x", "68.0")
        t._describe = lambda *a: calls.append("describe") or {"fields": [{"name": "DeveloperName", "type": "string"}]}
        t._query = lambda *a: calls.append("query") or []
        t._create_record = lambda *a, **k: calls.append("create") or "NEW"
        t._update_record = lambda *a, **k: calls.append("update")
        try:
            t._run_task()
            return None, calls
        except Exception as exc:
            return str(exc), calls


for module, cls, label in ((_tpt, "ManageTransactionProcessingTypes", "transaction processing types"),
                           (_fsc, "ManageFulfillmentScopeCnfg", "fulfillment scope cnfg")):
    for value, writes in ((" true ", False), ("on", False), ("", True), ("  ", True), (" false ", True), (0, True)):
        err, calls = upsert_run(module, cls, {"dry_run": value}, [{"DeveloperName": "A"}])
        check(f"{label}: dry_run {value!r} -> create={writes} (\"on\" and padded \" true \" wrote)",
              err is None and "query" in calls and ("create" in calls) is writes, repr((err, calls)))
    for value, needle in ((["true"], "dry_run must be a single value"), ("maybe", "dry_run must be true or false")):
        err, calls = upsert_run(module, cls, {"dry_run": value}, [{"DeveloperName": "A"}])
        check(f"{label}: dry_run {value!r} refused by name before any request",
              err is not None and needle in err and calls == [], repr((err, calls)))

# The up-front dry_run read in _run_task covers every operation, not only upsert.
for module, cls, label, ops in ((_tpt, "ManageTransactionProcessingTypes", "transaction processing types", ("list",)),
                                (_fsc, "ManageFulfillmentScopeCnfg", "fulfillment scope cnfg", ("list", "extract"))):
    for op in ops:
        err, calls = upsert_run(module, cls, {"operation": op, "dry_run": "maybe"}, [])
        check(f"{label}: operation {op} with dry_run 'maybe' is refused naming dry_run, before any file or request",
              err is not None and "dry_run must be true or false" in err and calls == [], repr((err, calls)))

_prtm = load("rlm_configure_pricing_recipe_table_mappings")


def prtm_run(options, table_found=True):
    calls = []
    t = _prtm.ConfigurePricingRecipeTableMappings.__new__(_prtm.ConfigurePricingRecipeTableMappings)
    t.options = dict(options)
    t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: calls.append("warn"))
    t._load_mappings = lambda: [{"pricingRecipeDeveloperName": "R", "decisionTableDeveloperName": "T",
                                 "pricingComponentType": "C"}]
    t._get_api_context = lambda: calls.append("context") or ("tok", "https://x", "68.0")
    t._get_recipe_ids = lambda *a: calls.append("recipes") or {"R": "RID"}
    t._get_table_ids = lambda *a: calls.append("tables") or ({"T": "TID"} if table_found else {})
    t._get_existing_mappings = lambda *a: calls.append("existing") or {}
    t._post_tooling = lambda *a: calls.append("post")
    try:
        t._run_task()
        return None, calls
    except Exception as exc:
        return str(exc), calls


for value, posts in ((" true ", False), ("on", False), ("", True), ("off", True)):
    err, calls = prtm_run({"dry_run": value})
    check(f"recipe mappings: dry_run {value!r} -> post={posts}", err is None and "existing" in calls
          and ("post" in calls) is posts, repr((err, calls)))
err, calls = prtm_run({"skip_missing_tables": " on "}, table_found=False)
check("recipe mappings: a padded skip_missing_tables 'on' skips the missing table", err is None and "warn" in calls,
      repr((err, calls)))
err, calls = prtm_run({"skip_missing_tables": "  "}, table_found=False)
check("recipe mappings: a blank skip_missing_tables is false: the missing table fails",
      err is not None and "not found" in err, repr((err, calls)))
for options, needle in (({"dry_run": ["true"]}, "dry_run must be a single value"),
                        ({"skip_missing_tables": "maybe"}, "skip_missing_tables must be true or false")):
    err, calls = prtm_run(options)
    check(f"recipe mappings: {options!r} refused by name before any request (it was read after the lookups)",
          err is not None and needle in err and calls == [], repr((err, calls)))

_vs = load("rlm_validate_setup")
_t = _vs.ValidateSetup.__new__(_vs.ValidateSetup)
for value, default, want in ((" false ", True, False), ("off", True, False), ("n", True, False),
                             ("  ", True, True), (None, False, False), (" true ", False, True), (0, True, False)):
    _t.options = {"auto_fix": value}
    check(f"validate_setup: auto_fix {value!r} (default {default}) is {want} (\" false \" and \"off\" read true)",
          _t._bool_option("auto_fix", default) is want)
for value, needle in ((["false"], "auto_fix must be a single value"), ("maybe", "auto_fix must be true or false")):
    _t.options = {"auto_fix": value}
    check(f"validate_setup: auto_fix {value!r} is refused by name", raises(lambda: _t._bool_option("auto_fix", True), needle))
_t = _vs.ValidateSetup.__new__(_vs.ValidateSetup)
_t.options = {"fail_on_error": "maybe"}
_t.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None, error=lambda *a, **k: None)
_ran = []
_t._check_python = lambda *a, **k: _ran.append("check")
check("validate_setup: _run_task refuses a bad boolean before any check runs",
      raises(lambda: _t._run_task(), "fail_on_error must be true or false") and _ran == [])


print("todo 488: export_bre retrieve_metadata and reconfigure_expression_set rank through the helpers")
_bre = load("rlm_bre")


def bre_run(options):
    """ExportBRE._run_task with the exports stubbed; return (error, queries, metadata retrieved?)."""
    queries, retrieved = [], []
    t = _bre.ExportBRE.__new__(_bre.ExportBRE)
    t.options = {"output_dir": tempfile.mkdtemp(), **options}
    t.logger = MagicMock()

    def export(soql, fields, dest):
        queries.append(soql)
        if "FROM RuleLibrary " in soql:
            return [{"Id": "RL1", "RuleLibraryDefinitionId": "D1", "RuleLibraryDefinition": {"DeveloperName": "Lib"}}]
        return []
    t._export_query = export
    t._export_rulesets = lambda ids, output_dir: None
    t._retrieve_metadata = lambda names, output_dir: retrieved.append(list(names))
    try:
        t._run_task()
        err = None
    except Exception as exc:
        err = str(exc)
    return err, queries, bool(retrieved)


# Today's default is kept: blank or unset retrieves. "no", "off" and "0" now mean false (only
# "false" did; anything else retrieved anyway).
for value, want in ((None, True), ("", True), ("  ", True), (" true ", True), ("on", True), ("y", True),
                    ("false", False), (" no ", False), ("off", False), ("0", False), (0, False)):
    err, queries, retrieved = bre_run({"retrieve_metadata": value})
    check(f"export_bre: retrieve_metadata {value!r} retrieves metadata: {want}",
          err is None and queries and retrieved is want, repr((err, len(queries), retrieved)))
for value, needle in ((["true"], "retrieve_metadata must be a single value"),
                      ("maybe", "retrieve_metadata must be true or false")):
    err, queries, retrieved = bre_run({"retrieve_metadata": value})
    check(f"export_bre: retrieve_metadata {value!r} refused by name before any query",
          err is not None and needle in err and queries == [] and not retrieved, repr((err, queries)))

_res = load("rlm_reconfigure_expression_set")


def res_run(options):
    """ReconfigureExpressionSet._run_task up to its first query; return (error, queries, logged rank)."""
    queries, logged = [], []
    t = _res.ReconfigureExpressionSet.__new__(_res.ReconfigureExpressionSet)
    t.options = {"expression_set_name": "ES", "context_definition_name": "CD", **options}
    t.logger = MagicMock()
    t.logger.info.side_effect = lambda msg, *a: logged.append(a)

    def first_query(*a, **k):
        queries.append(a)
        raise RuntimeError("stop: first query")
    t._get_expression_set_version = first_query
    try:
        t._run_task()
        return None, queries, logged
    except RuntimeError as exc:
        return ("reached" if "stop: first query" in str(exc) else str(exc)), queries, logged
    except Exception as exc:
        return str(exc), queries, logged


for value, want in ((None, 1), ("", 1), ("  ", 1), (" 3 ", 3), (2, 2), ("1", 1)):
    err, queries, logged = res_run({"rank": value})
    check(f"reconfigure_expression_set: rank {value!r} is {want} and the first query is sent",
          err == "reached" and queries and logged and logged[0][2] == want, repr((err, queries, logged[:1])))
for value, needle in ((0, "rank must be a positive integer"), ("0", "rank must be a positive integer"),
                      ("-2", "rank must be a positive integer"), ("abc", "rank must be a positive integer"),
                      (["1"], "rank must be a single value")):
    err, queries, logged = res_run({"rank": value})
    check(f"reconfigure_expression_set: rank {value!r} refused by name before any query (0 became 1, 'abc' a ValueError)",
          err is not None and needle in err and queries == [], repr((err, queries)))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")

"""Tasks resolve the API version from project config; OrgConfig has no api_version (pack 479)."""
import ast
import importlib
import logging
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import repo `tasks.*` modules before cumulusci: its project_config empties tasks.__path__ (see rlm_manage_flows).
import tasks.expression_set_schema  # noqa: E402,F401
from tasks.soql_utils import project_api_version  # noqa: E402
from scripts.ux._context import DEFAULT_API_VERSION as UX_DEFAULT_API_VERSION  # noqa: E402


class StrictOrgConfig(types.SimpleNamespace):
    """Like OrgConfig: no api_version attribute, and reading one fails hard (STRICT_GETATTR)."""

    def __getattr__(self, name):
        raise AssertionError(f"org_config.{name} is not an OrgConfig attribute")


def _task(module, cls, version="69.0", options=None):
    # cumulusci's project_config empties tasks.__path__ once imported; restore it so later task modules resolve.
    sys.modules["tasks"].__path__ = [str(REPO / "tasks")]
    klass = getattr(importlib.import_module(module), cls)
    task = klass.__new__(klass)
    task.org_config = StrictOrgConfig(access_token="t", instance_url="https://x.my.salesforce.com")
    task.project_config = types.SimpleNamespace(project__package__api_version=version)
    task.options = options or {}
    task.logger = logging.getLogger("t")
    return task


PROPERTIES = [
    ("tasks.rlm_expression_set_connect", "ExpressionSetConnectBase"),
    ("tasks.rlm_apply_procedure_plan_overlay", "ApplyProcedurePlanOverlay"),
    ("tasks.rlm_sfdmu", "DeleteSFDMUData"),
    ("tasks.rlm_reconfigure_expression_set", "ReconfigureExpressionSet"),
    ("tasks.rlm_create_procedure_plan_def", "CreateProcedurePlanDefinition"),
    ("tasks.rlm_create_procedure_plan_def", "ActivateProcedurePlanVersion"),
    ("tasks.rlm_create_procedure_plan_def", "DeactivateProcedurePlanVersion"),
    ("tasks.rlm_bre", "ExportBRE"),
    ("tasks.rlm_cml", "CMLBaseTask"),
]
# Sites with an api_version task option, which wins over the project's version.
TAKES_OPTION = {"ExpressionSetConnectBase", "ApplyProcedurePlanOverlay", "DeleteSFDMUData", "ExportBRE", "CMLBaseTask"}
# Sites that had no fallback: an unset version still raises.
NO_DEFAULT = {"CMLBaseTask"}

# (module, class, call returning the version) for versions read inside a method.
METHODS = [
    ("tasks.rlm_recalculate_permission_set_groups", "RecalculatePermissionSetGroups", lambda t: t._api_version(), False, True),
    ("tasks.rlm_configure_pricing_recipe_table_mappings", "ConfigurePricingRecipeTableMappings",
     lambda t: t._get_api_context()[2], True, True),
    ("tasks.rlm_manage_flows", "ManageFlows", lambda t: t._api_version(), False, False),
    ("tasks.rlm_manage_expression_sets", "ManageExpressionSets", lambda t: t._get_api_version(), False, False),
    ("tasks.rlm_manage_transaction_processing_types", "ManageTransactionProcessingTypes",
     lambda t: t._get_api_context()[2], True, False),
    ("tasks.rlm_manage_fulfillment_scope_cnfg", "ManageFulfillmentScopeCnfg", lambda t: t._get_api_context()[2], True, False),
]


def _raises(fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 (TaskOptionsError is cumulusci's)
        return "No API version" in str(exc)
    return False


def test_property_reads_project_version():
    for module, cls in PROPERTIES:
        assert _task(module, cls)._api_version == "69.0", cls
        assert _task(module, cls, version="v69.0")._api_version == "69.0", cls
        if cls in NO_DEFAULT:
            assert _raises(lambda: _task(module, cls, version=None)._api_version), cls
        else:
            assert _task(module, cls, version=None)._api_version == "68.0", cls  # prior hardcoded fallback kept
        if cls in TAKES_OPTION:
            assert _task(module, cls, options={"api_version": "v70.0"})._api_version == "70.0", cls


def test_method_sites_read_project_version():
    for module, cls, read, takes_option, has_default in METHODS:
        assert read(_task(module, cls)) == "69.0", cls
        if has_default:
            assert read(_task(module, cls, version=None)) == "68.0", cls
        else:
            assert _raises(lambda: read(_task(module, cls, version=None))), cls
        if takes_option:
            assert read(_task(module, cls, options={"api_version": "v70.0"})) == "70.0", cls


# ---- pack 495: every remaining task reads the version through project_api_version ----

class Probe(Exception):
    """Carries what a stubbed call saw (not a RequestException, so no task swallows it)."""

    def __init__(self, seen):
        super().__init__(seen)
        self.seen = seen


def _probe_requests():
    """Replace requests' verbs so a call raises Probe(url); returns a restore function."""
    import requests

    saved = {verb: getattr(requests, verb) for verb in ("get", "post", "patch", "put", "delete")}

    def make(_verb):
        def call(url, *args, **kwargs):
            raise Probe(url)
        return call

    for verb in saved:
        setattr(requests, verb, make(verb))
    return lambda: [setattr(requests, verb, fn) for verb, fn in saved.items()]


def _seen(fn):
    try:
        return fn()
    except Probe as probe:
        return probe.seen


def _urls(task):
    task.instance_url = "https://x.my.salesforce.com"
    task.access_token = "t"
    task.logger = logging.getLogger("t")
    return task


def _billing(t):
    import tempfile

    plan = Path(tempfile.mkdtemp())
    (plan / "SequencePolicies.json").write_text('[{"name": "p"}]')
    t.options = {"plan_dir": str(plan)}
    t.sf = types.SimpleNamespace(query=lambda soql: {"records": []})
    t._build_ref_id_cache = lambda policies: {}
    t._build_body = lambda policy, cache: {}
    return _seen(t._run_task)


def _configure_search_index(t):
    import tempfile

    path = Path(tempfile.mkdtemp()) / "c.json"
    path.write_text('{"indexConfigurations": [{"a": 1}]}')
    t.options = {"path": str(path)}
    return _seen(t._run_task)


def _context_service(t):
    t._load_keychain = lambda: None
    t._prep_runtime()
    return t.api_version


def _stamp_commit(t):
    import json
    import tempfile

    temp = tempfile.mkdtemp()
    t._write_sfdx_project(temp)
    return json.loads((Path(temp) / "sfdx-project.json").read_text())["sourceApiVersion"]


def _reorder(t):
    import tempfile

    root = Path(tempfile.mkdtemp())
    (root / "s.robot").write_text("")
    t.project_config.repo_root = str(root)
    t.org_config.username = "u"
    t.options = {"suite": "s.robot"}

    def build(labels, api_version):
        raise Probe(api_version)

    t._build_ordered_app_ids = build
    return _seen(t._run_task)


def _ux(t):
    import tasks.rlm_ux_assembly as mod

    t.project_config.repo_root = str(REPO)
    t.logger = logging.getLogger("t")
    t.options = {"deploy": False}

    class Assembler:
        def __init__(self, ctx):
            self.ctx = ctx

        def run(self, *args):
            raise Probe(self.ctx.api_version)

    saved, mod.UxAssembler = mod.UxAssembler, Assembler
    try:
        return _seen(t._run_task)
    finally:
        mod.UxAssembler = saved


def _pinned(module):
    """The version a `_sf` client is pinned to; None when the task fell back to the org's own client."""
    def read(t):
        mod = importlib.import_module(module)
        t.org_config.salesforce_client = "ORG"
        t.logger = logging.getLogger("t")
        saved, mod.Salesforce = mod.Salesforce, lambda **kw: kw["version"]
        try:
            client = t._sf
        finally:
            mod.Salesforce = saved
        return None if client == "ORG" else client
    return read


def _pinned_decision_tables(t):
    mod = importlib.import_module("tasks.rlm_manage_decision_tables")
    t.org_config.salesforce_client = "ORG"
    t.logger = logging.getLogger("t")
    saved, mod.Salesforce = mod.Salesforce, lambda **kw: kw["version"]
    try:
        client = t._pinned_salesforce_client()
    finally:
        mod.Salesforce = saved
    return None if client == "ORG" else client


def _rebuild(t):
    t.options = {"raise_on_failure": True}  # the warn-and-continue path: test_tolerant_tasks_warn_on_an_unset_version
    return _seen(t._run_task)


def _in_url(url):
    return url.split("/services/data/v", 1)[1].split("/", 1)[0]


# (module, class, read -> version text, unset behaviour: "raises" or the default/None expected)
SWEEP = [
    ("tasks.rlm_sync_pricing_data", "SyncPricingData", lambda t: _in_url(_urls(t)._build_url_and_headers("e")[0]), "raises"),
    ("tasks.rlm_refresh_decision_table", "RefreshDecisionTable", lambda t: _in_url(_urls(t)._build_url_and_headers("e")[0]), "raises"),
    ("tasks.rlm_extend_stdctx", "ExtendStandardContext", lambda t: _in_url(_urls(t)._build_url_and_headers("e")[0]), "raises"),
    ("tasks.rlm_enable_change_data_capture", "EnableChangeDataCapture", lambda t: _in_url(t._tooling_url("q")), "raises"),
    ("tasks.rlm_billing", "CreateSequencePolicies", lambda t: _in_url(_billing(t)), "raises"),
    ("tasks.rlm_configure_search_index", "ConfigureSearchIndex", lambda t: _in_url(_configure_search_index(t)), "raises"),
    ("tasks.rlm_rebuild_search_index", "RebuildSearchIndex", lambda t: _in_url(_rebuild(t)), "raises"),
    ("tasks.rlm_rebuild_search_index", "CheckSearchIndexReadiness", lambda t: _in_url(_rebuild(t)), "raises"),
    ("tasks.rlm_context_service", "ManageContextDefinition", _context_service, "raises"),
    ("tasks.rlm_stamp_commit", "StampGitCommit", _stamp_commit, "raises"),
    ("tasks.rlm_reorder_app_launcher", "ReorderAppLauncher", _reorder, "raises"),
    ("tasks.rlm_create_persona_user", "CreatePersonaUser", lambda t: t._api_version(), "68.0"),
    ("tasks.rlm_publish_agents", "PublishAgents", lambda t: t._api_version(), "68.0"),
    ("tasks.rlm_create_approval_email_templates", "CreateApprovalEmailTemplates",
     lambda t: _in_url(t._api_headers()[1]), "68.0"),
    ("tasks.rlm_ux_assembly", "AssembleAndDeployUX", _ux, UX_DEFAULT_API_VERSION),
    ("tasks.rlm_deploy_expression_sets", "DeployExpressionSets", _pinned("tasks.rlm_deploy_expression_sets"), None),
    ("tasks.rlm_deactivate_changed_decision_tables", "DeactivateChangedDecisionTables",
     _pinned("tasks.rlm_deactivate_changed_decision_tables"), None),
    ("tasks.rlm_manage_decision_tables", "ManageDecisionTables", _pinned_decision_tables, None),
]


def test_sweep_sites_read_project_version():
    restore = _probe_requests()
    try:
        for module, cls, read, unset in SWEEP:
            label = f"{module}.{cls}"
            assert read(_task(module, cls, version="v69.0")) == "69.0", label
            assert read(_task(module, cls, version="69.0")) == "69.0", label
            if unset == "raises":
                assert _raises(lambda: read(_task(module, cls, version=None))), label
            else:
                assert read(_task(module, cls, version=None)) == unset, label
    finally:
        restore()


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def _tolerant(module, cls, setup, raise_on_failure):
    """Run a warn-and-continue task with no API version; (raised message or None, warnings, request url or None)."""
    t = _task(module, cls, version=None)
    t.logger = logging.getLogger(f"tolerant.{cls}")
    capture = _Capture()
    t.logger.addHandler(capture)
    setup(t, raise_on_failure)
    try:
        t._run_task()
    except Probe as probe:
        return None, capture.messages, probe.seen
    except Exception as exc:  # noqa: BLE001 (cumulusci's exception classes)
        return str(exc), capture.messages, None
    finally:
        t.logger.removeHandler(capture)
    return None, capture.messages, None


def _setup_rebuild(t, strict):
    t.options = {"raise_on_failure": strict}


def _setup_configure(t, strict):
    import tempfile

    path = Path(tempfile.mkdtemp()) / "c.json"
    path.write_text('{"indexConfigurations": [{"a": 1}]}')
    t.options = {"path": str(path), "raise_on_failure": strict}


def _setup_cdc(t, strict):
    t.raise_on_failure = strict


def _setup_stamp(t, strict):
    t.org_config.username = "u"
    t.options = {}
    t._git = lambda *args: "abc"
    t._resolve_branch = lambda short: "b"
    t._is_dirty_tree = lambda: False
    t._resolve_org_definition = lambda: "dev"
    t._resolve_feature_flags = lambda: {}

    def deploy(temp_dir, username):
        raise Probe("deployed")

    t._deploy = deploy


# Tasks whose contract is "warn and continue" (unless raise_on_failure): an unset version must
# take that path too, not escape as an exception (pack 495 review). StampGitCommit never fails.
TOLERANT = [
    ("tasks.rlm_rebuild_search_index", "RebuildSearchIndex", _setup_rebuild, True),
    ("tasks.rlm_configure_search_index", "ConfigureSearchIndex", _setup_configure, True),
    ("tasks.rlm_enable_change_data_capture", "EnableChangeDataCapture", _setup_cdc, True),
    ("tasks.rlm_stamp_commit", "StampGitCommit", _setup_stamp, False),
]


def test_tolerant_tasks_warn_on_an_unset_version():
    restore = _probe_requests()
    try:
        for module, cls, setup, can_raise in TOLERANT:
            raised, warnings, request = _tolerant(module, cls, setup, False)
            assert raised is None and request is None, (cls, raised, request)
            assert any("No API version" in w for w in warnings), (cls, warnings)
            if can_raise:
                raised, _, request = _tolerant(module, cls, setup, True)
                assert raised and "No API version" in raised and request is None, (cls, raised, request)
    finally:
        restore()


def test_no_task_module_reads_the_project_version_directly():
    """Only soql_utils.project_api_version touches project__package__api_version."""
    hits = [path.name for path in sorted((REPO / "tasks").glob("*.py"))
            if path.name != "soql_utils.py" and "project__package__api_version" in path.read_text()]
    assert not hits, hits


def _org_config_api_version_reads(source):
    """Lines that read api_version off an org_config, as `x.org_config.api_version` or getattr(x.org_config, "api_version")."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Attribute) and node.attr == "api_version":
            target = node.value
        elif (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "getattr" and len(node.args) >= 2
              and isinstance(node.args[1], ast.Constant) and node.args[1].value == "api_version"):
            target = node.args[0]
        else:
            continue
        name = getattr(target, "attr", None) or getattr(target, "id", None)
        if name == "org_config":
            hits.append(node.lineno)
    return hits


def test_no_task_reads_org_config_api_version():
    assert _org_config_api_version_reads('v = getattr(\n    self.org_config,\n    "api_version",\n    None,\n)\n') == [1]
    assert _org_config_api_version_reads("v = self.org_config.api_version") == [1]
    hits = [f"{path.name}:{n}" for path in sorted((REPO / "tasks").glob("*.py"))
            for n in _org_config_api_version_reads(path.read_text())]
    assert not hits, hits


def test_helper_default_and_error():
    cfg = types.SimpleNamespace(project__package__api_version=None)
    assert project_api_version(cfg, default="68.0") == "68.0"
    assert project_api_version(types.SimpleNamespace(), default="68.0") == "68.0"
    try:
        project_api_version(cfg, KeyError)
    except KeyError:
        pass
    else:
        raise AssertionError("expected the error class")
    assert project_api_version(types.SimpleNamespace(project__package__api_version="v68.0")) == "68.0"
    assert project_api_version(cfg, default="68.0", option=" v70.0 ") == "70.0"
    assert project_api_version(types.SimpleNamespace(project__package__api_version="69.0"), option="") == "69.0"
    assert project_api_version(types.SimpleNamespace(project__package__api_version="69.0"), option="  ") == "69.0"


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL  {name}  {type(exc).__name__}: {exc}")
    print(f"{len(tests) - failed}/{len(tests)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

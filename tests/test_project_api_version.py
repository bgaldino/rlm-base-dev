"""Tasks resolve the API version from project config; OrgConfig has no api_version (pack 479)."""
import ast
import importlib
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import repo `tasks.*` modules before cumulusci: its project_config empties tasks.__path__ (see rlm_manage_flows).
import tasks.expression_set_schema  # noqa: E402,F401
from tasks.soql_utils import project_api_version  # noqa: E402


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

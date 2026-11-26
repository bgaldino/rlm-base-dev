"""Tasks resolve the API version from project config; OrgConfig has no api_version (pack 479)."""
import importlib
import re
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
]


def test_property_reads_project_version():
  for module, cls in PROPERTIES:
    assert _task(module, cls)._api_version == "69.0"
    assert _task(module, cls, version="v69.0")._api_version == "69.0"
    assert _task(module, cls, version=None)._api_version == "68.0"  # prior hardcoded fallback kept


def test_method_sites_read_project_version():
    t = _task("tasks.rlm_recalculate_permission_set_groups", "RecalculatePermissionSetGroups")
    assert t._api_version() == "69.0"
    t = _task("tasks.rlm_configure_pricing_recipe_table_mappings", "ConfigurePricingRecipeTableMappings")
    assert t._get_api_context()[2] == "69.0"
    t = _task("tasks.rlm_configure_pricing_recipe_table_mappings", "ConfigurePricingRecipeTableMappings",
              options={"api_version": "70.0"})
    assert t._get_api_context()[2] == "70.0"


def test_no_task_reads_org_config_api_version():
    pat = re.compile(r'org_config\.api_version|org_config,\s*"api_version"')
    hits = []
    for path in (REPO / "tasks").glob("*.py"):
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if path.name != "soql_utils.py" and pat.search(line) and not line.lstrip().startswith("#"):
                hits.append(f"{path.name}:{n}")
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

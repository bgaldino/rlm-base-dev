#!/usr/bin/env python3
"""
Offline checks for tasks/rlm_deploy_expression_sets.py (the post-deploy version read-back).

    python tests/test_deploy_expression_sets.py

No org and no CumulusCI install: the module degrades on ImportError, and the org's
ExpressionSetVersion rows are faked. Why it exists (todo packs 172, 175): a deploy of
the repo's ``_V1`` succeeds and changes no price when the org executes a later version
of the same definition, or when the deploy handler skips a version whose DeveloperName
exists under a different VersionNumber. The read-back turns both into a failed build.
"""
import importlib.util
import logging
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "_rlm_test_deploy_expression_sets", REPO / "tasks" / "rlm_deploy_expression_sets.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}{'' if condition else ' — ' + str(detail)}")
    if not condition:
        failures.append(label)


PRICING = "RLM_DefaultPricingProcedure"
V1 = f"{PRICING}_V1"
# ramp264's version chain (packs 172/175): three active, the highest active (v40) executes.
RAMP264 = [
    {"ApiName": V1, "VersionNumber": 1, "IsActive": True},
    {"ApiName": f"{PRICING}_RLM_Rev_Mgmt_Def_and_Promo_Price_Proc_v20", "VersionNumber": 2,
     "IsActive": False},
    {"ApiName": f"{PRICING}_RLM_Rev_Mgmt_Def_and_Partner_Price_Proc_v30", "VersionNumber": 3,
     "IsActive": True},
    {"ApiName": f"{PRICING}_RLM_Rev_Mgmt_Def_Partner_Price_and_Ramp_v40", "VersionNumber": 4,
     "IsActive": True},
]
DRAFT_TO_ACTIVE = [{"transform": "find_replace", "options": {"patterns": [
    {"xpath": '//ExpressionSetDefinition/versions/status[text()="Draft"]', "replace": "Active",
     "api": "rest"},
    {"xpath": "//x/value[text()=\"__ID__\"]", "replace_record_id_query": "SELECT Id FROM X"},
]}}]


def expected(name=PRICING, api=V1, number=1, status="Draft"):
    return {"definition": name, "apiName": api, "versionNumber": number, "status": status}


# ---------------------------------------------------------------------------
print("\n[1] what the repo deploys")

shipped = mod.repo_versions(REPO / "force-app" / "main" / "default" / "expressionSetDefinition")
pricing = [v for v in shipped if v["definition"] == PRICING]
check("every shipped definition is read",
      len({v["definition"] for v in shipped}) == len(list(
          (REPO / "force-app/main/default/expressionSetDefinition").glob("*.expressionSetDefinition-meta.xml"))),
      shipped)
check("the pricing procedure ships one Draft version _V1, VersionNumber 1",
      pricing == [dict(expected(), file=f"{PRICING}.expressionSetDefinition-meta.xml")], pricing)
check("a missing path yields nothing", mod.repo_versions(REPO / "no-such-dir") == [])

check("the Draft→Active find_replace transform is recognised",
      mod.draft_deploys_active(DRAFT_TO_ACTIVE) is True)
check("no transforms → Draft stays Draft", mod.draft_deploys_active(None) is False)
check("a transform that only swaps record ids does not count",
      mod.draft_deploys_active([{"transform": "find_replace", "options": {"patterns": [
          DRAFT_TO_ACTIVE[0]["options"]["patterns"][1]]}}]) is False)

yml = (REPO / "cumulusci.yml").read_text(encoding="utf-8")
block = re.search(r"^  activate_and_deploy_expression_sets:\n(.*?)(?=^  \S)", yml, re.S | re.M)
body = block.group(1) if block else ""
check("activate_and_deploy_expression_sets runs this task class",
      "class_path: tasks.rlm_deploy_expression_sets.DeployExpressionSets" in body, body[:300])
check("its version_check is the safe default (fail)", "version_check: fail" in body)
check("its transforms still flip Draft to Active",
      'versions/status[text()="Draft"]' in body and "replace: Active" in body)

# ---------------------------------------------------------------------------
print("\n[2] read-back findings")

fresh = {PRICING: [{"ApiName": V1, "VersionNumber": 1, "IsActive": True}]}
check("a fresh single-version org has no finding",
      mod.version_findings([expected()], fresh, True) == [])

chain = mod.version_findings([expected()], {PRICING: RAMP264}, True)
check("a ramp264-style chain is a finding: _V1 is active but v40 executes",
      len(chain) == 1 and "does not execute" in chain[0]
      and "Partner_Price_and_Ramp_v40 (v4)" in chain[0], chain)
check("the chain finding points at set_step_formula.py and the warn option",
      chain and "set_step_formula.py" in chain[0] and "version_check" in chain[0], chain)

noop = mod.version_findings(
    [expected()], {PRICING: [{"ApiName": V1, "VersionNumber": 2, "IsActive": True}]}, True)
check("same DeveloperName under another VersionNumber is the silent no-op finding",
      len(noop) == 1 and "silent" in noop[0] and "VersionNumber 2" in noop[0], noop)

missing = mod.version_findings([expected()], {PRICING: RAMP264[1:]}, True)
check("a deployed version absent from the org is a finding",
      len(missing) == 1 and "no ExpressionSetVersion named" in missing[0], missing)
check("a definition with no rows at all is a finding",
      len(mod.version_findings([expected()], {}, True)) == 1)

inactive = mod.version_findings(
    [expected()], {PRICING: [{"ApiName": V1, "VersionNumber": 1, "IsActive": False}]}, True)
check("a version the deploy activates that reads inactive is a finding",
      len(inactive) == 1 and "inactive" in inactive[0], inactive)
check("without the Draft→Active transform a Draft version need not be active",
      mod.version_findings(
          [expected()], {PRICING: [{"ApiName": V1, "VersionNumber": 1, "IsActive": False}]},
          False) == [])
check("an Inactive-status version is checked for existence and number only",
      mod.version_findings([expected(status="Inactive")], {PRICING: RAMP264}, True) == [])
check("an Active-status version must execute even without the transform",
      len(mod.version_findings([expected(status="Active")], {PRICING: RAMP264}, False)) == 1)
check("the executing version itself passes",
      mod.version_findings([expected(api=RAMP264[3]["ApiName"], number=4)],
                           {PRICING: RAMP264}, True) == [])


# ---------------------------------------------------------------------------
print("\n[3] the task: two queries, fail by default, warn on request")


class _FakeSf:
    def __init__(self, sets, versions):
        self.sets, self.versions, self.queries = sets, versions, []

    def query_all(self, soql):
        self.queries.append(soql)
        if "FROM ExpressionSetVersion" in soql:
            return {"records": self.versions}
        return {"records": self.sets}


def make_task(mode, rows, tmp):
    task = object.__new__(mod.DeployExpressionSets)
    task.logs = []

    class _Capture(logging.Handler):
        def emit(handler, record):
            task.logs.append((record.levelname, record.getMessage()))

    task.logger = logging.getLogger(f"test_deploy_es_{id(task)}")
    task.logger.addHandler(_Capture())
    task.logger.setLevel(logging.INFO)
    task.logger.propagate = False
    task.options = {"path": str(tmp), "transforms": DRAFT_TO_ACTIVE, "version_check": mode}
    task.version_check = mode
    task._sf_client = _FakeSf(
        [{"Id": "9QLx", "ExpressionSetDefinition": {"DeveloperName": PRICING}}],
        [dict(r, ExpressionSetId="9QLx") for r in rows],
    )
    return task


import shutil  # noqa: E402
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    shutil.copy(REPO / "force-app/main/default/expressionSetDefinition"
                / f"{PRICING}.expressionSetDefinition-meta.xml", tmp)

    ok = make_task("fail", fresh[PRICING], tmp)
    ok._check_versions()
    check("a clean read-back passes and says so",
          any("Version read-back: all 1" in m for _, m in ok.logs), ok.logs)
    check("the read-back takes two queries, not one per definition",
          len(ok._sf_client.queries) == 2, ok._sf_client.queries)

    failing = make_task("fail", RAMP264, tmp)
    try:
        failing._check_versions()
        raised = None
    except mod.CumulusCIFailure as exc:
        raised = exc
    check("version_check fail raises on a chain", raised is not None, failing.logs)
    check("the failure says how to continue anyway",
          raised is not None and "version_check warn" in str(raised), raised)
    check("each finding is logged as an error",
          any(level == "ERROR" and "does not execute" in m for level, m in failing.logs),
          failing.logs)

    warning = make_task("warn", RAMP264, tmp)
    warning._check_versions()
    check("version_check warn logs the finding as a warning and continues",
          any(level == "WARNING" and "does not execute" in m for level, m in warning.logs)
          and not any(level == "ERROR" for level, _ in warning.logs), warning.logs)

    empty = make_task("fail", [], Path(td) / "none")
    empty._check_versions()
    check("no repo versions → nothing to read back, no query",
          empty._sf_client.queries == [], empty._sf_client.queries)

check("the option is declared on the task",
      "version_check" in mod.DeployExpressionSets.task_options)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("all checks passed")

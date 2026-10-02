#!/usr/bin/env python3
"""
Offline checks for tasks/rlm_deactivate_changed_decision_tables.py and its flow wiring.

    python tests/test_deactivate_changed_decision_tables.py

No org required, and no CumulusCI install: the module degrades on ImportError. The org
and the check-only deploy are faked; the failure text is in the shape CCI's
ApiDeploy._process_response builds ("<Action> of DecisionTable <name>: <type>: <problem>").

Why this exists (todo 096): the task it replaced parked every Active table's XML in
`.skip/` before `deploy_pre`, so a change to a repo decision table never reached an
already-prepared org — and the build still went green. The checks below pin the
replacement's one job: deactivate exactly the tables the platform refuses to edit in
place, and never hide a change or a failure.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml

_spec = importlib.util.spec_from_file_location(
    "_rlm_test_deactivate_changed_dt", REPO / "tasks" / "rlm_deactivate_changed_decision_tables.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}{'' if condition else ' — ' + str(detail)}")
    if not condition:
        failures.append(label)


ACTIVE_EDIT = "Update of DecisionTable {}: Error: Can't edit an active Decision Table"
OTHER = "Update of DecisionTable {}: Error: Invalid field Foo__c"


# ---------------------------------------------------------------------------
print("\n[1] parsing the check-only failure")

text = "\n\n".join([ACTIVE_EDIT.format("RLM_A"), OTHER.format("RLM_B")])
check("attributes the active-edit failure to its table only",
      mod.tables_blocked_by_active_edit(text, ["RLM_A", "RLM_B"]) == {"RLM_A"},
      mod.tables_blocked_by_active_edit(text, ["RLM_A", "RLM_B"]))
check("a non-active-edit failure is reported, not treated as blocked",
      mod.other_failures(text) == [OTHER.format("RLM_B")], mod.other_failures(text))
check("no active-edit failure -> nothing blocked",
      mod.tables_blocked_by_active_edit(OTHER.format("RLM_A"), ["RLM_A"]) == set())
check("an unattributable active-edit failure blocks every candidate",
      mod.tables_blocked_by_active_edit("Can't edit an active Decision Table", ["RLM_A", "RLM_B"])
      == {"RLM_A", "RLM_B"})
check("a curly apostrophe still matches",
      mod.tables_blocked_by_active_edit(ACTIVE_EDIT.format("RLM_A").replace("'", "’"), ["RLM_A"])
      == {"RLM_A"})


# ---------------------------------------------------------------------------
print("\n[2] candidates come from the repo files, not a hardcoded list")

pre = mod.repo_table_names(REPO / "unpackaged/pre/5_decisiontables")
check("pre tables discovered from files",
      pre == ["RLM_CostBookEntries", "RLM_ProductCategoryQualification", "RLM_ProductQualification"], pre)
prm = mod.repo_table_names(REPO / "unpackaged/post_prm_pricing/decisionTables")
check("PRM table discovered from files", prm == ["RLM_Channel_Program_Level_Partner"], prm)
check("a missing directory yields no candidates", mod.repo_table_names(REPO / "no/such/dir") == [])


# ---------------------------------------------------------------------------
print("\n[3] the task's decisions against a faked org")


class _Logger:
    def __init__(self):
        self.lines = []

    def info(self, msg, *a):
        self.lines.append(("info", msg % a if a else msg))

    def warning(self, msg, *a):
        self.lines.append(("warning", msg % a if a else msg))

    def error(self, msg, *a):
        self.lines.append(("error", msg % a if a else msg))


class _DecisionTable:
    def __init__(self, fail_on=None):
        self.updates = []
        self.fail_on = fail_on

    def update(self, record_id, body):
        if (record_id, body) == self.fail_on:
            raise Exception("UNABLE_TO_LOCK_ROW")
        self.updates.append((record_id, body))


class _Sf:
    def __init__(self, active, query_error=None, update_fail_on=None):
        self.active = active
        self.query_error = query_error
        self.queries = []
        self.DecisionTable = _DecisionTable(update_fail_on)

    def query(self, soql):
        self.queries.append(soql)
        if self.query_error:
            raise Exception(self.query_error)
        return {"records": [{"Id": f"id_{n}", "DeveloperName": n} for n in self.active]}


def run(files, active, check_failure=None, deploy_failure=None, query_error=None, skipped=(),
        update_fail_on=None):
    """Run the task over a temp table dir. Returns (sf, deploys, logger, dir, task).

    ``deploys`` lists each deploy as {"names", "check_only"}; the check-only one is first.
    """
    tmp = Path(tempfile.mkdtemp())
    for name in files:
        (tmp / f"{name}{mod.DECISION_TABLE_SUFFIX}").write_text("<DecisionTable/>")
    if skipped:
        (tmp / ".skip").mkdir()
        for name in skipped:
            (tmp / ".skip" / f"{name}{mod.DECISION_TABLE_SUFFIX}").write_text("<DecisionTable/>")

    task = object.__new__(mod.DeactivateChangedDecisionTables)
    task.options = {"path": str(tmp)}
    task.logger = _Logger()
    sf = _Sf(active, query_error, update_fail_on)
    task._sf_client = sf
    deploys = []

    def fake_get_api():
        # The no-argument signature: the staged dir must arrive through options["path"].
        deploys.append({
            "names": sorted(p.name for p in Path(task.options["path"]).iterdir()),
            "check_only": task.check_only,
        })
        failure = check_failure if task.check_only else deploy_failure

        def call():
            if failure:
                # The shape ApiDeploy.__call__ really raises: the component failure
                # re-wrapped as MetadataParseError, a MetadataApiError (measured on 264).
                raise mod.MetadataApiError(mod.MDAPI_WRAPPER_PREFIX + failure, None)
        return call

    task._get_api = fake_get_api
    error = None
    try:
        task._run_task()
    except Exception as e:  # noqa: BLE001 - the caller asserts on it
        error = e
    task.raised = error
    return sf, deploys, task.logger, tmp, task


def _file(name):
    return f"{name}{mod.DECISION_TABLE_SUFFIX}"


sf, deploys, _log, _, task = run(["RLM_A", "RLM_B"], active=[])
check("nothing Active -> no deploy, no deactivation",
      not deploys and not sf.DecisionTable.updates, (deploys, sf.DecisionTable.updates))

sf, deploys, _log, tmp, task = run(["RLM_A", "RLM_B"], active=["RLM_A", "RLM_B"])
check("check-only accepts -> tables stay Active (the bundle deploy applies in place)",
      sf.DecisionTable.updates == [] and len(deploys) == 1, (sf.DecisionTable.updates, deploys))
check("the check-only deploy really is check-only", deploys[0]["check_only"] is True, deploys)
check("options['path'] and check_only are restored afterwards",
      task.options["path"] == str(tmp) and task.check_only is False, (task.options, task.check_only))

sf, deploys, log, tmp, task = run(["RLM_A", "RLM_B", "RLM_C"], active=["RLM_A", "RLM_B"],
                                  check_failure=ACTIVE_EDIT.format("RLM_A"))
check("only the Active tables' files are staged for the check",
      deploys[0]["names"] == [_file("RLM_A"), _file("RLM_B")], deploys)
check("only the table rejected for the active-edit restriction is deactivated",
      sf.DecisionTable.updates == [("id_RLM_A", {"Status": "Inactive"})], sf.DecisionTable.updates)
check("... and it is deployed by the task itself, for real, straight after",
      len(deploys) == 2 and deploys[1] == {"names": [_file("RLM_A")], "check_only": False}, deploys)
check("... which succeeds without raising", task.raised is None, task.raised)

sf, deploys, log, _, task = run(["RLM_A", "RLM_B"], active=["RLM_A", "RLM_B"],
                                check_failure=ACTIVE_EDIT.format("RLM_A"),
                                deploy_failure=OTHER.format("RLM_A"))
check("a failed deploy reactivates what was deactivated",
      sf.DecisionTable.updates == [("id_RLM_A", {"Status": "Inactive"}), ("id_RLM_A", {"Status": "Active"})],
      sf.DecisionTable.updates)
check("... and fails the task with the platform's reason",
      isinstance(task.raised, mod.MetadataApiError) and "Invalid field Foo__c" in str(task.raised)
      and "reactivated unchanged" in str(task.raised), task.raised)

sf, deploys, log, _, task = run(["RLM_A", "RLM_B"], active=["RLM_A", "RLM_B"],
                                check_failure="\n\n".join([ACTIVE_EDIT.format("RLM_A"), ACTIVE_EDIT.format("RLM_B")]),
                                update_fail_on=("id_RLM_B", {"Status": "Inactive"}))
check("a deactivation failing part-way reactivates the ones already deactivated",
      sf.DecisionTable.updates == [("id_RLM_A", {"Status": "Inactive"}), ("id_RLM_A", {"Status": "Active"})],
      sf.DecisionTable.updates)
check("... deploys nothing for real, and raises", len(deploys) == 1 and task.raised is not None,
      (deploys, task.raised))

sf, deploys, log, _, task = run(["RLM_A"], active=["RLM_A"],
                                check_failure=ACTIVE_EDIT.format("RLM_A"),
                                deploy_failure=OTHER.format("RLM_A"),
                                update_fail_on=("id_RLM_A", {"Status": "Active"}))
check("a reactivation that fails is logged as an error naming the recovery command",
      any(lvl == "error" and "manage_decision_tables" in msg for lvl, msg in log.lines), log.lines)
check("... and the raised error says the table is still Inactive, not that it was reactivated",
      "could NOT be reactivated" in str(task.raised) and "reactivated unchanged" not in str(task.raised),
      task.raised)

sf, deploys, log, _, task = run(["RLM_A", "RLM_B"], active=["RLM_A", "RLM_B"],
                                check_failure="\n\n".join([ACTIVE_EDIT.format("RLM_A"), OTHER.format("RLM_B")]))
check("a mixed result deactivates nothing — the bundle deploy would fail anyway",
      sf.DecisionTable.updates == [] and len(deploys) == 1, (sf.DecisionTable.updates, deploys))
check("the other failure is surfaced as a warning",
      any(lvl == "warning" and "Invalid field Foo__c" in msg for lvl, msg in log.lines), log.lines)
check("... without the MDAPI wrapper prefix",
      not any(mod.MDAPI_WRAPPER_PREFIX in msg for _lvl, msg in log.lines), log.lines)

sf, deploys, log, _, task = run(["RLM_A"], active=["RLM_A"],
                                query_error="INVALID_TYPE: sObject type 'DecisionTable' is not supported")
check("fresh org (INVALID_TYPE) -> no deploy, no deactivation",
      not deploys and not sf.DecisionTable.updates)

sf, deploys, log, tmp, task = run(["RLM_A"], active=["RLM_A"], query_error="Session expired")
check("an unknown query error deactivates nothing and excludes nothing",
      not deploys and not sf.DecisionTable.updates and (tmp / _file("RLM_A")).exists())
check("... and says so", any(lvl == "warning" and "deactivating nothing" in msg for lvl, msg in log.lines),
      log.lines)

sf, deploys, _log, tmp, task = run(["RLM_A"], active=[], skipped=["RLM_B"])
check("a table left in .skip/ by an aborted run of the retired task is moved back",
      (tmp / _file("RLM_B")).exists() and "RLM_B" in sf.queries[0], sf.queries)

sf, deploys, _log, tmp, task = run(["RLM_A", "RLM_B"], active=[])
check("the query is scoped to the repo's tables and to Active",
      "IN ('RLM_A', 'RLM_B')" in sf.queries[0] and "Status = 'Active'" in sf.queries[0], sf.queries)


# ---------------------------------------------------------------------------
print("\n[4] flow wiring")

cci = yaml.safe_load((REPO / "cumulusci.yml").read_text())
tasks, flows = cci["tasks"], cci["flows"]


def step_tasks(flow):
    return {int(k): v.get("task") or v.get("flow") for k, v in flows[flow]["steps"].items()}


core = step_tasks("prepare_core")
check("prepare_core deactivates changed tables immediately before deploy_pre",
      core.get(6) == "deactivate_changed_decision_tables" and core.get(7) == "deploy_pre", core)
check("nothing in cumulusci.yml still runs the retired exclude/restore tasks",
      not {"exclude_active_decision_tables", "restore_decision_tables"} & (set(tasks) | {
          t for f in flows for t in step_tasks(f).values()}))

prm = step_tasks("deploy_post_prm_pricing")
deploy_at = next(n for n, t in prm.items() if t == "deploy_post_prm_pricing_decision_tables")
check("the PRM table deploy is immediately preceded by its deactivate step",
      prm.get(deploy_at - 1) == "deactivate_changed_post_prm_pricing_decision_tables", prm)
check("... under the same feature-flag condition",
      flows["deploy_post_prm_pricing"]["steps"][deploy_at - 1].get("when")
      == flows["deploy_post_prm_pricing"]["steps"][deploy_at].get("when"))

pre_paths = {Path(p).name for p in [tasks["deactivate_changed_decision_tables"]["options"]["path"]]}
check("the pre deactivate task points at the directory deploy_pre deploys the tables from",
      Path(tasks["deactivate_changed_decision_tables"]["options"]["path"]).parent.as_posix()
      == tasks["deploy_pre"]["options"]["path"])
check("the PRM deactivate task points at the PRM deploy task's path",
      tasks["deactivate_changed_post_prm_pricing_decision_tables"]["options"]["path"]
      == tasks["deploy_post_prm_pricing_decision_tables"]["options"]["path"])
for name in ("deactivate_changed_decision_tables", "deactivate_changed_post_prm_pricing_decision_tables"):
    check(f"{name} uses the new class",
          tasks[name]["class_path"]
          == "tasks.rlm_deactivate_changed_decision_tables.DeactivateChangedDecisionTables")


print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {failures}")
    sys.exit(1)
print("All checks passed.")

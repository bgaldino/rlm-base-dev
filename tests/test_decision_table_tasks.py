#!/usr/bin/env python3
"""
Offline regression tests for the decision-table refresh path.

Every assertion here exists because the thing it checks was BROKEN and shipped, or —
in the flow-shape case — was broken in a draft and caught only by hand. None of it
needs an org or a CumulusCI install: both task modules degrade on ImportError, the
same property `tests/test_rlm_apex_file.py` relies on.

    python tests/test_decision_table_tasks.py

Modelled on `tests/test_rlm_apex_file.py`, which exists solely because
FileBasedAnonymousApexTask shipped with `salesforce_task = False`. That defect class
then recurred twice more in this feature, which is what this file is for.
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml


def load_task_module(stem):
    """
    Load a module from `tasks/` by explicit file path.

    ⚠ Not `from tasks.x import y`. `tasks/` has no `__init__.py`, so it is an implicit
    namespace package whose `__path__` is recomputed dynamically — and once one task
    module has pulled CumulusCI in, `tasks.__path__` collapses to `[]` and any SECOND
    `tasks.*` import fails with ModuleNotFoundError even though `sys.path` and the cwd
    are unchanged. `tests/test_rlm_apex_file.py` never hits this because it imports a
    single task module. Loading by path sidesteps the resolution entirely.
    """
    path = REPO / "tasks" / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(f"_rlm_test_{stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' — ' + detail) if detail else ''}")
        failures.append(label)


# ---------------------------------------------------------------------------
# 1. --org acceptance. Both classes rejected --org until 2026-07-27, so every
#    refresh silently ran against the CCI DEFAULT org (issue #320).
# ---------------------------------------------------------------------------
print("\n[1] salesforce_task is set on both decision-table task classes")

_manage = load_task_module("rlm_manage_decision_tables")
_refresh = load_task_module("rlm_refresh_decision_table")
ManageDecisionTables = _manage.ManageDecisionTables
RefreshDecisionTable = _refresh.RefreshDecisionTable
_as_name_list = _manage._as_name_list

check("ManageDecisionTables.salesforce_task is True", ManageDecisionTables.salesforce_task is True)
check("RefreshDecisionTable.salesforce_task is True", RefreshDecisionTable.salesforce_task is True)

# The flag alone does NOT bring an OAuth refresh — only BaseSalesforceTask overrides
# _update_credentials. Both classes hit the REST API directly, so both must override it
# themselves or an expired token means "refreshed nothing, reported success".
check(
    "ManageDecisionTables overrides _update_credentials",
    "_update_credentials" in vars(ManageDecisionTables),
)
check(
    "RefreshDecisionTable overrides _update_credentials",
    "_update_credentials" in vars(RefreshDecisionTable),
)

# ---------------------------------------------------------------------------
# 2. Name normalisation. A comma-separated CLI string used to become ONE name.
# ---------------------------------------------------------------------------
print("\n[2] _as_name_list splits, trims and rejects blanks")

check('"A,B,C" splits into three', _as_name_list("A,B,C", "x") == ["A", "B", "C"])
check('" A , B " trims', _as_name_list(" A , B ", "x") == ["A", "B"])
check("a real list passes through", _as_name_list(["A", "B"], "x") == ["A", "B"])
check("single name still works", _as_name_list("A", "x") == ["A"])

for bad, why in ((" , ", "all-blank string"), ([" ", ""], "all-blank list"), (5, "wrong type")):
    try:
        _as_name_list(bad, "x")
        check(f"{why} raises", False, "no exception")
    except Exception:
        check(f"{why} raises", True)

# ---------------------------------------------------------------------------
# 3. Boolean coercion. CCI hands CLI options through as strings, so "false" is
#    truthy and would silently select an incremental refresh.
# ---------------------------------------------------------------------------
print("\n[3] is_incremental coerces string CLI input")

process_bool_arg = _manage.process_bool_arg

check('"false" -> False', process_bool_arg("false") is False)
check('"true"  -> True', process_bool_arg("true") is True)
check("False   -> False", process_bool_arg(False) is False)

# ---------------------------------------------------------------------------
# 4. Flow shape. A draft of this very change created a duplicate step key, and
#    YAML silently kept the last one — deleting refresh_dt_commerce from the flow.
#    Caught by hand once; this is what catches it next time.
# ---------------------------------------------------------------------------
print("\n[4] refresh_all_decision_tables step keys are contiguous and complete")

with open(REPO / "cumulusci.yml") as fh:
    cci = yaml.safe_load(fh)

steps = cci["flows"]["refresh_all_decision_tables"]["steps"]
keys = sorted(steps)
check("step keys are 1..N contiguous", keys == list(range(1, len(keys) + 1)), str(keys))

tasks_in_flow = {s.get("task") for s in steps.values()}
for required in ("refresh_dt_default_pricing", "refresh_dt_commerce", "refresh_dt_prm_pricing"):
    check(f"{required} present in the flow", required in tasks_in_flow)

# refresh_dt_default_pricing was referenced by NO flow at all, which is why
# StandardTax was never refreshed in any build. It must stay unconditional.
default_pricing = [s for s in steps.values() if s.get("task") == "refresh_dt_default_pricing"]
check(
    "refresh_dt_default_pricing has no when: guard",
    bool(default_pricing) and "when" not in default_pricing[0],
)

# A TSO ships the Commerce tables regardless of the commerce flag.
commerce = [s for s in steps.values() if s.get("task") == "refresh_dt_commerce"]
check(
    "refresh_dt_commerce is gated on commerce OR tso",
    bool(commerce) and "tso" in commerce[0].get("when", "") and "commerce" in commerce[0].get("when", ""),
    commerce[0].get("when", "") if commerce else "step absent",
)

# ---------------------------------------------------------------------------
# 5. Operator-facing text must not contradict the flow.
# ---------------------------------------------------------------------------
print("\n[5] the Commerce task description reflects the tso gate")

desc = cci["tasks"]["refresh_dt_commerce"]["description"]
check("description mentions tso", "tso" in desc.lower(), desc)

print("\n" + "=" * 60)
if failures:
    print(f"{len(failures)} FAILED: {', '.join(failures)}")
    sys.exit(1)
print("All decision-table task checks passed.")

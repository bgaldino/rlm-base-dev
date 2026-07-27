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
import re
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
#
# ⚠ INVOKE the hook, do not just assert the attribute exists. An existence check passes
# if the body is replaced with `pass`, which is materially the original defect.


# ⚠ Record an ORDERED event sequence, not two independent booleans. A pair of flags is
# satisfied by `with save_if_changed(): pass` followed by refresh_oauth_token() OUTSIDE the
# block — which defeats the whole point, since save_if_changed diffs the config on exit and
# would see nothing to persist. Only the ordering enter → refresh → exit proves the refresh
# happened inside the persistence context.
class _FakeOrgConfig:
    def __init__(self, events):
        self.events = events
        self.refreshed_with = None

    def refresh_oauth_token(self, keychain):
        self.refreshed_with = keychain
        self.events.append("refresh")

    def save_if_changed(self):
        outer = self

        class _Ctx:
            def __enter__(self_inner):
                outer.events.append("enter")

            def __exit__(self_inner, *exc):
                outer.events.append("exit")
                return False

        return _Ctx()


class _FakeProjectConfig:
    def __init__(self, keychain):
        self.keychain = keychain


def credentials_hook_events(cls):
    """Invoke _update_credentials against fakes and return (events, refreshed_with_keychain)."""
    events = []
    sentinel = object()
    task = object.__new__(cls)
    task.org_config = _FakeOrgConfig(events)
    task.project_config = _FakeProjectConfig(sentinel)
    cls._update_credentials(task)
    return events, task.org_config.refreshed_with is sentinel


for cls in (ManageDecisionTables, RefreshDecisionTable):
    events, right_keychain = credentials_hook_events(cls)
    check(f"{cls.__name__}._update_credentials refreshes with the keychain", right_keychain)
    check(
        f"{cls.__name__} refreshes INSIDE save_if_changed (enter→refresh→exit)",
        events == ["enter", "refresh", "exit"],
        str(events),
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

# The offline fallback must match CumulusCI's real helper, INCLUDING raising on an
# uninterpretable value. A fallback that disagrees makes every check above prove the
# wrong thing when CumulusCI is absent.
try:
    process_bool_arg("maybe")
    check("uninterpretable value raises", False, "returned instead of raising")
except TypeError:
    check("uninterpretable value raises", True)

# ⚠ Exercise the TASK CALL SITES, not just the helper. Deleting the process_bool_arg
# call from either task leaves the three checks above green while "false" once again
# reaches the payload as a truthy string.


class _SilentLogger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class _Recorder:
    """Captures the payload each task hands to its transport."""

    def __init__(self):
        self.payloads = []


def manage_payload_for(raw_value):
    rec = _Recorder()
    task = object.__new__(ManageDecisionTables)
    task.options = {"developer_names": "A_Table", "is_incremental": raw_value}
    task.logger = _SilentLogger()
    task.org_config = object()
    task._sf_client = object()
    task._refresh_single_decision_table = lambda sf, name, inc: (
        rec.payloads.append(inc) or {"isSuccess": True, "outputValues": {"Status": "Queued"}}
    )
    ManageDecisionTables._refresh_decision_tables(task)
    return rec.payloads[0]


def refresh_payload_for(raw_value):
    rec = _Recorder()
    task = object.__new__(RefreshDecisionTable)
    task.options = {"developerNames": "A_Table", "isIncremental": raw_value}
    task.logger = _SilentLogger()
    task._prep_runtime = lambda: None
    task._refresh_decision_table = lambda name, inc: rec.payloads.append(inc)
    RefreshDecisionTable._run_task(task)
    return rec.payloads[0]


for label, fn in (("ManageDecisionTables", manage_payload_for), ("RefreshDecisionTable", refresh_payload_for)):
    try:
        got_false = fn("false")
        got_true = fn("true")
        check(f'{label} sends real False for "false"', got_false is False, repr(got_false))
        check(f'{label} sends real True for "true"', got_true is True, repr(got_true))
    except Exception as exc:  # surface rather than silently skip
        check(f"{label} boolean call-site check ran", False, f"{type(exc).__name__}: {exc}")

# The refresh module keeps its OWN offline fallback. Testing only the manage module's copy
# leaves the other free to drift back to plain truthiness while all checks stay green.
for mod_label, fn in (("manage", _manage.process_bool_arg), ("refresh", _refresh.process_bool_arg)):
    ok = fn("false") is False and fn("true") is True and fn(0) is False
    check(f"{mod_label} fallback vocabulary matches CCI", ok)
    try:
        fn("maybe")
        check(f"{mod_label} fallback raises on an uninterpretable value", False, "returned")
    except TypeError:
        check(f"{mod_label} fallback raises on an uninterpretable value", True)

# ---------------------------------------------------------------------------
# 3b. The status gate. Only an explicit Queued counts as accepted — everything
#     else, including a missing outputValues or an unrecognised value, is a
#     failure. Round 2 shipped "anything but Failed", which let the code's own
#     'Unknown' fallback claim a queue that never happened.
# ---------------------------------------------------------------------------
print("\n[3b] the status gate accepts ONLY an explicit Queued")

STATUS_CASES = [
    ({"isSuccess": True, "outputValues": {"Status": "Queued"}}, True, "Queued"),
    ({"isSuccess": True, "outputValues": {"Status": "queued"}}, True, "queued (case)"),
    ({"isSuccess": True, "outputValues": {"Status": "Failed"}}, False, "Failed"),
    ({"isSuccess": True, "outputValues": {"Status": "Accepted"}}, False, "unrecognised status"),
    ({"isSuccess": True, "outputValues": {}}, False, "missing Status"),
    ({"isSuccess": True}, False, "missing outputValues"),
    ({"isSuccess": False, "errors": [{"message": "nope"}]}, False, "isSuccess False"),
]


def manage_counts_success(response):
    """Drive ManageDecisionTables._refresh_decision_tables and report whether it counted a queue."""
    task = object.__new__(ManageDecisionTables)
    task.options = {"developer_names": "A_Table", "is_incremental": False}
    task.logger = _SilentLogger()
    task.org_config = object()
    task._sf_client = object()
    task._refresh_single_decision_table = lambda sf, name, inc: response
    try:
        ManageDecisionTables._refresh_decision_tables(task)
        return True  # no raise => fail_count was 0 => it counted a queue
    except Exception:
        return False  # raises "Failed to queue a refresh for N" when fail_count > 0


for response, should_queue, label in STATUS_CASES:
    got = manage_counts_success(response)
    check(
        f"ManageDecisionTables treats {label} as {'queued' if should_queue else 'NOT queued'}",
        got is should_queue,
        f"counted queued={got}",
    )

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
#
# ⚠ EVALUATE the expression across all four combinations. Asserting that the string
# merely contains "commerce" and "tso" passes for `commerce AND tso`, which would
# re-break the exact tso=true/commerce=false build the fix protects while leaving this
# check green.
commerce = [s for s in steps.values() if s.get("task") == "refresh_dt_commerce"]
when = commerce[0].get("when", "") if commerce else ""


# ⚠ CumulusCI evaluates `when:` with **Jinja2**, not Python — `cumulusci/core/flowrunner.py`
# builds an ImmutableSandboxedEnvironment (:71, :89) and calls compile_expression (:515).
# Use that engine when it is importable so the check is faithful. Python `eval` is the
# fallback, and the two differ in a way that matters: Jinja2 resolves an unknown attribute
# to a falsy Undefined and raises nothing, while `eval` raises AttributeError. The
# unknown-flag check below closes that gap in BOTH engines, which is why it is not optional.
try:
    from jinja2.sandbox import ImmutableSandboxedEnvironment

    _jinja_env = ImmutableSandboxedEnvironment()
except ImportError:  # jinja2 ships with CumulusCI; absent in the bare offline environment
    _jinja_env = None


def _flag_ctx(commerce_flag, tso_flag):
    class _Custom:
        pass

    custom = _Custom()
    setattr(custom, "project__custom__commerce", commerce_flag)
    setattr(custom, "project__custom__tso", tso_flag)
    return custom


def evaluate_when(expr, commerce_flag, tso_flag):
    """Evaluate a cumulusci `when:` expression, in CCI's engine where available."""
    ctx = _flag_ctx(commerce_flag, tso_flag)
    if _jinja_env is not None:
        return bool(_jinja_env.compile_expression(expr)(project_config=ctx))
    return bool(eval(expr, {"__builtins__": {}}, {"project_config": ctx}))


engine = "jinja2 (CCI's own)" if _jinja_env is not None else "eval fallback — jinja2 absent"
expected = {(False, False): False, (False, True): True, (True, False): True, (True, True): True}
if not when:
    check("refresh_dt_commerce has a when: expression", False, "step absent or unguarded")
else:
    actual = {pair: evaluate_when(when, *pair) for pair in expected}
    check(
        f"refresh_dt_commerce truth table is commerce OR tso [{engine}]",
        actual == expected,
        f"{when} -> {actual}",
    )

# ⚠ The one thing Jinja2 swallows silently is a flag name that does not exist: it is
# Undefined, therefore falsy, therefore the step never runs — and nothing errors. That is
# bit-for-bit the bug this branch exists to fix, so a typo in any `when:` would reintroduce
# it invisibly. Checked by name against the real flag list, which needs no engine at all.
declared_flags = set(cci["project"]["custom"])
bad_refs = {}
for key, step in steps.items():
    expr = step.get("when") or ""
    unknown = set(re.findall(r"project__custom__(\w+)", expr)) - declared_flags
    if unknown:
        bad_refs[key] = sorted(unknown)
check(
    "every when: in the flow references only declared flags",
    not bad_refs,
    f"unknown flags: {bad_refs}",
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

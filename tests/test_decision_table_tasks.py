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
# 1b. The pinned-client invariant. Every operation must go through `_sf` so calls
#     use the PROJECT's api_version, not whatever the org has drifted up to. An
#     earlier version pinned only the refresh, leaving the query and the only
#     WRITE unpinned.
# ---------------------------------------------------------------------------
print("\n[1b] only the sanctioned fallback bypasses the pinned client")

_manage_src = (REPO / "tasks" / "rlm_manage_decision_tables.py").read_text()
_unpinned_uses = _manage_src.count("self.org_config.salesforce_client")

# ⚠ A TRIPWIRE, not a proof — scope the claim honestly. This counts one literal spelling, so
# it catches the single most probable regression (pasting `sf = self.org_config.salesforce_client`
# into a new operation, which is exactly how the round-2 defect arose) and nothing else.
# `getattr(self.org_config, "salesforce_client")`, binding `oc = self.org_config` first, or
# constructing Salesforce(...) inline all bypass it silently — measured. Real enforcement is an
# AST walk; this is the cheap 90%. The one sanctioned use is the LOGGED fallback inside
# _pinned_salesforce_client.
check(
    "only the pinned fallback spells out org_config.salesforce_client",
    _unpinned_uses == 1,
    f"found {_unpinned_uses} uses, expected 1",
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


class _CapturingLogger:
    """
    Records what a task told the operator, per level.

    ⚠ Interpolate %-style args. Both task modules mix f-strings with lazy
    `logger.info("  %s (%d): %s", ut, len(dts), ...)` formatting, and capturing only the
    template would silently drop every value — a check on the rendered text would then be
    asserting against `%s` placeholders and passing for the wrong reason.
    """

    def __init__(self):
        self.infos = []
        self.warnings = []
        self.errors = []
        self.debugs = []

    @staticmethod
    def _render(msg, args):
        """
        Render exactly as stdlib logging does — including RAISING on a bad format.

        ⚠ Do NOT swallow the error. `LogRecord.getMessage()` is `msg % self.args` and raises
        on a mismatch; verified: `LogRecord(..., "Refresh queued for %d", ("A_Table",))`
        raises TypeError. Returning the raw template instead would let a malformed
        production call PASS a substring assertion, because the literal half of the template
        survives — `"Refresh queued for %d"` still contains "Refresh queued". A test double
        that is more forgiving than production hides exactly the bug it should surface.

        ⚠ Skipping interpolation when args is empty is stdlib behaviour, not a divergence:
        `LogRecord(..., "100%% sure", ())` renders "100%% sure" unchanged. Verified.
        """
        text = str(msg)
        return text % args if args else text

    def info(self, msg, *a, **k):
        self.infos.append(self._render(msg, a))

    def warning(self, msg, *a, **k):
        self.warnings.append(self._render(msg, a))

    def error(self, msg, *a, **k):
        self.errors.append(self._render(msg, a))

    def debug(self, msg, *a, **k):
        self.debugs.append(self._render(msg, a))


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
#
#     ⚠ Drive BOTH classes. Each carries its own copy of this gate, and the copy
#     in RefreshDecisionTable is the one every refresh_dt_* step of every build
#     runs. Exercising only the manual task left the build path's gate free to be
#     deleted with every check still green — which is the same shape as the
#     original defect, one level up.
# ---------------------------------------------------------------------------
print("\n[3b] the status gate accepts ONLY an explicit Queued — in BOTH classes")

STATUS_CASES = [
    ({"isSuccess": True, "outputValues": {"Status": "Queued"}}, True, "Queued"),
    ({"isSuccess": True, "outputValues": {"Status": "queued"}}, True, "queued (case)"),
    ({"isSuccess": True, "outputValues": {"Status": " Queued "}}, True, "Queued (whitespace)"),
    ({"isSuccess": True, "outputValues": {"Status": "Failed"}}, False, "Failed"),
    ({"isSuccess": True, "outputValues": {"Status": "Accepted"}}, False, "unrecognised status"),
    ({"isSuccess": True, "outputValues": {"Status": "   "}}, False, "whitespace-only Status"),
    ({"isSuccess": True, "outputValues": {}}, False, "missing Status"),
    ({"isSuccess": True}, False, "missing outputValues"),
    ({"isSuccess": False, "errors": [{"message": "nope"}]}, False, "isSuccess False"),
    # ⚠ A failure carrying NO details. Every other negative case leaves a second error line
    # behind (the per-error loop), which masks the build path's generic failure line: downgrade
    # that line to a warning and those cases still see an error and stay green. This shape has
    # nothing else to log, so it is the only case that holds the generic line in place.
    ({"isSuccess": False}, False, "isSuccess False, no error details"),
]

QUEUE_FAILURE_MESSAGE = "Failed to queue a refresh"


def manage_counts_success(response):
    """
    Drive ManageDecisionTables._refresh_decision_tables; report whether it counted a queue.

    ⚠ Assert on the REASON, not merely that something raised. A bare
    `except Exception: return False` returns the expected answer for every not-queued case
    even when the method is broken outright — an AttributeError from a renamed internal
    reads exactly like a working fail-closed gate, so most of these checks would pass under
    a total breakage. Anything that is not the queue-failure exception is re-raised for the
    caller to record as a FAIL.
    """
    task = object.__new__(ManageDecisionTables)
    task.options = {"developer_names": "A_Table", "is_incremental": False}
    task.logger = _SilentLogger()
    task.org_config = object()
    task._sf_client = object()
    task._refresh_single_decision_table = lambda sf, name, inc: response
    try:
        ManageDecisionTables._refresh_decision_tables(task)
        return True  # no raise => fail_count was 0 => it counted a queue
    except Exception as exc:
        if QUEUE_FAILURE_MESSAGE not in str(exc):
            raise
        return False


def refresh_logs_for(response):
    """
    Drive the BUILD PATH gate — RefreshDecisionTable._refresh_decision_table — and return
    everything it told the operator.

    That method deliberately does not raise (exit-0 behaviour is coupled to the
    unconditional default-pricing flow step; see todo pack 049), so the verdict is
    observable only through the log. Asserting on error PRESENCE rather than on wording
    keeps the verdict check alive when the message is reworded — which this branch has now
    done twice.

    ⚠ Returns the whole logger, not just `errors`. An earlier version returned the error
    list alone, so the success path was never asserted at all: deleting the queued
    `logger.info` outright broke ZERO checks, and every refresh_dt_* step of every build
    would have run in total silence with the suite still green. Capturing a field and never
    reading it is not coverage.
    """
    task = object.__new__(RefreshDecisionTable)
    logger = _CapturingLogger()
    task.logger = logger
    task._build_url_and_headers = lambda endpoint: ("https://example.invalid/x", {})
    task._make_request = lambda method, url, **kwargs: response
    RefreshDecisionTable._refresh_decision_table(task, "A_Table", False)
    return logger


for response, should_queue, label in STATUS_CASES:
    verdict = "queued" if should_queue else "NOT queued"

    manage_label = f"ManageDecisionTables treats {label} as {verdict}"
    try:
        got = manage_counts_success(response)
        check(manage_label, got is should_queue, f"counted queued={got}")
    except Exception as exc:
        check(manage_label, False, f"unexpected {type(exc).__name__}: {exc}")

    refresh_label = f"RefreshDecisionTable treats {label} as {verdict}"
    try:
        logs = refresh_logs_for(response)
        check(refresh_label, (not logs.errors) is should_queue, f"errors={logs.errors}")

        # ⚠ Assert the ANNOUNCEMENT for EVERY case, not only the queued ones. Silence is
        # indistinguishable from acceptance if only errors are read — but so is noise:
        # checking the announcement only when should_queue leaves a regression that logs
        # "Refresh queued" unconditionally, or from the FAILURE branch, entirely green. Its
        # error still satisfies the verdict check above and its contradictory success line is
        # never inspected. That is the dangerous direction — a failed request claiming a queue.
        announced = any("Refresh queued" in m for m in logs.infos)
        check(
            f"RefreshDecisionTable announces a queue for {label} ONLY when it queued",
            announced is should_queue,
            f"announced={announced} infos={logs.infos}",
        )
        # ⚠ Pin the CONTENT, not a literal prefix. "Refresh queued" is eight characters of
        # boilerplate: a message naming the wrong table with the status interpolation deleted
        # satisfies it. The expected status is the fixture's own value stripped — deriving it
        # from the response rather than re-implementing the production fallback.
        if should_queue:
            expected_status = ((response.get("outputValues") or {}).get("Status") or "").strip()
            check(
                f"the {label} announcement names the table and the rendered status",
                any("A_Table" in m and f"Status: {expected_status}" in m for m in logs.infos),
                str(logs.infos),
            )
    except Exception as exc:
        check(refresh_label, False, f"unexpected {type(exc).__name__}: {exc}")

# ⚠ The 'Unknown' sentinel must be applied AFTER the strip. '   ' is truthy, so an
# `or 'Unknown'` placed before .strip() never fires and the operator message renders a
# blank where the status belongs — at the exact moment the gate is trying to explain
# itself. Both classes normalise identically; this pins the rendering, not just the verdict.
blank_status_errors = refresh_logs_for({"isSuccess": True, "outputValues": {"Status": "   "}}).errors
check(
    "a whitespace-only Status renders as Unknown, not blank",
    bool(blank_status_errors) and "Unknown" in blank_status_errors[0],
    str(blank_status_errors),
)

# ⚠ The two classes carry SEPARATE copies of the async guidance, and "the build path and the
# manual path said different things" was round 2's top finding. A comment saying they must not
# drift is prose; this holds them.
#
# ⚠ Compare the WHOLE guidance clause on the RENDERED message, not a prefix in the source. A
# prefix check stops before the part that was corrected twice — flip one class to say a
# POST-refresh verdict and the shared opening survives in both files, so a check labelled
# "byte-identical" stays green while the two messages contradict each other. Rendering also
# sidesteps source line-wrapping, which is not a semantic difference.
GUIDANCE_START = "Completion is asynchronous;"
_QUEUED = {"isSuccess": True, "outputValues": {"Status": "Queued"}}


def manage_logs_for(response):
    """Drive ManageDecisionTables._refresh_decision_tables and return what it logged."""
    task = object.__new__(ManageDecisionTables)
    task.options = {"developer_names": "A_Table", "is_incremental": False}
    logger = _CapturingLogger()
    task.logger = logger
    task.org_config = object()
    task._sf_client = object()
    task._refresh_single_decision_table = lambda sf, name, inc: response
    try:
        ManageDecisionTables._refresh_decision_tables(task)
    except Exception as exc:
        if QUEUE_FAILURE_MESSAGE not in str(exc):
            raise
    return logger


def _guidance(logger):
    for message in logger.infos:
        if GUIDANCE_START in message:
            return message[message.index(GUIDANCE_START):]
    return None


_manage_guidance = _guidance(manage_logs_for(_QUEUED))
_refresh_guidance = _guidance(refresh_logs_for(_QUEUED))
check(
    "both classes render byte-identical async guidance",
    _manage_guidance is not None and _manage_guidance == _refresh_guidance,
    f"manage={_manage_guidance!r} refresh={_refresh_guidance!r}",
)

# ---------------------------------------------------------------------------
# 4. Flow shape. A draft of this very change created a duplicate step key, and
#    YAML silently kept the last one — deleting refresh_dt_commerce from the flow.
#    Caught by hand once; this is what catches it next time.
# ---------------------------------------------------------------------------
print("\n[4] refresh_all_decision_tables step keys are contiguous and complete")

with open(REPO / "cumulusci.yml") as fh:
    cci = yaml.safe_load(fh)

declared_flags = set(cci["project"]["custom"])
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
    """
    A project_config stand-in carrying EVERY declared flag, defaulting False.

    ⚠ Every flag, not only the two under test. Populate just commerce and tso and a THIRD
    flag added to the gate is Undefined under Jinja2 — falsy, silently ignored, truth table
    unchanged, check still PASSES — while the offline eval fallback raises AttributeError.
    Same edit, opposite verdicts, and the faithful engine is the one that waves it through.
    Declaring them all makes both engines agree; the exact-flag-set check below then catches
    the edit in either environment.
    """
    class _Custom:
        pass

    custom = _Custom()
    for flag in declared_flags:
        setattr(custom, f"project__custom__{flag}", False)
    setattr(custom, "project__custom__commerce", commerce_flag)
    setattr(custom, "project__custom__tso", tso_flag)
    return custom


def evaluate_when(expr, commerce_flag, tso_flag):
    """
    Evaluate a cumulusci `when:` expression, in CCI's engine where available.

    ⚠ The `eval` is not an injection surface: `expr` is read from this repository's own
    cumulusci.yml, `__builtins__` is stripped, and the only name in scope is the local
    flag stand-in. It is the offline fallback for Jinja2, nothing more.
    """
    ctx = _flag_ctx(commerce_flag, tso_flag)
    if _jinja_env is not None:
        return bool(_jinja_env.compile_expression(expr)(project_config=ctx))
    return bool(eval(expr, {"__builtins__": {}}, {"project_config": ctx}))  # noqa: S307


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
    # ⚠ Pin the OPERAND SET as well as the truth table. A third flag ORed into the gate
    # leaves all four rows unchanged — it only ever widens the condition — so the truth
    # table alone cannot see it. This check is engine-independent and sees it immediately.
    check(
        "the refresh_dt_commerce gate references exactly commerce and tso",
        set(re.findall(r"project__custom__(\w+)", when)) == {"commerce", "tso"},
        when,
    )

# ⚠ The one thing Jinja2 swallows silently is a flag name that does not exist: it is
# Undefined, therefore falsy, therefore the step never runs — and nothing errors. That is
# bit-for-bit the bug this branch exists to fix, so a typo in any `when:` would reintroduce
# it invisibly. Checked by name against the real flag list, which needs no engine at all.
#
# ⚠ Match the WHOLE reference, not just `project__custom__<name>`. A malformed PREFIX —
# `project__custom_rating`, one underscore short — produces no match for the narrow pattern,
# so an unknown-flag scan finds nothing to complain about and the typo sails through as a
# falsy Undefined. Extracting every `<namespace>.<attribute>` and requiring project_config
# attributes to be exactly `project__custom__<declared flag>` closes that hole.
#
# ⚠ Scanned across EVERY flow, not just this one. The marginal cost is one extra loop and
# widening it is what found the psg_debug defect below on the first run.
# ⚠ Validate the COMPLETE org_config reference, not just the namespace. Allowlisting
# `org_config` wholesale lets `org_config.scrtch` through — and CCI's OrgConfig resolves an
# unknown attribute to None rather than raising, so under Jinja2 that typo is falsy and the
# guarded step is silently skipped. That is bit-for-bit the defect class this check exists to
# catch, just in the other namespace. Verified live 2026-07-27: `org_config.scrtch` -> None.
# CumulusCI puts exactly two names in the when: context (flowrunner.py:511-513), and these are
# the only org_config attributes the repo uses; a static set needs no CumulusCI import, so the
# offline suite stays offline.
ALLOWED_ORG_CONFIG_REFS = {"org_config.scratch", "org_config.org_type"}

# ⚠ PRE-EXISTING on main, not introduced by this branch. `psg_debug` is referenced by two
# steps of assign_feature_permission_sets and is absent from project.custom, so both evaluate
# `<flag> and Undefined` -> False in every org and have never run. Allowlisted so this check
# ships ENFORCED rather than blocked on an undecided question. Tracked as issue #331.
#
# ⚠ Scoped to (flow, step, flag), NOT to the bare name. A name-scoped allowlist forgives the
# flag in all 198 clauses across 46 flows — measured: re-gating refresh_dt_prm_pricing onto
# psg_debug, which would silently stop that step running in any org, broke zero checks. These
# two sites are forgiven; a third reference anywhere is a failure.
KNOWN_UNDECLARED = {
    ("assign_feature_permission_sets", 1, "psg_debug"),
    ("assign_feature_permission_sets", 4, "psg_debug"),
}

# ⚠ Consume the WHOLE dotted run. `re.findall(r"(\w+)\.(\w+)", ...)` matches non-overlapping,
# so `org_config.scratch.nonexistent` yields only ("org_config", "scratch") — an ALLOWED
# reference — and the trailing segment is never examined. Jinja2 resolves that third hop to a
# falsy Undefined and the guarded step is silently skipped, so the check passes while the name
# it claims to validate does not resolve. Measured by both reviewers in round 6: zero failures.
# A chain rooted at an UNKNOWN namespace was always caught; the hole was chains rooted at a
# name the check recognises. Anything beyond <namespace>.<attribute> is now rejected outright.
bad_refs = {}
seen_undeclared = set()
for flow_name, flow in (cci.get("flows") or {}).items():
    for key, step in ((flow or {}).get("steps") or {}).items():
        expr = (step or {}).get("when") or ""
        if not expr:
            continue
        for run in re.findall(r"\b\w+(?:\.\w+)+", expr):
            segments = run.split(".")
            if len(segments) > 2:
                bad_refs.setdefault(f"{flow_name}[{key}]", []).append(
                    f"{run} (chained past <namespace>.<attribute>; the tail resolves to Undefined)"
                )
                continue
            namespace, attribute = segments
            if namespace == "org_config":
                if run in ALLOWED_ORG_CONFIG_REFS:
                    continue
            # ⚠ Namespace must be exactly project_config. Matching on the attribute alone also
            # accepted `other.project__custom__rating`, which fails loudly at runtime but should
            # not pass a check whose whole job is catching names that will not resolve.
            elif namespace == "project_config" and attribute.startswith("project__custom__"):
                flag = attribute[len("project__custom__"):]
                if flag in declared_flags:
                    continue
                if (flow_name, key, flag) in KNOWN_UNDECLARED:
                    seen_undeclared.add((flow_name, key, flag))
                    continue
            bad_refs.setdefault(f"{flow_name}[{key}]", []).append(run)

check(
    f"every when: across all {len(cci.get('flows') or {})} flows resolves to a real name",
    not bad_refs,
    f"bad references: {bad_refs} — if one is a legitimate new org_config attribute, "
    "add the complete reference to ALLOWED_ORG_CONFIG_REFS",
)

# ⚠ EQUALITY, not disjointness. The exemption set has to track the live references in both
# directions, and there are more than two ways for it to rot: issue #331 closed by DECLARING
# the flag, closed by DELETING both steps, or the steps RELOCATED. Each leaves a stale tuple
# that silently forgives whatever later occupies that flow/step slot. A disjointness check
# saw only the first. Measured: deleting the two dead references broke zero checks.
check(
    "KNOWN_UNDECLARED matches the live exemptions exactly — no stale or missing entry",
    seen_undeclared == KNOWN_UNDECLARED,
    f"stale, delete these: {sorted(KNOWN_UNDECLARED - seen_undeclared)}; "
    f"unlisted: {sorted(seen_undeclared - KNOWN_UNDECLARED)}",
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

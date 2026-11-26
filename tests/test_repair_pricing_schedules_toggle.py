"""ensure_pricing_schedules: settings deploys overwrite, and a stranded toggle is reported (pack 503)."""
import logging
import os
import shlex
import subprocess
import sys
import types
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import repo `tasks.*` modules before cumulusci (see rlm_manage_flows).
import tasks.rlm_repair_pricing_schedules as mod  # noqa: E402

# Placeholders: the deploys are stubbed, so no bundle is read.
DISABLE = "disable-bundle"
ENABLE = "enable bundle"
USER = "user@example.test"
# The restore command carries the absolute path, so it works from anywhere inside the project.
RESTORE = (
    f"sf project deploy start --source-dir {shlex.quote(os.path.abspath(ENABLE))} "
    f"--target-org {USER} --ignore-conflicts"
)


def ends_with_restore(text):
    """The restore command closes the message on its own line, with nothing after it to copy by mistake."""
    return bool(text) and text.endswith("\n  " + RESTORE)

OK = (0, "{}", "")
FAIL = (1, "", "1 conflicts detected")


class UnexpectedDeploy(BaseException):
    """More deploy calls than the case scripted. A BaseException so the task's own handlers cannot swallow it."""


class Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def run_case(results, state="off", interrupt=None, polls=None, username=USER, options=None, early_dt_error=False):
    """Drive _run_task through the toggle with scripted deploy results.

    Returns a namespace: calls (deploy argvs), error (TaskOptionsError text or None), raised (other exception),
    sleeps_before (deploy-call count at each sleep), polls (schedule queries), logs.
    interrupt: "disable" (the first deploy call), "deploy" (the second), "sleep" (the pause before the enable
    retry) or "probe" (the state check) raises KeyboardInterrupt.
    polls: _get_missing_schedules results in order (the pre-check first); an exception item is raised.
    early_dt_error: decision-table validation is on and its query fails if it runs before any deploy.
    """
    task = mod.EnsurePricingSchedules.__new__(mod.EnsurePricingSchedules)
    task.org_config = types.SimpleNamespace(username=username)
    task.logger = logging.getLogger(f"t{id(task)}")
    task.logger.setLevel(logging.INFO)
    capture = Capture()
    task.logger.addHandler(capture)
    task.options = {
        "disable_settings_path": DISABLE,
        "enable_settings_path": ENABLE,
        "validate_decision_table_lookups": "false",
        "poll_attempts": "2",
        "poll_interval_seconds": "7",
        **(options or {}),
    }
    queue = list(results)
    out = types.SimpleNamespace(calls=[], error=None, raised=None, sleeps_before=[], polls=0, logs=capture.messages)

    def fake_run(cmd, **kwargs):
        out.calls.append(list(cmd))
        if (interrupt == "disable" and len(out.calls) == 1) or (interrupt == "deploy" and len(out.calls) == 2):
            raise KeyboardInterrupt
        if not queue:
            raise UnexpectedDeploy(f"unscripted deploy {cmd}")
        code, stdout, stderr = queue.pop(0)
        return subprocess.CompletedProcess(cmd, code, stdout, stderr)

    states = iter(polls or [["Standard Attribute Based Adjustment"], []])

    def missing(names):
        out.polls += 1
        result = next(states, [])
        if isinstance(result, Exception):
            raise result
        return result

    def sleep(seconds):
        out.sleeps_before.append((len(out.calls), seconds))
        if interrupt == "sleep" and len(out.calls) == 2:
            raise KeyboardInterrupt

    task._get_missing_schedules = missing
    # The settings paths are checked to exist before any query (todo 488). DISABLE and ENABLE are
    # placeholders (the deploys are stubbed), so that one check is stubbed too; the rest of the
    # option reading (required, stripped, a list refused) still runs.
    real_path_option = task._path_option

    def path_option(name, default=None, directory=False):
        if name in ("disable_settings_path", "enable_settings_path"):
            with mock.patch.object(mod.Path, "exists", lambda self: True):
                return real_path_option(name, default, directory)
        return real_path_option(name, default, directory)

    task._path_option = path_option
    if early_dt_error:
        task.options["validate_decision_table_lookups"] = "true"
        # Absolute, so the up-front directory check does not depend on the working directory.
        task.options["expression_sets_metadata_path"] = str(REPO / "force-app/main/default/expressionSetDefinition")
        task._discover_lookup_decision_tables = lambda *a: ["T"]

        def missing_tables(names):
            if not out.calls:
                raise mod.TaskOptionsError("decision table query failed before any deploy")
            return []

        task._get_missing_decision_tables = missing_tables
    def pricing_state():
        if interrupt == "probe":
            raise KeyboardInterrupt
        return state

    task._pricing_state = pricing_state
    with mock.patch.object(mod.subprocess, "run", fake_run), \
            mock.patch.object(mod.time, "sleep", sleep):
        try:
            task._run_task()
        except mod.TaskOptionsError as exc:  # Exception itself when cumulusci is absent
            out.error = str(exc)
        except BaseException as exc:  # noqa: BLE001 (the interrupt case)
            out.raised = exc
    task.logger.removeHandler(capture)
    return out


def check_argvs():
    run = run_case([OK, OK])
    if not run.calls:
        return ["no deploy calls were made"]
    problems = []
    if run.error:
        problems.append(f"unexpected error {run.error}")
    if len(run.calls) != 2:
        problems.append(f"expected 2 deploys, got {len(run.calls)}")
    for call, path in zip(run.calls, (DISABLE, ENABLE)):
        problems += argv_problems(call, path)
    if run.polls < 2:
        problems.append("the task did not poll after the toggle")
    return problems


def argv_problems(call, path):
    problems = []
    if "--ignore-conflicts" not in call:
        problems.append(f"{path}: --ignore-conflicts missing")
    if call[call.index("--source-dir") + 1] != path:
        problems.append(f"{path}: wrong --source-dir")
    if call[call.index("--target-org") + 1] != USER:
        problems.append(f"{path}: wrong --target-org")
    return problems


def check_retry_succeeds():
    run = run_case([OK, FAIL, OK])
    if not run.calls:
        return ["no deploy calls were made"]
    problems = []
    if run.error:
        problems.append(f"unexpected error {run.error}")
    if len(run.calls) != 3:
        problems.append(f"expected 3 deploys, got {len(run.calls)}")
    for call in run.calls[1:]:
        problems += argv_problems(call, ENABLE)
    if (2, 7) not in run.sleeps_before:
        problems.append(f"no pause before the retry: {run.sleeps_before}")
    if run.polls < 2:
        problems.append("the task did not poll after a successful retry")
    return problems


def enable_fails_twice(state):
    run = run_case([OK, FAIL, FAIL], state=state)
    if not run.calls:
        return run, ["no deploy calls were made"]
    problems = []
    if len(run.calls) != 3:
        problems.append(f"expected 3 deploys, got {len(run.calls)}")
    for call in run.calls[1:]:
        problems += argv_problems(call, ENABLE)
    if not run.error:
        return run, problems + ["no error raised"]
    if "1 conflicts detected" not in run.error:
        problems.append("message lacks the deploy error")
    return run, problems


def check_enable_fails_twice_off():
    run, problems = enable_fails_twice("off")
    if run.error:
        if "Pricing reads as DISABLED" not in run.error:
            problems.append("message does not say Pricing reads as disabled")
        if "the disable deploy succeeded" not in run.error:
            problems.append(f"message does not name the cause: {run.error}")
        if not ends_with_restore(run.error):
            problems.append(f"message does not end with the quoted restore command: {run.error!r}")
    return problems


def check_enable_fails_twice_unknown():
    run, problems = enable_fails_twice("unknown")
    if run.error:
        if "may be DISABLED" not in run.error or "could not be read" not in run.error:
            problems.append("message does not say the state is uncertain")
        if not ends_with_restore(run.error):
            problems.append(f"message does not end with the restore command: {run.error!r}")
    return problems


def check_enable_fails_twice_on():
    """A failed deploy that still landed: warn and let polling decide, with no claim that Pricing is off."""
    run = run_case([OK, FAIL, FAIL], state="on")
    if not run.calls:
        return ["no deploy calls were made"]
    problems = []
    if len(run.calls) != 3:
        problems.append(f"expected 3 deploys, got {len(run.calls)}")
    if run.error:
        problems.append(f"unexpected error {run.error}")
    if run.polls < 2:
        problems.append("the task did not poll")
    warned = [m for m in run.logs if "reads as enabled" in m]
    if not warned or "1 conflicts detected" not in warned[0]:
        problems.append(f"no warning with the deploy error: {run.logs}")
    if any(RESTORE in m or "may now be off" in m for m in run.logs):
        problems.append("a log claims Pricing may be off although it reads as enabled")
    return problems


def check_polling_sees_pricing_off():
    """After a successful enable, a schedule query that fails while Pricing reads off keeps polling, then says so."""
    query_error = mod.TaskOptionsError("Failed to query PriceAdjustmentSchedule: INVALID_TYPE")
    problems = []
    run = run_case([OK, OK], state="off", polls=[["X"], query_error, query_error])
    if run.polls != 3:
        problems.append(f"still off: expected 3 schedule queries, got {run.polls}")
    if not run.error or "still reads as DISABLED" not in run.error or not ends_with_restore(run.error):
        problems.append(f"still off: wrong error {run.error!r}")
    elif "cannot see the object" not in run.error:
        problems.append(f"still off: the claim is not hedged for a user who cannot see the object: {run.error!r}")
    run = run_case([OK, OK], state="off", polls=[["X"], query_error, []])
    if run.error:
        problems.append(f"off then on: unexpected error {run.error}")
    for state in ("on", "unknown"):
        run = run_case([OK, OK], state=state, polls=[["X"], query_error, []])
        if run.polls != 3 or run.error:
            problems.append(f"{state}: a failed query should be retried ({run.polls} queries, {run.error})")
        run = run_case([OK, OK], state=state, polls=[["X"], query_error, query_error])
        if run.polls != 3 or not run.error or "INVALID_TYPE" not in run.error:
            problems.append(f"{state}: the last failed query should raise it ({run.polls} queries, {run.error})")
        if run.error and "DISABLED" in run.error:
            problems.append(f"{state}: claims Pricing is disabled: {run.error}")
        if run.error and ends_with_restore(run.error) != (state == "unknown"):
            problems.append(f"{state}: restore hint {'missing' if state == 'unknown' else 'given'}: {run.error!r}")
    dropped = OSError("connection dropped")
    run = run_case([OK, OK], state="on", polls=[["X"], dropped, []])
    if run.polls != 3 or run.error or run.raised:
        problems.append(f"a dropped connection mid-poll should be retried ({run.polls} queries, {run.error}, {run.raised!r})")
    run = run_case([OK, OK], state="unknown", polls=[["X"], dropped, dropped])
    if not run.error or not ends_with_restore(run.error) or "connection dropped" not in run.error:
        problems.append(f"a dropped connection on the last poll with an unreadable state needs the hint: {run.error!r}")
    return problems


def check_disable_fails():
    problems = []
    wants = {
        "on": ("a rerun of this task re-enables it", False),
        "off": ("Pricing now reads as DISABLED", True),
        "unknown": ("Pricing may now be off", True),
    }
    for state, (phrase, wants_hint) in wants.items():
        run = run_case([FAIL], state=state)
        if not run.calls:
            return ["no deploy calls were made"]
        if len(run.calls) != 1:
            problems.append(f"{state}: expected 1 deploy, got {len(run.calls)}")
        if not run.error:
            problems.append(f"{state}: no error raised")
            continue
        if "1 conflicts detected. " not in run.error:
            problems.append(f"{state}: the deploy error is not a finished sentence: {run.error}")
        if phrase not in run.error:
            problems.append(f"{state}: expected {phrase!r}: {run.error}")
        if ends_with_restore(run.error) != wants_hint or (RESTORE in run.error) != wants_hint:
            problems.append(f"{state}: restore hint {'missing' if wants_hint else 'given'}: {run.error}")
    return problems


def check_pricing_already_off():
    """A rerun after a stranded toggle: the pre-check query fails while Pricing reads off -> enable, no disable."""
    query_error = mod.TaskOptionsError("Failed to query PriceAdjustmentSchedule: INVALID_TYPE")
    problems = []
    run = run_case([OK], state="off", polls=[query_error, []])
    if len(run.calls) != 1:
        problems.append(f"expected only the enable deploy, got {len(run.calls)} calls")
    elif argv_problems(run.calls[0], ENABLE):
        problems += argv_problems(run.calls[0], ENABLE)
    if run.error:
        problems.append(f"unexpected error {run.error}")
    if any("Toggling" in m for m in run.logs):
        problems.append(f"self-heal logs a toggle that does not happen: {run.logs}")
    if not any("reads as DISABLED" in m and "enabling it" in m for m in run.logs):
        problems.append(f"no log that Pricing was found disabled: {run.logs}")
    run = run_case([FAIL, FAIL], state="off", polls=[query_error])
    if len(run.calls) != 2 or not run.error:
        problems.append(f"enable fails twice after a self-heal: expected 2 deploys and an error, got {run.error}")
    elif "already off" not in run.error or "disable deploy" in run.error or not ends_with_restore(run.error):
        problems.append(f"enable fails twice after a self-heal: wrong cause or hint: {run.error!r}")
    run = run_case([OK], state="off", polls=[query_error, []], early_dt_error=True)
    if run.error or len(run.calls) != 1:
        problems.append(f"self-heal must not query decision tables before the enable: {run.error}, {len(run.calls)} calls")
    run = run_case([], state="off", polls=[query_error], username=None)
    if run.calls or not run.error or "No target org username" not in run.error:
        problems.append(f"self-heal with no username: expected a refusal before any deploy: {run.error}")
    run = run_case([], state="on", polls=[query_error])
    if run.calls or not run.error or "INVALID_TYPE" not in run.error:
        problems.append(f"a failed pre-check with Pricing on must raise without deploying: {run.error}, {len(run.calls)}")
    return problems


def check_preconditions():
    problems = []
    run = run_case([], username=None)
    if run.calls or not run.error or "No target org username" not in run.error:
        problems.append(f"no username: expected a refusal before any deploy: {run.error}, {len(run.calls)} calls")
    if run.polls != 1:
        problems.append("no username: the state probe or polling ran")
    if run.error and ("DISABLED" in run.error or "may now be off" in run.error):
        problems.append(f"no username: claims a Pricing state although nothing was deployed: {run.error}")
    for value in ("0", "-1"):
        run = run_case([], options={"poll_attempts": value})
        if run.calls or run.polls or not run.error or "poll_attempts" not in run.error:
            problems.append(f"poll_attempts {value}: expected a refusal before any query: {run.error}")
    return problems


def check_interrupt_logs_restore():
    problems = []
    cases = (
        ("disable", [OK], 1, "disabling pricing"),
        ("deploy", [OK], 2, "re-enabling pricing"),
        ("sleep", [OK, FAIL], 2, "re-enabling pricing"),
        ("probe", [OK, FAIL, FAIL], 3, "checking Pricing"),
    )
    for where, results, calls, phrase in cases:
        run = run_case(results, interrupt=where)
        if len(run.calls) != calls:
            problems.append(f"{where}: expected {calls} deploy calls, got {len(run.calls)}")
        if not isinstance(run.raised, KeyboardInterrupt):
            problems.append(f"{where}: interrupt not re-raised: {run.raised!r} / {run.error}")
        logged = [m for m in run.logs if RESTORE in m]
        if not logged:
            problems.append(f"{where}: no restore command logged: {run.logs}")
        elif "may" not in logged[0] or phrase not in logged[0] or not ends_with_restore(logged[0]):
            problems.append(f"{where}: the log should say Pricing may be off while {phrase}: {logged[0]}")
    return problems


def check_pricing_state():
    """_pricing_state reads Pricing as off only from INVALID_TYPE; anything else it cannot read is unknown."""
    import requests

    task = mod.EnsurePricingSchedules.__new__(mod.EnsurePricingSchedules)
    task.org_config = types.SimpleNamespace(instance_url="https://example.test", access_token="t")
    task.project_config = types.SimpleNamespace(project__package__api_version="66.0")
    seen = []

    def response(ok, body):
        def get(url, **kwargs):
            seen.append((url, kwargs.get("params"), kwargs.get("timeout")))
            if isinstance(body, Exception):
                raise body
            return types.SimpleNamespace(ok=ok, json=lambda: body)
        return get

    cases = [
        ("on", True, {"records": []}),
        ("off", False, [{"errorCode": "INVALID_TYPE", "message": "sObject type is not supported"}]),
        ("unknown", False, [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]),
        ("unknown", False, {"unexpected": "shape"}),
        ("unknown", False, requests.ConnectionError("down")),
    ]
    problems = []
    for want, ok, body in cases:
        with mock.patch.object(requests, "get", response(ok, body)):
            got = task._pricing_state()
        if got != want:
            problems.append(f"{body!r}: expected {want}, got {got}")
    if len(seen) != len(cases):
        problems.append(f"expected {len(cases)} queries, got {len(seen)}")
    elif "PriceAdjustmentSchedule" not in seen[0][1]["q"] or "/v66.0/query" not in seen[0][0]:
        problems.append(f"unexpected probe request {seen[0]}")
    elif not seen[0][2]:
        problems.append("the state probe has no timeout")
    return problems


def check_schedule_query_has_timeout():
    """A stalled connection must raise (an OSError the poll loop tolerates), not hang the task."""
    import requests

    task = mod.EnsurePricingSchedules.__new__(mod.EnsurePricingSchedules)
    task.org_config = types.SimpleNamespace(instance_url="https://example.test", access_token="t")
    task.project_config = types.SimpleNamespace(project__package__api_version="66.0")
    seen = []

    def get(url, **kwargs):
        seen.append(kwargs.get("timeout"))
        return types.SimpleNamespace(ok=True, json=lambda: {"records": []})

    with mock.patch.object(requests, "get", get):
        task._get_missing_schedules(["Standard"])
    return [] if seen and seen[0] else ["the schedule query has no timeout"]


def check_deploy_error_reads_json():
    """The deploy error comes from the --json payload on stdout, not a stderr warning."""
    warning = "Warning: @salesforce/cli update available"
    cases = [
        ('{"status": 1, "name": "SfError", "message": "bundle: File or folder not found"}',
         "bundle: File or folder not found"),
        ('{"status": 1, "message": "Deploy failed.", "result": {"details": {"componentFailures": '
         '{"fullName": "Pricing", "problem": "bad value"}}}}', "Deploy failed.; Pricing: bad value"),
        ('{"status": 1, "result": {"details": {"componentFailures": [{"fullName": "A", "problem": "x"}, '
         '{"fullName": "B", "problem": "y"}]}}}', "A: x; B: y"),
        ('{"status": 1, "result": []}', '{"status": 1, "result": []}\n' + warning),
        ("not json", "not json\n" + warning),
        ("", warning),
    ]
    problems = []
    for stdout, want in cases:
        got = mod.EnsurePricingSchedules._deploy_error(subprocess.CompletedProcess([], 1, stdout, warning))
        if got != want:
            problems.append(f"{stdout!r}: expected {want!r}, got {got!r}")
    run = run_case([OK, (1, cases[0][0], warning), (1, cases[0][0], warning)], state="off")
    if not run.error or "File or folder not found" not in run.error or warning in run.error:
        problems.append(f"task error does not carry the JSON message: {run.error}")
    return problems


def check_configured_paths_are_pricing_only():
    """The configured toggle deploys only the Pricing settings, and its two sides differ only in the toggle.

    A wider enable bundle (the whole 2_settings directory) also resets settings that later bundles change,
    such as Billing's invoice and payment-schedule flags, on every toggle and every restore.
    """
    import re

    import yaml

    config = yaml.safe_load((REPO / "cumulusci.yml").read_text())
    options = config["tasks"]["ensure_pricing_schedules"]["options"]
    problems, texts = [], {}
    for key, want in (("disable_settings_path", "false"), ("enable_settings_path", "true")):
        path = REPO / options[key]
        found = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
        if [p.name for p in found] != ["IndustriesPricing.settings-meta.xml"]:
            problems.append(f"{key} deploys more than the Pricing settings: {[p.name for p in found]}")
            continue
        text = found[0].read_text()
        toggles = re.findall(r"<enableSalesforcePricing>(\w+)</enableSalesforcePricing>", text)
        if toggles != [want]:
            problems.append(f"{key}: enableSalesforcePricing should be {want}, found {toggles}")
        texts[key] = re.sub(r"<enableSalesforcePricing>\w+<", "<enableSalesforcePricing><", text)
    if len(texts) == 2 and len(set(texts.values())) != 1:
        problems.append("the disable and enable settings differ in more than enableSalesforcePricing")
    return problems


CASES = [
    ("the deploy error is read from the --json payload", check_deploy_error_reads_json),
    ("both deploys pass --ignore-conflicts, path, org; the task polls", check_argvs),
    ("enable fails then retry succeeds after a pause", check_retry_succeeds),
    ("enable fails twice, Pricing reads off -> DISABLED + restore command", check_enable_fails_twice_off),
    ("enable fails twice, state unreadable -> may be disabled + restore command", check_enable_fails_twice_unknown),
    ("enable fails twice, Pricing reads on -> warn and poll, no disabled claim", check_enable_fails_twice_on),
    ("polling keeps waiting while Pricing reads off, then says it is still disabled", check_polling_sees_pricing_off),
    ("disable fails -> no enable; restore hint unless Pricing reads on", check_disable_fails),
    ("an interrupt while disabling, enabling, pausing or probing logs the restore command and re-raises",
     check_interrupt_logs_restore),
    ("a rerun while Pricing is already off enables it without a disable deploy", check_pricing_already_off),
    ("a missing username or a poll_attempts below 1 is refused before any deploy", check_preconditions),
    ("_pricing_state maps the probe response", check_pricing_state),
    ("the schedule query has a timeout", check_schedule_query_has_timeout),
    ("the configured toggle deploys only the Pricing settings, mirrored", check_configured_paths_are_pricing_only),
]


def main():
    failures = 0
    for name, fn in CASES:
        try:
            problems = fn()
        except (Exception, UnexpectedDeploy) as exc:  # a crash is a failure, not a pass
            problems = [f"crashed: {exc!r}"]
        print(("FAIL " if problems else "PASS ") + name + ("" if not problems else ": " + "; ".join(problems)))
        failures += bool(problems)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

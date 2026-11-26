#!/usr/bin/env python3
"""Task wiring for parent Id lookups in `tasks/rlm_sfdmu.py` (todo 298), offline.

`tests/test_sfdmu_id_lookups.py` covers the lookup module. This one covers what the module
can't: which org the `sf` CLI is pointed at (never the access token); that Ids resolve in a temp
copy without the SFDMU runtime dirs; that a whole `_run_task` (SFDMU stubbed) of a lookups plan
leaves the tracked plan byte-for-byte unchanged on success, a bad option and a failed lookup; and
that a plan loaded in place has its credentials cleared after a failed run, is untouched by an
early failure, and never has the access token logged. A load, filtered or not, also restores
the exact bytes of export.json it read (todo 319).

Also `TestSFDMUIdempotency`'s second-load rule for a listed insert rejection both loads have, its
`dynamic_assigned_to_user` option resolving the DRO placeholder on both loads (todo 329), and
`DeleteSFDMUData`'s `sobjects` option, which the qb-pricing teardown needs now that the plan has
no Insert objects (todo 298).

Needs CumulusCI (the task module imports it):
    ~/.local/pipx/venvs/cumulusci/bin/python tests/test_sfdmu_id_lookup_wiring.py
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import the repo's tasks package before cumulusci: importing cumulusci.core.config first
# leaves an empty namespace module at sys.modules["tasks"], which hides tasks/rlm_sfdmu.py.
import tasks.rlm_sfdmu as rs  # noqa: E402

from cumulusci.core.config import OrgConfig, ScratchOrgConfig  # noqa: E402
from cumulusci.core.exceptions import TaskOptionsError  # noqa: E402

_failures: list[str] = []


def check(label: str, got, want) -> None:
    if got == want:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}\n       got:  {got!r}\n       want: {want!r}")
        _failures.append(label)


print("sfdmu_cli_org")
scratch = ScratchOrgConfig({"username": "scratch@example.com", "access_token": "00Dxx!TOKEN"}, "dev")
persistent = OrgConfig({"username": "user@example.com", "access_token": "00Dxx!TOKEN"}, "prod")
tokenless = OrgConfig({"access_token": "00Dxx!TOKEN"}, "tok")
check("scratch: its username, the option ignored", rs.sfdmu_cli_org(scratch, "other@example.com"),
      "scratch@example.com")
check("persistent: the explicit option wins", rs.sfdmu_cli_org(persistent, "alias"), "alias")
check("persistent: else org_config.username", rs.sfdmu_cli_org(persistent, None), "user@example.com")
try:
    got = rs.sfdmu_cli_org(tokenless, None)
except TaskOptionsError:
    got = "TaskOptionsError"
check("no username: raises, never returns the access token", got, "TaskOptionsError")

print("LoadSFDMUData: lookups resolve in a temp copy")
plan = pathlib.Path(tempfile.mkdtemp()) / "plan"
shutil.copytree(REPO / "datasets/sfdmu/qb/en-US/qb-rating-entitlements", plan,
                ignore=shutil.ignore_patterns(*rs.SFDMU_RUNTIME_DIRS))
for runtime in rs.SFDMU_RUNTIME_DIRS:
    (plan / runtime).mkdir()
    (plan / runtime / "stale.csv").write_text("x\n")
before = {p.relative_to(plan): p.read_bytes() for p in plan.rglob("*") if p.is_file()}

task = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
task.org_config = scratch
task.options = {}
task.logger = type("L", (), {"info": lambda *_a, **_k: None})()
task.pathtoexportjson = str(plan)
task._temp_plan_dir = None
queries = []


def fake_query(org, soql):
    queries.append((org, soql))
    return [{"Id": f"1TrWt0000007{i:04d}AAA", "Status": "Active",
             "Product": {"StockKeepingUnit": sku}, "UsageResource": {"Code": code}}
            for i, (sku, code) in enumerate(sorted({
                (r["ProductUsageResource.Product.StockKeepingUnit"], r["ProductUsageResource.UsageResource.Code"])
                for name in ("ProductUsageResourcePolicy", "ProductUsageGrant")
                for r in rs.sfdmu_id_lookups._read_csv(str(plan / f"{name}.csv"))[1]}))]


rs.sf_query_records, real_query = fake_query, rs.sf_query_records
try:
    task._apply_parent_id_lookups()
except Exception:
    shutil.rmtree(plan.parent, ignore_errors=True)
    if task._temp_plan_dir:
        shutil.rmtree(task._temp_plan_dir, ignore_errors=True)
    raise
finally:
    rs.sf_query_records = real_query
temp = pathlib.Path(task.pathtoexportjson)
check("the run points at a temp copy", temp != plan and temp == pathlib.Path(task._temp_plan_dir), True)
check("the CLI query used the scratch username", {org for org, _ in queries}, {"scratch@example.com"})
check("runtime dirs are not copied", [d for d in rs.SFDMU_RUNTIME_DIRS if (temp / d).exists()], [])
check("the temp copy has the generated parent CSV", (temp / "ProductUsageResource.csv").is_file(), True)
with open(temp / "ProductUsageGrant.csv", encoding="utf-8") as fh:
    check("the temp grant CSV carries resolved Ids", fh.readline().startswith("ProductUsageResourceId,"), True)
after = {p.relative_to(plan): p.read_bytes() for p in plan.rglob("*") if p.is_file()}
check("the tracked plan is byte-for-byte unchanged", after == before, True)
shutil.rmtree(temp, ignore_errors=True)
shutil.rmtree(plan.parent, ignore_errors=True)


print("LoadSFDMUData._run_task: the tracked plan is never rewritten")


class _Log:
    def info(self, *_a, **_k):
        pass
    warning = error = info


class _Done:
    returncode, stdout, stderr = 0, "", ""


class _FakeScratch(ScratchOrgConfig):
    """A scratch config whose token/URL don't trigger org creation (no config_file here)."""
    access_token = "00Dxx!TOKEN"
    instance_url = "https://example.my.salesforce.com"


def run_task(options, query, plan_src=None, exit_code=0, org_config=None, sfdmu_output="", runs=None):
    """Run _run_task on a fresh copy of `plan_src`; return (before, after, error, temp, logs)."""
    work = pathlib.Path(tempfile.mkdtemp())
    copy = work / "plan"
    shutil.copytree(plan_src or REPO / "datasets/sfdmu/qb/en-US/qb-rating-entitlements", copy,
                    ignore=shutil.ignore_patterns(*rs.SFDMU_RUNTIME_DIRS))
    snapshot = lambda: {p.relative_to(copy): p.read_bytes() for p in copy.rglob("*") if p.is_file()}
    before = snapshot()
    t = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
    t.org_config = org_config or _FakeScratch({"username": "scratch@example.com"}, "dev")
    t.options = {"pathtoexportjson": str(copy), **options}
    logs = []
    t.logger = _Log()
    t.logger.info = t.logger.warning = t.logger.error = lambda msg, *_a, **_k: logs.append(str(msg))
    t._load_keychain = lambda: None
    done = _Done()
    done.returncode = exit_code
    done.stdout = done.stderr = sfdmu_output
    saved = (rs.sf_query_records, rs.subprocess.run)
    rs.sf_query_records, rs.subprocess.run = query, lambda *_a, **_k: (runs.append(_a[0] if _a else _k) if runs is not None else None, done)[1]
    error = None
    try:
        t._run_task()
    except Exception as exc:  # the task's own error is what we assert on
        error = exc
    finally:
        rs.sf_query_records, rs.subprocess.run = saved
        after = snapshot()
        shutil.rmtree(work, ignore_errors=True)
    return before, after, error, getattr(t, "_temp_plan_dir", None), logs


SHIPPED = REPO / "datasets/sfdmu/qb/en-US/qb-rating-entitlements"
SHIPPED_KEYS = sorted({(r["ProductUsageResource.Product.StockKeepingUnit"], r["ProductUsageResource.UsageResource.Code"])
                       for name in ("ProductUsageResourcePolicy", "ProductUsageGrant")
                       for r in rs.sfdmu_id_lookups._read_csv(str(SHIPPED / f"{name}.csv"))[1]})


def org_with_every_pur(_org, _soql):
    return [{"Id": f"1TrWt0000007{i:04d}AAA", "Status": "Active", "Product": {"StockKeepingUnit": sku},
             "UsageResource": {"Code": code}} for i, (sku, code) in enumerate(SHIPPED_KEYS)]


before, after, error, temp, logs = run_task({}, org_with_every_pur)
check("success: no error", error, None)
check("success: tracked plan byte-for-byte unchanged", after == before, True)
check("success: temp copy removed", bool(temp) and not os.path.exists(temp), True)
before, after, error, temp, logs = run_task({"ignore_row_errors_for": "{bad"}, org_with_every_pur)
check("bad option: the option error surfaces (not masked by cleanup)", type(error).__name__, "TaskOptionsError")
check("bad option: tracked plan unchanged", after == before, True)
before, after, error, temp, logs = run_task({}, lambda _org, _soql: [])
check("failed lookup: IdLookupError surfaces", type(error).__name__, "IdLookupError")
check("failed lookup: tracked plan unchanged", after == before, True)
check("failed lookup: temp copy removed", bool(temp) and not os.path.exists(temp), True)

# A plan with no lookups loads in place, so cleanup itself must restore the file.
PLAIN = REPO / "datasets/sfdmu/qb/en-US/qb-rating"
plain_export = (PLAIN / "export.json").read_text()
before, after, error, temp, logs = run_task({}, org_with_every_pur, plan_src=PLAIN, exit_code=1)
check("in place, SFDMU fails: the command error surfaces", type(error).__name__, "CommandException")
restored = json.loads(after[pathlib.Path("export.json")])
check("in place, SFDMU fails: credentials cleared from export.json", restored.get("orgs"), [])
check("in place, SFDMU fails: object sets intact",
      restored["objectSets"] == json.loads(plain_export)["objectSets"], True)
check("the access token is never logged", any("00Dxx!TOKEN" in m for m in logs), False)
# A load restores the exact bytes it read: re-dumping dropped a trailing newline and escaped
# non-ASCII text, so the plan showed as modified after every load (todo 319).
NEWLINE_PLAN = REPO / "datasets/sfdmu/q3/en-US/q3-rates"
check("fixture: q3-rates export.json ends with a newline",
      (NEWLINE_PLAN / "export.json").read_bytes().endswith(b"\n"), True)
for code in (0, 1):
    before, after, error, temp, logs = run_task({}, org_with_every_pur, plan_src=NEWLINE_PLAN, exit_code=code)
    check(f"in place (exit {code}): export.json byte-for-byte unchanged",
          after[pathlib.Path("export.json")] == before[pathlib.Path("export.json")], True)
before, after, error, temp, logs = run_task({"object_sets": "[0]"}, org_with_every_pur, plan_src=NEWLINE_PLAN)
check("in place, filtered run: export.json byte-for-byte unchanged",
      after[pathlib.Path("export.json")] == before[pathlib.Path("export.json")], True)
before, after, error, temp, logs = run_task({"object_sets": "[0]"}, org_with_every_pur, plan_src=PLAIN, exit_code=1)
check("in place, filtered run fails: every object set restored",
      json.loads(after[pathlib.Path("export.json")])["objectSets"] == json.loads(plain_export)["objectSets"], True)

# `-o dynamic_assigned_to_user false` arrives as the string "false": it must disable the option
# (the stubbed run returns no JSON, so a User Name query would fail the task).
before, after, error, temp, logs = run_task({"dynamic_assigned_to_user": "false"}, org_with_every_pur,
                                            plan_src=PLAIN)
check('dynamic_assigned_to_user "false": no user query, the run completes', error, None)


# todo 488: every boolean option goes through soql_utils.option_flag. `_as_bool` read a list as
# True, "maybe" as False, and sync_objectset_source_to_source was raw truthiness ("false" was on).
_RUNS = []


def run_task_recording(options, query, **kw):
    """run_task, with each subprocess.run call (the SFDMU load) recorded in _RUNS."""
    del _RUNS[:]
    return run_task(options, query, runs=_RUNS, **kw)


synced = []
_saved_sync = rs.LoadSFDMUData._sync_objectset_source_to_source
rs.LoadSFDMUData._sync_objectset_source_to_source = lambda self: synced.append(True)
try:
    for value, want in (("false", []), ("  ", []), ("", []), (" true ", [True]), ("on", [True])):
        del synced[:]
        before, after, error, temp, logs = run_task_recording(
            {"sync_objectset_source_to_source": value}, org_with_every_pur, plan_src=PLAIN)
        check(f"sync_objectset_source_to_source {value!r}: synced={bool(want)}, and the load ran",
              (error, synced, bool(_RUNS)), (None, want, True))
finally:
    rs.LoadSFDMUData._sync_objectset_source_to_source = _saved_sync
for value, flag in ((" true ", True), ("on", True), ("  ", False), ("false", False), (0, False)):
    before, after, error, temp, logs = run_task_recording({"simulation": value}, org_with_every_pur, plan_src=PLAIN)
    check(f"simulation {value!r}: --simulation={flag}, and the load ran",
          (error, bool(_RUNS), any("--simulation" in str(c) for c in _RUNS)), (None, True, flag))
for name in ("simulation", "sync_objectset_source_to_source", "dynamic_assigned_to_user", "fail_on_row_errors"):
    for value, needle in ((["true"], "must be a single value"), ("maybe", "must be true or false")):
        before, after, error, temp, logs = run_task_recording({name: value}, org_with_every_pur, plan_src=PLAIN)
        check(f"{name} {value!r}: refused by name before the load, plan untouched",
              (type(error).__name__, f"{name} {needle}" in str(error), _RUNS, after == before),
              ("TaskOptionsError", True, [], True))



def prep_runtime_steps(options):
    """LoadSFDMUData._prep_runtime with each side-effecting step stubbed to record; return (error, steps)."""
    steps = []
    t = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
    t.options = {"pathtoexportjson": str(PLAIN), **options}
    t.org_config = _FakeScratch({"username": "scratch@example.com"}, "dev")
    t.logger = _Log()
    for step in ("_load_keychain", "_apply_dynamic_assigned_to_user", "_apply_parent_id_lookups",
                 "_apply_conditional_steps", "_sync_objectset_source_to_source", "_prepare_export_json_file"):
        setattr(t, step, lambda step=step: steps.append(step))
    try:
        t._prep_runtime()
        return None, steps
    except Exception as exc:  # the task's own error is what is asserted
        return exc, steps


# todo 488: the up-front reads in _prep_runtime. Without them, dynamic_assigned_to_user is refused only
# after _load_keychain, sync_objectset_source_to_source after the lookups, and simulation and
# fail_on_row_errors not until the export.json is rewritten or the run is over.
for name in ("dynamic_assigned_to_user", "sync_objectset_source_to_source", "simulation", "fail_on_row_errors"):
    for value in (["true"], "maybe"):
        error, steps = prep_runtime_steps({name: value})
        check(f"_prep_runtime: {name} {value!r} is refused before the keychain, the lookups or the export.json rewrite",
              (type(error).__name__, name in str(error), steps), ("TaskOptionsError", True, []))
error, steps = prep_runtime_steps({"simulation": " true ", "sync_objectset_source_to_source": "on"})
check("_prep_runtime: valid values run every step (the refusals above are not vacuous)",
      (error, steps), (None, ["_load_keychain", "_apply_parent_id_lookups", "_apply_conditional_steps",
                              "_sync_objectset_source_to_source", "_prepare_export_json_file"]))

def row_errors_outcome(fail_on_row_errors):
    """_check_row_errors over one rejected row: 'failed' or 'warned'."""
    work = pathlib.Path(tempfile.mkdtemp())
    (work / "target").mkdir()
    (work / "target" / "Foo_insert_target.csv").write_text("Name,Errors\nr1,boom\n")
    t = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
    t.options = {"pathtoexportjson": str(work), "fail_on_row_errors": fail_on_row_errors}
    t.pathtoexportjson = str(work)
    t._row_error_ignores = {}
    warned = []
    t.logger = type("L", (), {"info": lambda *_a, **_k: None, "warning": lambda _s, m, *_a, **_k: warned.append(m)})()
    try:
        t._check_row_errors({})
        return "warned" if warned else "nothing"
    except rs.CommandException:
        return "failed"
    finally:
        shutil.rmtree(work, ignore_errors=True)


for value, want in ((None, "failed"), ("", "failed"), ("   ", "failed"), (" true ", "failed"),
                    ("false", "warned"), (" off ", "warned"), (0, "warned")):
    check(f"fail_on_row_errors {value!r}: {want} (blank read as false and let rejections through)",
          row_errors_outcome(value), want)


class _FakePersistent(OrgConfig):
    """A persistent org with no username: the token becomes SFDMU's org name."""
    access_token = "00Dyy!PERSISTENT_TOKEN"
    instance_url = "https://example.my.salesforce.com"


before, after, error, temp, logs = run_task({}, org_with_every_pur, plan_src=PLAIN,
                                            org_config=_FakePersistent({}, "tso"))
check("persistent org: the run completes", error, None)
check("persistent org: the token is never logged (command or export.json)",
      [m for m in logs if "PERSISTENT_TOKEN" in m], [])
check("persistent org: the command log is still written, redacted",
      any(m.startswith("Executing command:") and "<redacted>" in m for m in logs), True)
echo = "connected to 00Dyy!PERSISTENT_TOKEN as 00Dzz!OPTION_TOKEN"
for code in (0, 1):
    before, after, error, temp, logs = run_task({"accesstoken": "00Dzz!OPTION_TOKEN"}, org_with_every_pur,
                                                plan_src=PLAIN, org_config=_FakePersistent({}, "tso"),
                                                exit_code=code, sfdmu_output=echo)
    check(f"accesstoken option + SFDMU echo (exit {code}): neither token logged at any level",
          [m for m in logs if "PERSISTENT_TOKEN" in m or "OPTION_TOKEN" in m], [])
before, after, error, temp, logs = run_task({"object_sets": "[7]"}, org_with_every_pur, plan_src=PLAIN)
check("in place, bad object_sets: the option error surfaces", type(error).__name__, "TaskOptionsError")
check("in place, bad object_sets: export.json byte-for-byte unchanged",
      after[pathlib.Path("export.json")] == before[pathlib.Path("export.json")], True)
# The same rule on LoadSFDMUData: a failed restore after a successful load fails the task, and
# after a failed load the load's own error is the one raised (#666 review).
saved_restore = rs._restore_export_json
rs._restore_export_json = lambda *_a, **_k: (_ for _ in ()).throw(IOError("disk full"))
try:
    before, after, error, temp, logs = run_task({}, org_with_every_pur, plan_src=PLAIN)
    check("load succeeds, restore fails: the task fails", type(error).__name__, "OSError")
    before, after, error, temp, logs = run_task({}, org_with_every_pur, plan_src=PLAIN, exit_code=1)
    check("load fails, restore fails: the load's error is kept", type(error).__name__, "CommandException")
    # A lookup plan loads from a temp copy whose export.json holds the token: it is removed even
    # when the restore raises (#666 review).
    before, after, error, temp, logs = run_task({}, org_with_every_pur)
    check("restore fails on a temp copy: the task fails", type(error).__name__, "OSError")
    check("...and the temp copy is still removed", bool(temp) and not os.path.exists(temp), True)
finally:
    rs._restore_export_json = saved_restore

print("ExtractSFDMUData: the token is never logged")
extract_logs = []
ext = rs.ExtractSFDMUData.__new__(rs.ExtractSFDMUData)
ext.org_config = _FakePersistent({}, "tso")
ext.options = {"pathtoexportjson": str(PLAIN), "run_post_process": "false",
               "extractions_base_dir": tempfile.mkdtemp()}
ext.logger = _Log()
ext.logger.info = ext.logger.warning = ext.logger.error = lambda msg, *_a, **_k: extract_logs.append(str(msg))
ext._load_keychain = lambda: None
outcomes = {}
for code in (0, 1, "raise"):
    done = _Done()
    done.returncode, done.stdout, done.stderr = (code if code != "raise" else 0,
                                                 "source org 00Dyy!PERSISTENT_TOKEN", "00Dyy!PERSISTENT_TOKEN")

    def fake_run(*_a, _done=done, _code=code, **_k):
        if _code == "raise":  # an error whose message carries the token reaches the except log
            raise RuntimeError("sf failed for 00Dyy!PERSISTENT_TOKEN")
        return _done
    saved_run = rs.subprocess.run
    rs.subprocess.run = fake_run
    try:
        ext._run_task()
        outcomes[code] = None
    except Exception as exc:
        outcomes[code] = type(exc).__name__
    finally:
        rs.subprocess.run = saved_run
check("extract: exit 0 completes, exit 1 fails, a raised error propagates",
      outcomes, {0: None, 1: "CommandException", "raise": "RuntimeError"})
check("extract: the success path ran end to end",
      any(m.startswith("Extraction complete") for m in extract_logs), True)
check("extract: the token is never logged (command, SFDMU output, error)",
      [m for m in extract_logs if "PERSISTENT_TOKEN" in m], [])
check("extract: the raised error is still logged, redacted",
      any(m.startswith("Extraction error:") and "<redacted>" in m for m in extract_logs), True)
check("extract: the command is still logged, redacted",
      any(m.startswith("Executing extraction:") and "<redacted>" in m for m in extract_logs), True)
shutil.rmtree(ext.options["extractions_base_dir"], ignore_errors=True)


def extract_options(options):
    """ExtractSFDMUData._run_task with `options`; return (error type, SFDMU runs, post-processed?)."""
    runs, logs = [], []
    t = rs.ExtractSFDMUData.__new__(rs.ExtractSFDMUData)
    t.org_config = _FakePersistent({}, "tso")
    t.options = {"pathtoexportjson": str(PLAIN), "extractions_base_dir": tempfile.mkdtemp(), **options}
    t.logger = _Log()
    t.logger.info = t.logger.warning = t.logger.error = lambda msg, *_a, **_k: logs.append(str(msg))
    t._load_keychain = lambda: None
    t._resolve_reference_plan_dir = lambda plan_dir: logs.append("resolve-reference") or None
    saved_run, saved_post = rs.subprocess.run, rs.run_post_process_script
    rs.subprocess.run = lambda *a, **k: runs.append(a) or _Done()
    rs.run_post_process_script = lambda *a, **k: logs.append("post-process")
    try:
        t._run_task()
        err = None
    except Exception as exc:  # noqa: BLE001 - the type is asserted
        err = f"{type(exc).__name__}: {exc}"
    finally:
        rs.subprocess.run, rs.run_post_process_script = saved_run, saved_post
        shutil.rmtree(t.options["extractions_base_dir"], ignore_errors=True)
    return err, runs, "post-process" in logs


# todo 488: run_post_process read "off", "n" and a list as true; copy_to_plan was read after the extract.
for value, post in ((" off ", False), ("n", False), (0, False), ("  ", True), (None, True)):
    err, runs, post_processed = extract_options({"run_post_process": value})
    check(f"extract: run_post_process {value!r} post-processes={post}, and the extract ran",
          (err, bool(runs), post_processed), (None, True, post))
for options, needle in (({"run_post_process": ["false"]}, "run_post_process must be a single value"),
                        ({"run_post_process": "maybe"}, "run_post_process must be true or false"),
                        ({"copy_to_plan": ["true"]}, "copy_to_plan must be a single value"),
                        ({"copy_to_plan": "maybe"}, "copy_to_plan must be true or false")):
    err, runs, _ = extract_options(options)
    check(f"extract: {options!r} refused by name before the extract",
          (bool(err) and "TaskOptionsError" in err and needle in err, runs), (True, []))

print("ExtractSFDMUData: processed output of a lookup plan is re-import-ready")
ENT = REPO / "datasets/sfdmu/qb/en-US/qb-rating-entitlements"
base = pathlib.Path(tempfile.mkdtemp())
ext2 = rs.ExtractSFDMUData.__new__(rs.ExtractSFDMUData)
ext2.org_config = _FakeScratch({"username": "scratch@example.com"}, "dev")
ext2.options = {"pathtoexportjson": str(ENT), "extractions_base_dir": str(base)}
ext2.logger = _Log()
ext2._load_keychain = lambda: None
ext2._build_code_backfill_map = lambda *_a, **_k: {}
calls = []


def fake_extract_run(cmd, *_a, **_k):
    calls.append(cmd)
    if isinstance(cmd, str) and "sfdmu run" in cmd:  # the extract: write what SFDMU would
        work = cmd.split(" -p ", 1)[1].split()[0]
        for name in ("ProductUsageResourcePolicy", "ProductUsageGrant"):
            header, rows = rs.sfdmu_id_lookups._read_csv(str(ENT / f"{name}.csv"))
            keys = [c for c in header if c.startswith("ProductUsageResource.")]
            out = [dict({c: v for c, v in r.items() if c not in keys}, Id=f"X{i:017d}",
                        ProductUsageResourceId=f"1TrWt000000{i:04d}AAA") for i, r in enumerate(rows)]
            rs.sfdmu_id_lookups._write_csv(os.path.join(work, f"{name}.csv"),
                                           ["Id", "ProductUsageResourceId"] + [c for c in header if c not in keys], out)
    return _Done()


def fake_parent_query(_org, soql):
    ids = [i.strip("' ") for i in soql.split("IN (", 1)[1].rstrip(")").split(",")]
    return [{"Id": i, "Product": {"StockKeepingUnit": "QB-DB"}, "UsageResource": {"Code": f"UR-{i[-7:-3]}"}}
            for i in ids]


saved = (rs.subprocess.run, rs.sf_query_records, rs.run_post_process_script)
rs.subprocess.run, rs.sf_query_records = fake_extract_run, fake_parent_query
rs.run_post_process_script = lambda extraction_dir, plan_dir, processed_dir, **_k: None
try:
    ext2._run_task()
    processed = pathlib.Path(ext2.return_values["processed_dir"])
    check("processed dir carries export.json", (processed / "export.json").is_file(), True)
    copied = processed / rs.sfdmu_id_lookups.LOOKUPS_FILENAME
    check("processed dir carries parent_id_lookups.json (so a load resolves the children's Ids)",
          copied.is_file() and copied.read_bytes() == (ENT / rs.sfdmu_id_lookups.LOOKUPS_FILENAME).read_bytes(),
          True)
finally:
    rs.subprocess.run, rs.sf_query_records, rs.run_post_process_script = saved
    shutil.rmtree(base, ignore_errors=True)

print("TestSFDMUIdempotency: a listed insert rejection on both loads")
# qb-pcm's ProrationPolicy insert duplicates the platform default on every load, so it is rejected
# on the first load and again on the second. #636 made every second-load insert rejection fatal,
# which failed test_qb_pcm_idempotency on every org. A listed rejection the same target file already
# had on the first load is not a missed match; a new one, a larger one, one in another pass's file,
# or one whose error text isn't the listed one still fails.
idem_root = pathlib.Path(tempfile.mkdtemp())
idem_dir = idem_root / "plan"
idem_dir.mkdir()
(idem_dir / "export.json").write_text(json.dumps({"objects": []}))
LISTED = "duplicate value found: Name duplicates value on record with id: x"


def fake_load(rejections, stamp):
    """Write `<path>: (count, error)` target files with an explicit mtime, so the second load's
    files always differ from the first load's baseline, whatever the filesystem's resolution."""
    def run(*_a, **_k):
        for rel, (n, error) in rejections.items():
            path = idem_dir / "target" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Name,Errors\n" + "".join(f"r{i},{error}\n" for i in range(n)))
            os.utime(path, (stamp, stamp))
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    return run


def idem_task():
    t = rs.TestSFDMUIdempotency.__new__(rs.TestSFDMUIdempotency)
    t.options = {}
    t.org_config = scratch
    t.accesstoken, t.instanceurl = "00Dxx!TOKEN", "https://x.my.salesforce.com"
    t.logger = type("L", (), {"info": lambda *_a, **_k: None, "warning": lambda *_a, **_k: None,
                              "error": lambda *_a, **_k: None})()
    t._row_error_ignores = rs._parse_row_error_ignores(
        {"ProrationPolicy": "duplicate value found", "Widget": "duplicate value found"})
    return t


def two_loads(first, second):
    """'passed', or which load failed and on which objects."""
    task = idem_task()
    saved_run = rs.subprocess.run
    shutil.rmtree(idem_dir / "target", ignore_errors=True)
    try:
        for load, (rejections, strict) in enumerate(((first, False), (second, True)), 1):
            rs.subprocess.run = fake_load(rejections, 1_000_000 + 100 * load)
            try:
                task._run_load_in(str(idem_dir), strict=strict)
            except rs.CommandException as exc:
                return f"load {load} failed: " + ", ".join(
                    o for o in ("ProrationPolicy", "Widget") if o in str(exc))
        return "passed"
    finally:
        rs.subprocess.run = saved_run


PP, PP2 = "ProrationPolicy_insert_target.csv", "object-set-2/ProrationPolicy_insert_target.csv"
check("listed, rejected on both loads: passes",
      two_loads({PP: (1, LISTED)}, {PP: (1, LISTED)}), "passed")
check("listed, but only rejected on the second load: fails (a missed match)",
      two_loads({}, {PP: (1, LISTED)}), "load 2 failed: ProrationPolicy")
check("listed, more rejections on the second load than the first: fails",
      two_loads({PP: (1, LISTED)}, {PP: (2, LISTED)}), "load 2 failed: ProrationPolicy")
check("listed, but the second load's error text isn't the listed one: fails",
      two_loads({"Widget_insert_target.csv": (1, LISTED)},
                {"Widget_insert_target.csv": (1, "The child product exists in the group")}),
      "load 2 failed: Widget")
check("two passes: the first load's pass-2 rejections don't excuse new ones in pass 1",
      two_loads({PP2: (5, LISTED)}, {PP: (3, LISTED), PP2: (5, LISTED)}), "load 2 failed: ProrationPolicy")
check("two passes: each pass's own repeated rejections pass",
      two_loads({PP: (5, LISTED), PP2: (1, LISTED)}, {PP: (5, LISTED), PP2: (1, LISTED)}), "passed")
idem_bytes = '{\n  "objects": [],\n  "note": "café"\n}\n'.encode()
(idem_dir / "export.json").write_bytes(idem_bytes)
two_loads({}, {})
check("idempotency load: export.json byte-for-byte unchanged (newline, non-ASCII)",
      (idem_dir / "export.json").read_bytes() == idem_bytes, True)


def restore_fails(*_a, **_k):
    raise IOError("disk full")


# A restore that fails after a successful load must fail the task, since export.json may still
# hold the access token; after a failed load the load's own error is kept (#666 review).
saved_restore = rs._restore_export_json
rs._restore_export_json = restore_fails
try:
    task, saved_run = idem_task(), rs.subprocess.run
    rs.subprocess.run = fake_load({}, 1_000_500)
    try:
        task._run_load_in(str(idem_dir), strict=False)
        outcome = "returned"
    except IOError:
        outcome = "IOError"
    finally:
        rs.subprocess.run = saved_run
    check("idempotency load succeeds, restore fails: the task fails", outcome, "IOError")
    task = idem_task()
    rs.subprocess.run = lambda *_a, **_k: type("R", (), {"returncode": 1, "stdout": "", "stderr": ""})()
    try:
        task._run_load_in(str(idem_dir), strict=False)
        outcome = "returned"
    except rs.CommandException:
        outcome = "CommandException"
    except IOError:
        outcome = "IOError"
    finally:
        rs.subprocess.run = saved_run
    check("idempotency load fails, restore fails: the load's error is kept", outcome, "CommandException")
finally:
    rs._restore_export_json = saved_restore
shutil.rmtree(idem_root, ignore_errors=True)

print("TestSFDMUIdempotency: dynamic_assigned_to_user resolves the placeholder on both loads")
# qb-dro's load sets dynamic_assigned_to_user; the test ran without it, so both loads sent the raw
# placeholder and the platform rejected FulfillmentStepDefinition rows for a blank AssignedToId
# (todo 329). With the option, each load runs from a temp copy carrying the org user's Name.
dro_root = pathlib.Path(tempfile.mkdtemp())
DRO = dro_root / "qb-dro"
shutil.copytree(REPO / "datasets/sfdmu/qb/en-US/qb-dro", DRO, ignore=shutil.ignore_patterns(*rs.SFDMU_RUNTIME_DIRS))
dro_before = {p.relative_to(DRO): p.read_bytes() for p in DRO.rglob("*") if p.is_file()}
seen, user_queries = [], []
has_credential = [True]


def dro_run(cmd, *_a, **_k):
    if isinstance(cmd, list):  # an `sf data query`: the conditional-step probe or the User Name
        soql = cmd[cmd.index("-q") + 1]
        if "FROM NamedCredential" in soql:  # with the RLM credential the plan keeps its step
            records = [{"DeveloperName": "RLM"}] if has_credential[0] else []
        elif "FROM FulfillmentStepDefinition" in soql:  # the stale-step probe: a fresh org
            records = []
        elif "FROM User" in soql:
            user_queries.append(cmd)
            records = [{"Name": "Admin User"}]
        else:
            raise AssertionError(soql)
        return type("R", (), {"returncode": 0, "stderr": "",
                              "stdout": json.dumps({"status": 0, "result": {"records": records}})})()
    plan = pathlib.Path(cmd.split(" -p ", 1)[1].split(" ", 1)[0])
    seen.append((plan, (plan / "FulfillmentStepDefinition.csv").read_text(encoding="utf-8")))
    return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()


for option, want_name, credential in ((True, True, True), ("false", False, True), (True, True, False)):
    seen.clear(), user_queries.clear()
    has_credential[0] = credential
    task = idem_task()
    task.options = {"dynamic_assigned_to_user": option}
    task.targetusername = "scratch@example.com"
    saved_run = rs.subprocess.run
    rs.subprocess.run = dro_run
    try:
        task._run_load_once(str(DRO), strict=False)
        task._run_load_once(str(DRO), strict=True)
    finally:
        rs.subprocess.run = saved_run
    tag = f"dynamic_assigned_to_user={option!r}, credential={credential}"
    check(f"{tag}: both loads ran", len(seen), 2)
    check(f"{tag}: both loads carry the tenant step only with the credential",
          ["Stage New Tenant" in csv for _, csv in seen], [credential] * 2)
    if want_name:
        check(f"{tag}: both loads send the org user's Name",
              [("Admin User" in csv, rs.DRO_ASSIGNED_TO_PLACEHOLDER in csv) for _, csv in seen],
              [(True, False)] * 2)
        check(f"{tag}: both loads ran from a temp copy, now removed",
              [(plan != DRO, plan.exists()) for plan, _ in seen], [(True, False)] * 2)
        check(f"{tag}: the user Name is queried once, by username",
              [c[c.index("-o") + 1] for c in user_queries], ["scratch@example.com"])
    else:
        # qb-dro carries conditional_steps.json, so even without the user Name each load runs from a
        # temp copy (the step is probed there); the placeholder is still sent raw.
        check(f"{tag}: the placeholder is unchanged (a temp copy, for the conditional step)",
              [(plan != DRO, rs.DRO_ASSIGNED_TO_PLACEHOLDER in csv) for plan, csv in seen], [(True, True)] * 2)
        check(f"{tag}: no user query", user_queries, [])
    shutil.rmtree(DRO / "target", ignore_errors=True)  # in case a run wrote output beside the plan
dro_after = {p.relative_to(DRO): p.read_bytes() for p in DRO.rglob("*") if p.is_file()}
check("qb-dro plan byte-for-byte unchanged", dro_after == dro_before, True)
shutil.rmtree(dro_root, ignore_errors=True)

# todo 488: the roundtrip options were read after the first load, and `in {"1", "true", "yes"}`
# read " true " and "on" as false.
def idem_options(options):
    """TestSFDMUIdempotency._run_task up to its first load; return (error, loads, roundtrip read)."""
    loads = []
    t = rs.TestSFDMUIdempotency.__new__(rs.TestSFDMUIdempotency)
    t.options = {"pathtoexportjson": str(PLAIN), **options}
    t.org_config = _FakeScratch({"username": "scratch@example.com"}, "dev")
    t.logger = type("L", (), {"info": lambda *_a, **_k: None, "warning": lambda *_a, **_k: None,
                              "error": lambda *_a, **_k: None})()
    t._load_keychain = lambda: None

    def first_load(*_a, **_k):
        loads.append("load")
        raise RuntimeError("stop after the first load")
    t._run_load_once = first_load
    try:
        t._run_task()
        return "no error", loads
    except RuntimeError as exc:
        return ("stopped" if "stop after" in str(exc) else str(exc)), loads
    except Exception as exc:  # noqa: BLE001 - the text is asserted
        return f"{type(exc).__name__}: {exc}", loads


for value in (" true ", "on", True, "", None, "false"):
    check(f"idempotency: use_extraction_roundtrip {value!r} is accepted and the first load runs",
          idem_options({"use_extraction_roundtrip": value, "persist_extraction_output": value}), ("stopped", ["load"]))
for options, needle in (({"use_extraction_roundtrip": ["true"]}, "use_extraction_roundtrip must be a single value"),
                        ({"persist_extraction_output": "maybe"}, "persist_extraction_output must be true or false"),
                        ({"dynamic_assigned_to_user": ["true"]}, "dynamic_assigned_to_user must be a single value")):
    err, loads = idem_options(options)
    check(f"idempotency: {options!r} refused by name before the first load",
          ("TaskOptionsError" in err and needle in err, loads), (True, []))

print("clear_credentials_under: the idempotency roundtrip's kept dir")
# Persist mode keeps the roundtrip dir, and the second load ran from processed/export.json; a failed
# restore there could leave the token behind, so every export.json under the dir is cleared (#666).
keep = pathlib.Path(tempfile.mkdtemp())
(keep / "processed").mkdir()
for p in (keep / "export.json", keep / "processed" / "export.json"):
    p.write_text(json.dumps({"orgs": [{"accessToken": "00Dxx!TOKEN"}], "objects": []}))
untouched = b'{\n  "objects": [],\n  "note": "caf\xc3\xa9"\n}\n'
(keep / "processed" / "clean").mkdir()
(keep / "processed" / "clean" / "export.json").write_bytes(untouched)
(keep / "processed" / "bad").mkdir()
(keep / "processed" / "bad" / "export.json").write_text("{not json")
warnings = []
rs.clear_credentials_under(str(keep), warnings.append)
check("every export.json under the dir is cleared",
      [json.loads(p.read_text())["orgs"] for p in (keep / "export.json", keep / "processed" / "export.json")], [[], []])
check("an unreadable one is reported, not raised", len(warnings), 1)
check("one with no credentials is left byte-for-byte unchanged",
      (keep / "processed" / "clean" / "export.json").read_bytes() == untouched, True)
shutil.rmtree(keep, ignore_errors=True)

print("DeleteSFDMUData: named sobjects on an Upsert plan")
# qb-pricing has no Insert objects since todo 298, so its teardown names them. Each must be a type
# the plan inserts or upserts; a typo, a Readonly/Update type or an empty list fails instead of
# deleting nothing, the wrong types, or every record of a type the plan only reads.
PRICING = REPO / "datasets/sfdmu/qb/en-US/qb-pricing"


def run_delete(options):
    task = rs.DeleteSFDMUData.__new__(rs.DeleteSFDMUData)
    task.options = {"pathtoexportjson": str(PRICING), **options}
    task.logger = type("L", (), {"info": lambda *_a, **_k: None, "warning": lambda *_a, **_k: None})()
    deleted = []
    task._delete_all_records = lambda name: deleted.append(name) or 0
    task._run_task()
    return deleted


check("no option: an all-Upsert plan deletes nothing", run_delete({}), [])
check("named: deleted children first, in reverse plan order",
      run_delete({"sobjects": ["PricebookEntry", "PriceAdjustmentTier", "CostBookEntry"]}),
      ["CostBookEntry", "PricebookEntry", "PriceAdjustmentTier"])
check("named as a comma string (cci -o): same order",
      run_delete({"sobjects": "PricebookEntry, CostBookEntry"}), ["CostBookEntry", "PricebookEntry"])
try:
    got = run_delete({"sobjects": ["PricebookEntry", "Pricebookentry"]})
except TaskOptionsError as exc:
    got = "TaskOptionsError" if "Pricebookentry" in str(exc) else str(exc)
check("named: an undeclared type fails before anything is deleted", got, "TaskOptionsError")
for label, option in (("a Readonly type (Product2) is refused, never deleted org-wide", ["Product2"]),
                      ("an Update-only type (ProrationPolicy) is refused", ["ProrationPolicy"]),
                      ("an empty list fails instead of falling back to Insert mode", []),
                      ("an empty string fails instead of falling back to Insert mode", " , ")):
    try:
        got = run_delete({"sobjects": option})
    except TaskOptionsError:
        got = "TaskOptionsError"
    check(f"named: {label}", got, "TaskOptionsError")
# todo 488: a value that is not a string or a list of strings is refused by name, before any delete,
# instead of a raw TypeError (int) or the object name "None" (a YAML `- ~` item).
for label, option in (("int 0", 0), ("a null list item", ["PricebookEntry", None]),
                      ("a nested list item", [["PricebookEntry"]]), ("a dict", {"PricebookEntry": 1})):
    _deleted = []
    _task = rs.DeleteSFDMUData.__new__(rs.DeleteSFDMUData)
    _task.options = {"pathtoexportjson": str(PRICING), "sobjects": option}
    _task.logger = type("L", (), {"info": lambda *_a, **_k: None, "warning": lambda *_a, **_k: None})()
    _task._delete_all_records = lambda name: _deleted.append(name) or 0
    try:
        _task._run_task()
        got = "no error"
    except TaskOptionsError as exc:
        got = "refused naming sobjects" if "sobjects must be" in str(exc) else str(exc)
    except Exception as exc:  # noqa: BLE001 - a raw error is the defect under test
        got = f"{type(exc).__name__}: {exc}"
    check(f"named: {label} is refused naming the option, nothing deleted", (got, _deleted), ("refused naming sobjects", []))
_got = run_delete({"sobjects": ["PricebookEntry"]})
check("named: the valid control does reach the delete (the refusals above are not vacuous)", _got, ["PricebookEntry"])

print("LoadSFDMUData: conditional DRO steps are dropped in a temp copy (todo 419)")
src_plan = REPO / "datasets/sfdmu/qb/en-US/qb-dro"
tracked = {p.relative_to(src_plan): p.read_bytes() for p in src_plan.rglob("*")
           if p.is_file() and not set(p.relative_to(src_plan).parts) & set(rs.SFDMU_RUNTIME_DIRS)}
cond_queries = []


def no_credential(org, soql):
    cond_queries.append((org, soql))
    return []


cond = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
cond.org_config = scratch
cond.options = {}
cond.logger = type("L", (), {"info": lambda *_a, **_k: None})()
cond.pathtoexportjson = str(src_plan)
cond._temp_plan_dir = None
saved_query = rs.sf_query_records
rs.sf_query_records = no_credential
try:
    cond._apply_conditional_steps()
finally:
    rs.sf_query_records = saved_query
cond_temp = pathlib.Path(cond.pathtoexportjson)
try:
    check("the run points at a temp copy", cond_temp != src_plan and cond_temp == pathlib.Path(cond._temp_plan_dir), True)
    check("the CLI query used the scratch username, never the token",
          {org for org, _ in cond_queries}, {"scratch@example.com"})
    check("the step is gone from the temp definitions",
          "Stage New Tenant" in (cond_temp / "FulfillmentStepDefinition.csv").read_text(), False)
    check("the tracked plan is byte-for-byte unchanged",
          {p.relative_to(src_plan): p.read_bytes() for p in src_plan.rglob("*")
           if p.is_file() and not set(p.relative_to(src_plan).parts) & set(rs.SFDMU_RUNTIME_DIRS)}, tracked)
finally:
    if cond_temp != src_plan:
        shutil.rmtree(cond_temp, ignore_errors=True)
plain = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
plain.org_config = scratch
plain.options = {}
plain.logger = cond.logger
plain.pathtoexportjson = str(REPO / "datasets/sfdmu/qb/en-US/qb-pricing")
plain._temp_plan_dir = None
plain._apply_conditional_steps()
check("a plan without conditional_steps.json is left alone",
      plain.pathtoexportjson, str(REPO / "datasets/sfdmu/qb/en-US/qb-pricing"))

print("LoadSFDMUData: insert_qb_dro_data's options run the user Name and the condition together")
# The load task as insert_qb_dro_data runs it (dynamic_assigned_to_user on): both temp-copy steps
# share one copy, so the loaded CSV carries the user Name and, without the credential, no tenant step.
for credential in (True, False):
    seen.clear(), user_queries.clear()
    has_credential[0] = credential
    work = pathlib.Path(tempfile.mkdtemp())
    shutil.copytree(REPO / "datasets/sfdmu/qb/en-US/qb-dro", work / "qb-dro",
                    ignore=shutil.ignore_patterns(*rs.SFDMU_RUNTIME_DIRS))
    load = rs.LoadSFDMUData.__new__(rs.LoadSFDMUData)
    load.org_config = _FakeScratch({"username": "scratch@example.com"}, "dev")
    load.options = {"pathtoexportjson": str(work / "qb-dro"), "dynamic_assigned_to_user": True}
    load.logger = _Log()
    load._load_keychain = lambda: None
    saved_run = rs.subprocess.run
    rs.subprocess.run = dro_run
    try:
        load._run_task()
        error = None
    except Exception as exc:  # asserted below
        error = exc
    finally:
        rs.subprocess.run = saved_run
        shutil.rmtree(work, ignore_errors=True)
    tag = f"credential={credential}"
    check(f"{tag}: the load completes", error, None)
    check(f"{tag}: SFDMU ran once, from a temp copy", [plan != work / "qb-dro" for plan, _ in seen], [True])
    check(f"{tag}: the loaded definitions carry the user Name, and the tenant step only with the credential",
          [("Admin User" in csv, rs.DRO_ASSIGNED_TO_PLACEHOLDER in csv, "Stage New Tenant" in csv)
           for _, csv in seen], [(True, False, credential)])

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")

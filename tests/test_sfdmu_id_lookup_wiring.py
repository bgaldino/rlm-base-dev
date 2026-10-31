#!/usr/bin/env python3
"""Task wiring for parent Id lookups in `tasks/rlm_sfdmu.py` (todo 298), offline.

`tests/test_sfdmu_id_lookups.py` covers the lookup module. This one covers what the module
can't: which org the `sf` CLI is pointed at (never the access token); that Ids resolve in a temp
copy without the SFDMU runtime dirs; that a whole `_run_task` (SFDMU stubbed) of a lookups plan
leaves the tracked plan byte-for-byte unchanged on success, a bad option and a failed lookup; and
that a plan loaded in place has its credentials cleared after a failed run, is untouched by an
early failure, and never has the access token logged.

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


def run_task(options, query, plan_src=None, exit_code=0, org_config=None, sfdmu_output=""):
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
    rs.sf_query_records, rs.subprocess.run = query, lambda *_a, **_k: done
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
before, after, error, temp, logs = run_task({"object_sets": "[0]"}, org_with_every_pur, plan_src=PLAIN, exit_code=1)
check("in place, filtered run fails: every object set restored",
      json.loads(after[pathlib.Path("export.json")])["objectSets"] == json.loads(plain_export)["objectSets"], True)


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

print("ExtractSFDMUData: the token is never logged")
extract_logs = []
ext = rs.ExtractSFDMUData.__new__(rs.ExtractSFDMUData)
ext.org_config = _FakePersistent({}, "tso")
ext.options = {"pathtoexportjson": str(PLAIN), "run_post_process": "false",
               "extractions_base_dir": tempfile.mkdtemp()}
ext.logger = _Log()
ext.logger.info = ext.logger.warning = ext.logger.error = lambda msg, *_a, **_k: extract_logs.append(str(msg))
ext._load_keychain = lambda: None
for code in (0, 1):
    done = _Done()
    done.returncode, done.stdout, done.stderr = code, "source org 00Dyy!PERSISTENT_TOKEN", "00Dyy!PERSISTENT_TOKEN"
    saved_run = rs.subprocess.run
    rs.subprocess.run = lambda *_a, **_k: done
    try:
        ext._run_task()
    except Exception:
        pass  # exit 1 raises by design; the logs are what is checked
    finally:
        rs.subprocess.run = saved_run
check("extract: the token is never logged (command, SFDMU output, error)",
      [m for m in extract_logs if "PERSISTENT_TOKEN" in m], [])
check("extract: the command is still logged, redacted",
      any(m.startswith("Executing extraction:") and "<redacted>" in m for m in extract_logs), True)
shutil.rmtree(ext.options["extractions_base_dir"], ignore_errors=True)

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")

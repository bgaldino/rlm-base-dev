#!/usr/bin/env python3
"""Task wiring for parent Id lookups in `tasks/rlm_sfdmu.py` (todo 298), offline.

`tests/test_sfdmu_id_lookups.py` covers the lookup module. This one covers the two things the
module can't: which org the `sf` CLI is pointed at (never the access token), and that a load
resolves Ids in a temp copy without the SFDMU runtime dirs, leaving the tracked plan untouched.

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

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")

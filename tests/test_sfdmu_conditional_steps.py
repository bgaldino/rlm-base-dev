#!/usr/bin/env python3
"""Offline tests for `scripts/sfdmu_conditional_steps.py` (todo 419, item 3).

Runs the real qb-dro plan through `apply_conditions` with a fake `query`: the tenant callout
step and its two dependency rows go when the `RLM` Named Credential is missing, the rest of the
plan (the billing chain, `Start Project`) is untouched, and a plan that has the credential is left
byte-for-byte as tracked. A stale step on the org is reported. A plan that already lacks the step
(a round-trip extract) loads when the credential is missing, but fails when the credential exists,
so a renamed step cannot turn the guard into a no-op.

Run: `python tests/test_sfdmu_conditional_steps.py` (offline, no org).
"""
from __future__ import annotations

import csv
import json
import pathlib
import shutil
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import sfdmu_conditional_steps as cs  # noqa: E402

STEP = "Stage New Tenant for Provisioning - Platform"
PLAN = REPO / "datasets/sfdmu/qb/en-US/qb-dro"
_failures: list[str] = []


def check(label: str, got, want) -> None:
    if got == want:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}\n       got:  {got!r}\n       want: {want!r}")
        _failures.append(label)


def fresh_plan() -> pathlib.Path:
    dest = pathlib.Path(tempfile.mkdtemp()) / "plan"
    shutil.copytree(PLAN, dest, ignore=shutil.ignore_patterns("source", "target", "reports"))
    return dest


def rows(plan: pathlib.Path, name: str) -> list[dict]:
    with open(plan / name, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def tree(plan: pathlib.Path) -> dict:
    return {p.relative_to(plan).as_posix(): p.read_bytes() for p in plan.rglob("*") if p.is_file()}


def pairs_of(plan: pathlib.Path) -> set:
    return {(r["DependsOnStepDefinition.Name"], r["FulfillmentStepDefinition.Name"])
            for r in rows(plan, cs.DEPENDENCY_CSV)}


def fake_query(credential: bool, stale: bool = False):
    def query(soql: str):
        if "FROM NamedCredential" in soql:
            assert "NamespacePrefix = null" in soql, soql
            return [{"DeveloperName": "RLM"}] if credential else []
        if "FROM FulfillmentStepDefinition" in soql:
            return [{"Id": "x"}] if stale else []
        raise AssertionError(soql)
    return query


print("the tracked plan declares the callout step as conditional")
check("one step, requiring the RLM Named Credential", cs.load_conditions(str(PLAN)),
      [{"name": STEP, "requires": {"namedCredential": "RLM"}}])
check("the step is in the tracked definitions",
      STEP in {r["Name"] for r in rows(PLAN, cs.DEFINITION_CSV)}, True)

print("every tracked conditions file names steps its plan has")
# The load's rename guard fires only on an org that meets the requirement, which no default build
# does; this offline check covers a renamed step on every build.
tracked = sorted((REPO / "datasets").rglob(cs.CONDITIONS_FILENAME))
check("at least the qb-dro conditions file is found", PLAN / cs.CONDITIONS_FILENAME in tracked, True)
for spec in tracked:
    names = {r[cs.DEFINITION_NAME_COLUMN] for r in rows(spec.parent, cs.DEFINITION_CSV)}
    check(f"{spec.relative_to(REPO)}: every named step is in {cs.DEFINITION_CSV}",
          [i["name"] for i in cs.load_conditions(str(spec.parent)) if i["name"] not in names], [])

print("no RLM credential: the step and its dependencies go, the rest stays")
plan = fresh_plan()
before_defs = {r["Name"] for r in rows(plan, cs.DEFINITION_CSV)}
before_deps = rows(plan, cs.DEPENDENCY_CSV)
logs: list[str] = []
removed = cs.apply_conditions(str(plan), fake_query(False), logs.append)
after_defs = {r["Name"] for r in rows(plan, cs.DEFINITION_CSV)}
after_deps = rows(plan, cs.DEPENDENCY_CSV)
names_step = lambda r: STEP in (r["DependsOnStepDefinition.Name"], r["FulfillmentStepDefinition.Name"])  # noqa: E731
check("the step is reported removed", removed, [STEP])
check("only that definition is gone", before_defs - after_defs, {STEP})
check("exactly the two rows that name it are gone",
      sorted(r["Name"] for r in before_deps if names_step(r)),
      ["Provision Tenant to Provision Features", "Tenant to Receive Key"])
check("no remaining row names the step", [r for r in after_deps if names_step(r)], [])
check("the other dependency rows are untouched", len(after_deps), len(before_deps) - 2)
check("the billing chain is intact",
      {("Provision Licensing/Features", "Initiate Billing"), ("Start Project", "Initiate Billing"),
       ("Initiate Billing", "Post Invoice"), ("Post Invoice", "Receive Payment")} <= pairs_of(plan), True)
check("Receive Key and Provision Licensing are now roots",
      sorted({"Receive Key + Assign to Asset", "Provision Licensing/Features"}
             - {r["FulfillmentStepDefinition.Name"] for r in after_deps}),
      ["Provision Licensing/Features", "Receive Key + Assign to Asset"])
check("the log names the re-rooted steps",
      any("now without a predecessor: Provision Licensing/Features, Receive Key + Assign to Asset" in line
          for line in logs), True)
check("no stale warning when the org lacks the step", any("WARNING" in line for line in logs), False)
key = lambda r: tuple(sorted(r.items()))  # noqa: E731
check("every kept dependency row keeps all its columns",
      sorted(map(key, after_deps)), sorted(key(r) for r in before_deps if not names_step(r)))
check("every kept definition row keeps all its columns",
      sorted(map(key, rows(plan, cs.DEFINITION_CSV))),
      sorted(key(r) for r in rows(PLAN, cs.DEFINITION_CSV) if r["Name"] != STEP))

print("a plan that already lacks the step (round-trip extract)")
plan = fresh_plan()
cs.apply_conditions(str(plan), fake_query(False), [].append)
logs = []
check("no credential: nothing more to drop", cs.apply_conditions(str(plan), fake_query(False), logs.append), [])
check("the log says it was already absent", any("already absent" in line for line in logs), True)
try:
    cs.apply_conditions(str(plan), fake_query(True))
    got = "returned"
except cs.ConditionalStepError:
    got = "ConditionalStepError"
check("credential exists: the missing step fails (rename guard)", got, "ConditionalStepError")

print("the RLM credential exists: the plan is byte-for-byte unchanged")
plan = fresh_plan()
snapshot = tree(plan)
logs = []
removed = cs.apply_conditions(str(plan), fake_query(True), logs.append)
check("nothing removed", removed, [])
check("every file identical", tree(plan), snapshot)
check("the log says the step was kept", any("kept" in line for line in logs), True)

print("an org that already holds the step")
plan = fresh_plan()
logs = []
cs.apply_conditions(str(plan), fake_query(False, stale=True), logs.append)
check("the load warns it will still run", any("WARNING" in line and "still run" in line for line in logs), True)

print("a step with another predecessor keeps that dependency")
plan = fresh_plan()
(plan / "conditional_steps.json").write_text(json.dumps({"steps": [
    {"name": "Provision Licensing/Features", "requires": {"namedCredential": "ABSENT"}}]}))
logs = []
cs.apply_conditions(str(plan), fake_query(False), logs.append)
check("Initiate Billing is still gated by Start Project",
      ("Start Project", "Initiate Billing") in pairs_of(plan), True)
check("the log reports it as still gated",
      any("still gated by other steps: Initiate Billing" in line for line in logs), True)

print("bad input fails loudly")
for label, body, credential in (
        ("a step the plan does not have, on an org that can run it",
         {"steps": [{"name": "No Such Step", "requires": {"namedCredential": "RLM"}}]}, True),
        ("an unsupported requirement", {"steps": [{"name": STEP, "requires": {"remoteSite": "x"}}]}, False),
        ("a quote in the credential name",
         {"steps": [{"name": STEP, "requires": {"namedCredential": "R'LM"}}]}, False),
        ("an empty list", {"steps": []}, False),
        ("malformed JSON", "{not json", False),
        ("a per-pass copy of the definitions", None, False)):
    plan = fresh_plan()
    if body is None:
        (plan / "objectset_source" / "object-set-2").mkdir(parents=True, exist_ok=True)
        shutil.copy(plan / cs.DEFINITION_CSV, plan / "objectset_source" / "object-set-2" / cs.DEFINITION_CSV)
    else:
        (plan / "conditional_steps.json").write_text(body if isinstance(body, str) else json.dumps(body))
    try:
        cs.apply_conditions(str(plan), fake_query(credential))
        got = "returned"
    except cs.ConditionalStepError:
        got = "ConditionalStepError"
    check(f"{label} raises", got, "ConditionalStepError")
plan = fresh_plan()
(plan / "conditional_steps.json").unlink()
check("a plan with no conditions file is a no-op", cs.apply_conditions(str(plan), fake_query(False)), [])

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")

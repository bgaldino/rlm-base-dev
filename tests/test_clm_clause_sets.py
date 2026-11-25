#!/usr/bin/env python3
"""Offline checks for tasks/rlm_clm_clause_sets.py (todo 346).

    python tests/test_clm_clause_sets.py

No org and no CumulusCI install needed: the pure helpers are tested; the org is not.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("_clm_clause_sets", REPO / "tasks" / "rlm_clm_clause_sets.py")
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

failures = []


def check(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")


check("category value is the 15 character Id", mod.category_value("0zMWt0000001L5dMAE"), "0zMWt0000001L5d")

cats = {"Contract": "0zMWt0000001L5dMAE", "Retail": "0zMWt0000001L5eMAE"}
rows = [("A", "Contract", "en_US"), ("B", "Retail", "en_US")]
check("missing rows carry the portable Category",
      mod.missing_rows(rows, cats, set()),
      [{"Name": "A", "DefaultLanguage": "en_US", "Category": "0zMWt0000001L5d"},
       {"Name": "B", "DefaultLanguage": "en_US", "Category": "0zMWt0000001L5e"}])
check("an existing row is skipped", [r["Name"] for r in mod.missing_rows(rows, cats, {("A", "0zMWt0000001L5d")})], ["B"])
check("the same name under another category is not skipped",
      [r["Name"] for r in mod.missing_rows(rows, cats, {("A", "0zMWt0000001L5e")})], ["A", "B"])
try:
    mod.missing_rows([("A", "Nope", "en_US")], cats, set())
    failures.append("an unknown category must raise")
except Exception as exc:
    check("unknown category names the row", "'A'" in str(exc) and "'Nope'" in str(exc), True)

plan = mod.plan_rows(str(REPO / mod.DEFAULT_CSV))
check("the plan CSV has 20 rows", len(plan), 20)
check("every plan category is loaded by the plan",
      {c for _, c, _ in plan} <= {"Contract", "Retail"}, True)
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "x.csv"
    p.write_text("Name,DefaultLanguage\nA,en_US\n")
    try:
        mod.plan_rows(str(p))
        failures.append("a CSV without the category column must raise")
    except Exception:
        pass

check("18 character Category values count as existing",
      mod.missing_rows(rows, cats, {("A", "0zMWt0000001L5dMAE"), ("B", "0zMWt0000001L5eMAE")}), [])
check("rows with a Status other than Draft are counted",
      mod.ignored_status_count([("a", "c", "en_US", "Active"), ("b", "c", "en_US", "Draft"),
                                ("c", "c", "en_US", "")]), 1)
check("the plan CSV has 16 Active rows the platform ignores",
      mod.ignored_status_count(mod.plan_rows_with_status(str(REPO / mod.DEFAULT_CSV))), 16)


class FakeSf:
    """An org whose Category comes back as 18 characters, as an Id field would."""

    def __init__(self):
        self.sets = []
        self.DocumentClauseSet = self

    def query_all(self, soql):
        if "FROM ClauseCatgConfiguration" in soql:
            return {"records": [{"Id": "0zMWt0000001L5dMAE", "DeveloperName": "Contract"},
                                {"Id": "0zMWt0000001L5eMAE", "DeveloperName": "Retail"}]}
        return {"records": [{"Name": s["Name"], "Category": s["Category"] + "MAE"} for s in self.sets]}

    def create(self, fields):
        self.sets.append(dict(fields))


class FakeLog:
    def __init__(self):
        self.warnings = []

    def info(self, *_):
        pass

    def warning(self, message):
        self.warnings.append(message)


class FakeProject:
    repo_root = str(REPO)


task = mod.LoadClmClauseSets.__new__(mod.LoadClmClauseSets)
task.sf, task.logger, task.options, task.project_config = FakeSf(), FakeLog(), {}, FakeProject()
task._run_task()
check("first run inserts every row", len(task.sf.sets), 20)
check("first run warns about the ignored Status", len(task.logger.warnings), 1)
check("the warning names the count", "16 of 20" in task.logger.warnings[0], True)
task._run_task()
check("second run inserts nothing", len(task.sf.sets), 20)

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("OK")
